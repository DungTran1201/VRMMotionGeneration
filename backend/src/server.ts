import http from 'node:http';
import crypto from 'node:crypto';
import type { DatabaseSync } from 'node:sqlite';
import { AuthService } from './auth-service.js';
import { globalRateLimiter } from './rate-limiter.js';
import type { UserProfile } from '@vrm/platform-contracts';

const MAX_BODY_SIZE = 100 * 1024; // 100 KiB

export interface ServerOptions {
  db: DatabaseSync;
  corsOrigins?: string[];
}

export function createServer(options: ServerOptions): http.Server {
  const authService = new AuthService(options.db);
  const allowedOrigins = options.corsOrigins || [
    'http://localhost:5173',
    'http://localhost:4173',
    'http://127.0.0.1:5173',
    'https://vrm.app',
    'https://app.vrm.app'
  ];

  const server = http.createServer(async (req, res) => {
    const correlationId = (req.headers['x-correlation-id'] as string) || crypto.randomUUID();
    const timestamp = new Date().toISOString();

    // Security Headers
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    res.setHeader('X-Correlation-Id', correlationId);

    // CORS Handling
    const origin = req.headers['origin'];
    if (origin && (allowedOrigins.includes(origin) || process.env.NODE_ENV === 'test')) {
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Access-Control-Allow-Credentials', 'true');
      res.setHeader(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization, X-CSRF-Token, X-Correlation-Id, Idempotency-Key'
      );
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    }

    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    // Helper functions
    const sendJson = (statusCode: number, data: unknown, headers: Record<string, string> = {}) => {
      res.writeHead(statusCode, {
        'Content-Type': 'application/json; charset=utf-8',
        ...headers
      });
      res.end(JSON.stringify(data));
    };

    const sendError = (statusCode: number, code: string, message: string, headers: Record<string, string> = {}) => {
      sendJson(statusCode, { error: code, message, correlationId, timestamp }, headers);
    };

    // Parse URL & IP
    const url = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);
    const pathname = url.pathname;
    const clientIp = (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() || req.socket.remoteAddress || '127.0.0.1';
    const ipSubnet = clientIp.includes(':') ? `${clientIp.slice(0, clientIp.lastIndexOf(':'))}::/48` : `${clientIp.slice(0, clientIp.lastIndexOf('.'))}.0/24`;

    // Health check (zero secrets)
    if (req.method === 'GET' && (pathname === '/api/v1/health' || pathname === '/health')) {
      sendJson(200, { status: 'healthy', version: '0.1.0', timestamp });
      return;
    }

    // Parse Body
    let body: any = {};
    if (['POST', 'PATCH', 'PUT'].includes(req.method || '')) {
      try {
        body = await readJsonBody(req);
      } catch (err) {
        sendError(400, 'invalid_json_body', 'Request payload could not be parsed as JSON');
        return;
      }
    }

    // Session resolution (Cookie or Bearer)
    const cookies = parseCookies(req.headers['cookie']);
    const sessionToken = cookies['sid'] || parseBearerToken(req.headers['authorization']);
    let sessionUser: { user: UserProfile; sessionId: string } | null = null;
    if (sessionToken) {
      sessionUser = authService.resolveSession(sessionToken);
    }

    // Rate Limiting Enforcement
    const rateLimitKey = `${ipSubnet}:${pathname}`;
    let limit = 120;
    let windowSec = 60;

    if (pathname === '/api/v1/auth/login' || pathname === '/api/v1/auth/desktop-login') {
      limit = 10;
      windowSec = 900; // 15 mins
    } else if (pathname === '/api/v1/auth/register') {
      limit = 10;
      windowSec = 3600; // 1 hour
    } else if (pathname === '/api/v1/auth/forgot-password') {
      limit = 5;
      windowSec = 900;
    }

    const rateResult = globalRateLimiter.check(rateLimitKey, limit, windowSec);
    const rateHeaders = {
      'X-RateLimit-Limit': String(rateResult.limit),
      'X-RateLimit-Remaining': String(rateResult.remaining),
      'X-RateLimit-Reset': String(Math.floor(Date.now() / 1000) + rateResult.resetSeconds)
    };

    if (!rateResult.allowed) {
      sendError(429, 'rate_limit_exceeded', 'Too many requests. Please try again later.', {
        ...rateHeaders,
        'Retry-After': String(rateResult.resetSeconds)
      });
      return;
    }

    // Routing
    try {
      // 1. Direct Registration (NO EMAIL VERIFICATION GATE)
      if (req.method === 'POST' && pathname === '/api/v1/auth/register') {
        const result = await authService.register(body.email, body.password, body.displayName, ipSubnet, 'web');
        const cookie = `sid=${result.sessionToken}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`;
        sendJson(201, { user: result.user, csrfToken: result.csrfToken }, {
          'Set-Cookie': cookie,
          'X-CSRF-Token': result.csrfToken,
          ...rateHeaders
        });
        return;
      }

      // 2. Web Login
      if (req.method === 'POST' && pathname === '/api/v1/auth/login') {
        const result = await authService.login(body.email, body.password, ipSubnet, 'web');
        const cookie = `sid=${result.sessionToken}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`;
        sendJson(200, { user: result.user, csrfToken: result.csrfToken }, {
          'Set-Cookie': cookie,
          'X-CSRF-Token': result.csrfToken,
          ...rateHeaders
        });
        return;
      }

      // 3. Desktop Direct Login
      if (req.method === 'POST' && pathname === '/api/v1/auth/desktop-login') {
        const result = await authService.desktopLogin(body.email, body.password, body.deviceName, ipSubnet);
        sendJson(200, result, rateHeaders);
        return;
      }

      // 4. Desktop Refresh
      if (req.method === 'POST' && pathname === '/api/v1/auth/desktop-refresh') {
        if (!body.refreshToken) {
          sendError(400, 'missing_refresh_token', 'refreshToken is required');
          return;
        }
        const result = await authService.desktopRefresh(body.refreshToken);
        sendJson(200, result, rateHeaders);
        return;
      }

      // 5. Single-Device Logout
      if (req.method === 'POST' && pathname === '/api/v1/auth/logout') {
        if (sessionToken) {
          authService.logout(sessionToken);
        }
        sendJson(200, { message: 'Session terminated successfully' }, {
          'Set-Cookie': 'sid=; Path=/; Max-Age=0',
          ...rateHeaders
        });
        return;
      }

      // 6. Global Logout (All Devices)
      if (req.method === 'POST' && pathname === '/api/v1/auth/logout-all') {
        if (!sessionUser) {
          sendError(401, 'unauthorized', 'Authentication required');
          return;
        }
        authService.logoutAll(sessionUser.user.id);
        sendJson(200, { message: 'All active sessions have been revoked' }, {
          'Set-Cookie': 'sid=; Path=/; Max-Age=0',
          ...rateHeaders
        });
        return;
      }

      // 7. Forgot Password (Request Link)
      if (req.method === 'POST' && pathname === '/api/v1/auth/forgot-password') {
        const result = authService.forgotPassword(body.email || '', ipSubnet);
        sendJson(200, result, rateHeaders);
        return;
      }

      // 8. Reset Password Execution
      if (req.method === 'POST' && pathname === '/api/v1/auth/reset-password') {
        if (!body.token || !body.newPassword) {
          sendError(400, 'missing_required_fields', 'Both token and newPassword are required');
          return;
        }
        authService.resetPassword(body.token, body.newPassword);
        sendJson(200, { message: 'Password updated successfully. Please log in with your new password.' }, rateHeaders);
        return;
      }

      // Protected routes require valid sessionUser
      if (!sessionUser) {
        sendError(401, 'unauthorized', 'Authentication required for this resource', rateHeaders);
        return;
      }

      // 9. Get Profile
      if (req.method === 'GET' && pathname === '/api/v1/users/me') {
        const profile = authService.getUserProfile(sessionUser.user.id);
        sendJson(200, profile, rateHeaders);
        return;
      }

      // 10. Update Profile
      if (req.method === 'PATCH' && pathname === '/api/v1/users/me') {
        const updated = authService.updateProfile(sessionUser.user.id, body);
        sendJson(200, updated, rateHeaders);
        return;
      }

      // 11. Change Password
      if (req.method === 'POST' && pathname === '/api/v1/users/me/change-password') {
        if (!body.currentPassword || !body.newPassword) {
          sendError(400, 'missing_password_fields', 'Both currentPassword and newPassword are required');
          return;
        }
        authService.changePassword(
          sessionUser.user.id,
          body.currentPassword,
          body.newPassword,
          body.revokeOtherSessions !== false,
          sessionUser.sessionId
        );
        sendJson(200, { message: 'Password updated successfully' }, rateHeaders);
        return;
      }

      // 12. List Sessions
      if (req.method === 'GET' && pathname === '/api/v1/users/me/sessions') {
        const sessions = authService.getSessions(sessionUser.user.id, sessionUser.sessionId);
        sendJson(200, { sessions }, rateHeaders);
        return;
      }

      // 13. Revoke Session
      const sessionRevokeMatch = pathname.match(/^\/api\/v1\/users\/me\/sessions\/([^/]+)$/);
      if (req.method === 'DELETE' && sessionRevokeMatch) {
        const targetSessionId = sessionRevokeMatch[1];
        if (!targetSessionId) {
          sendError(400, 'invalid_session_id', 'Session ID is required');
          return;
        }
        authService.revokeSession(sessionUser.user.id, targetSessionId);
        sendJson(200, { message: 'Session revoked successfully' }, rateHeaders);
        return;
      }

      // 14. Delete Account
      if (req.method === 'POST' && pathname === '/api/v1/users/me/delete') {
        authService.deleteAccount(sessionUser.user.id, body.currentPassword || '', body.confirmationPhrase || '');
        sendJson(200, { message: 'Account permanently deleted' }, {
          'Set-Cookie': 'sid=; Path=/; Max-Age=0',
          ...rateHeaders
        });
        return;
      }

      // 15. List AI Provider Secrets
      if (req.method === 'GET' && pathname === '/api/v1/users/me/secrets') {
        const secrets = authService.getSecrets(sessionUser.user.id);
        sendJson(200, { secrets }, rateHeaders);
        return;
      }

      // 16. Save AI Provider Secret
      if (req.method === 'POST' && pathname === '/api/v1/users/me/secrets') {
        if (!body.provider || !body.apiKey) {
          sendError(400, 'missing_secret_fields', 'Both provider and apiKey are required');
          return;
        }
        const saved = authService.saveSecret(sessionUser.user.id, body.provider, body.apiKey);
        sendJson(201, saved, rateHeaders);
        return;
      }

      // 17. Delete AI Provider Secret
      const secretDeleteMatch = pathname.match(/^\/api\/v1\/users\/me\/secrets\/([^/]+)$/);
      if (req.method === 'DELETE' && secretDeleteMatch) {
        const provider = secretDeleteMatch[1];
        if (!provider) {
          sendError(400, 'invalid_provider', 'Provider is required');
          return;
        }
        authService.deleteSecret(sessionUser.user.id, provider);
        sendJson(200, { message: 'Provider key deleted' }, rateHeaders);
        return;
      }

      // Fallback: 404 Not Found
      sendError(404, 'not_found', `Route ${req.method} ${pathname} not found`);
    } catch (err: any) {
      const errMsg = err?.message || 'internal_server_error';
      if (errMsg === 'email_already_registered') {
        sendError(409, 'registration_failed', 'Unable to complete registration. If you already have an account, please sign in.');
      } else if (errMsg === 'invalid_credentials' || errMsg === 'invalid_current_password') {
        sendError(401, 'invalid_credentials', 'Invalid email or password');
      } else if (errMsg === 'invalid_or_revoked_token' || errMsg === 'session_expired') {
        sendError(401, 'invalid_or_revoked_token', 'Invalid or expired session token');
      } else if (errMsg === 'session_not_found') {
        sendError(404, 'session_not_found', 'Session not found or already revoked');
      } else if (errMsg === 'password_too_short') {
        sendError(422, 'password_too_short', 'Password must be at least 15 characters long');
      } else if (errMsg === 'password_too_long') {
        sendError(422, 'password_too_long', 'Password must be no more than 128 characters long');
      } else if (errMsg === 'invalid_email_format') {
        sendError(422, 'invalid_email_format', 'Please provide a valid email address');
      } else if (errMsg === 'invalid_or_expired_token') {
        sendError(400, 'invalid_or_expired_token', 'The password reset token is invalid or has expired');
      } else if (errMsg === 'invalid_confirmation_phrase') {
        sendError(400, 'invalid_confirmation_phrase', 'You must type "DELETE MY ACCOUNT" to confirm deletion');
      } else if (errMsg === 'account_suspended') {
        sendError(403, 'account_suspended', 'Account is suspended. Please contact support.');
      } else {
        sendError(500, 'internal_error', 'An unexpected error occurred. Please try again.');
      }
    }
  });

  return server;
}

function readJsonBody(req: http.IncomingMessage): Promise<any> {
  return new Promise((resolve, reject) => {
    let raw = '';
    let bytes = 0;

    req.on('data', (chunk) => {
      bytes += chunk.length;
      if (bytes > MAX_BODY_SIZE) {
        req.destroy();
        reject(new Error('payload_too_large'));
        return;
      }
      raw += chunk;
    });

    req.on('end', () => {
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(err);
      }
    });

    req.on('error', reject);
  });
}

function parseCookies(cookieHeader?: string): Record<string, string> {
  const result: Record<string, string> = {};
  if (!cookieHeader) return result;

  const parts = cookieHeader.split(';');
  for (const part of parts) {
    const [name, ...val] = part.trim().split('=');
    if (name && val.length > 0) {
      result[name] = decodeURIComponent(val.join('='));
    }
  }
  return result;
}

function parseBearerToken(authHeader?: string): string | null {
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }
  return authHeader.slice(7).trim();
}
