import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { DatabaseSync } from 'node:sqlite';
import { initSchema } from '../src/database.js';
import { createServer } from '../src/server.js';
import { globalRateLimiter } from '../src/rate-limiter.js';
import http from 'node:http';

describe('Authentication & Account Management API Tests', () => {
  let db: DatabaseSync;
  let server: http.Server;
  let baseUrl: string;

  beforeEach(async () => {
    globalRateLimiter.clear();
    db = new DatabaseSync(':memory:');
    initSchema(db);
    server = createServer({ db });

    await new Promise<void>((resolve) => {
      server.listen(0, '127.0.0.1', () => {
        const addr = server.address() as { port: number };
        baseUrl = `http://127.0.0.1:${addr.port}`;
        resolve();
      });
    });
  });

  afterEach(async () => {
    await new Promise<void>((resolve) => {
      server.close(() => {
        db.close();
        resolve();
      });
    });
  });

  // Helper request function
  async function request(
    path: string,
    options: {
      method?: string;
      body?: any;
      headers?: Record<string, string>;
      cookie?: string;
    } = {}
  ): Promise<{ status: number; body: any; headers: Headers }> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    if (options.cookie) {
      headers['Cookie'] = options.cookie;
    }

    const res = await fetch(`${baseUrl}${path}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    });

    const text = await res.text();
    let parsed: any;
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }

    return { status: res.status, body: parsed, headers: res.headers };
  }

  describe('Health Endpoint', () => {
    it('returns healthy status without exposing secrets', async () => {
      const res = await request('/api/v1/health');
      expect(res.status).toBe(200);
      expect(res.body.status).toBe('healthy');
      expect(res.body.version).toBe('0.1.0');
    });
  });

  describe('Registration (FR-AUTH-001 — NO EMAIL VERIFICATION GATE)', () => {
    it('registers user directly with status active and zero verification tokens', async () => {
      const res = await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'alex@example.com',
          password: 'CorrectHorseBatteryStaple123!',
          displayName: 'Alex Chen'
        }
      });

      expect(res.status).toBe(201);
      expect(res.body.user).toBeDefined();
      expect(res.body.user.email).toBe('alex@example.com');
      expect(res.body.user.status).toBe('active');
      expect(res.body.user.emailVerified).toBe(false);
      expect(res.body.user.emailStatusNotice).toContain('unverified');
      expect(res.body.csrfToken).toBeDefined();

      // Verify Set-Cookie header contains sid
      const setCookie = res.headers.get('set-cookie');
      expect(setCookie).toContain('sid=');
      expect(setCookie).toContain('HttpOnly');
      expect(setCookie).toContain('SameSite=Lax');

      // Verify in DB that account status is active
      const userInDb = db.prepare('SELECT status, password_hash FROM users WHERE email = ?').get('alex@example.com') as any;
      expect(userInDb).toBeDefined();
      expect(userInDb.status).toBe('active');
      expect(userInDb.password_hash).not.toContain('CorrectHorseBatteryStaple123!'); // Salted & hashed

      // Verify zero verification tokens exist in DB
      const resetTokens = db.prepare('SELECT COUNT(*) as count FROM password_reset_tokens').get() as any;
      expect(resetTokens.count).toBe(0);
    });

    it('rejects password shorter than 15 characters (SEC-PWD-001)', async () => {
      const res = await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'short@example.com',
          password: 'Short123!'
        }
      });

      expect(res.status).toBe(422);
      expect(res.body.error).toBe('password_too_short');
    });

    it('rejects duplicate email with generic anti-enumeration response', async () => {
      await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'duplicate@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });

      // Attempt second registration with same email (different case)
      const res = await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'DUPLICATE@example.com',
          password: 'AnotherSecureHorseBattery987!'
        }
      });

      expect(res.status).toBe(409);
      expect(res.body.error).toBe('registration_failed');
    });
  });

  describe('Web Login & Session Lifecycle (FR-AUTH-004, FR-AUTH-005)', () => {
    beforeEach(async () => {
      await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'john@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });
    });

    it('authenticates valid credentials and issues session cookie', async () => {
      const res = await request('/api/v1/auth/login', {
        method: 'POST',
        body: {
          email: 'john@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });

      expect(res.status).toBe(200);
      expect(res.body.user.email).toBe('john@example.com');
      expect(res.body.csrfToken).toBeDefined();
      expect(res.headers.get('set-cookie')).toContain('sid=');
    });

    it('returns generic 401 error for invalid password or nonexistent email', async () => {
      const res1 = await request('/api/v1/auth/login', {
        method: 'POST',
        body: {
          email: 'john@example.com',
          password: 'WrongPasswordGivenHere!'
        }
      });
      expect(res1.status).toBe(401);
      expect(res1.body.message).toBe('Invalid email or password');

      const res2 = await request('/api/v1/auth/login', {
        method: 'POST',
        body: {
          email: 'nonexistent@example.com',
          password: 'AnyPasswordProvided123!'
        }
      });
      expect(res2.status).toBe(401);
      expect(res2.body.message).toBe('Invalid email or password');
    });

    it('logs out and revokes active session', async () => {
      const loginRes = await request('/api/v1/auth/login', {
        method: 'POST',
        body: {
          email: 'john@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });
      const cookie = loginRes.headers.get('set-cookie')!.split(';')[0];

      // Access profile
      const profRes = await request('/api/v1/users/me', { cookie });
      expect(profRes.status).toBe(200);

      // Logout
      const logoutRes = await request('/api/v1/auth/logout', { method: 'POST', cookie });
      expect(logoutRes.status).toBe(200);

      // Subsequent access with old cookie returns 401
      const afterRes = await request('/api/v1/users/me', { cookie });
      expect(afterRes.status).toBe(401);
    });
  });

  describe('Desktop Native Login & Token Refresh (RFC 8252, safeStorage)', () => {
    beforeEach(async () => {
      await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'desktop@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });
    });

    it('performs desktop login returning access token and refresh token', async () => {
      const res = await request('/api/v1/auth/desktop-login', {
        method: 'POST',
        body: {
          email: 'desktop@example.com',
          password: 'CorrectHorseBatteryStaple123!',
          deviceName: 'Windows-Station-1'
        }
      });

      expect(res.status).toBe(200);
      expect(res.body.accessToken).toBeDefined();
      expect(res.body.refreshToken).toBeDefined();
      expect(res.body.expiresIn).toBe(900); // 15 mins

      // Access protected endpoint via Bearer token
      const profileRes = await request('/api/v1/users/me', {
        headers: { Authorization: `Bearer ${res.body.refreshToken}` }
      });
      expect(profileRes.status).toBe(200);
      expect(profileRes.body.email).toBe('desktop@example.com');
    });

    it('refreshes desktop tokens with sliding rotation', async () => {
      const loginRes = await request('/api/v1/auth/desktop-login', {
        method: 'POST',
        body: {
          email: 'desktop@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });

      const oldRefresh = loginRes.body.refreshToken;

      const refreshRes = await request('/api/v1/auth/desktop-refresh', {
        method: 'POST',
        body: { refreshToken: oldRefresh }
      });

      expect(refreshRes.status).toBe(200);
      expect(refreshRes.body.accessToken).toBeDefined();
      expect(refreshRes.body.refreshToken).toBeDefined();
      expect(refreshRes.body.refreshToken).not.toBe(oldRefresh);

      // Old refresh token is no longer valid
      const secondRefresh = await request('/api/v1/auth/desktop-refresh', {
        method: 'POST',
        body: { refreshToken: oldRefresh }
      });
      expect(secondRefresh.status).toBe(401);
    });
  });

  describe('Password Reset Lifecycle (FR-ACCT-001, FR-ACCT-002)', () => {
    it('executes password reset with single-use token and invalidates prior sessions', async () => {
      process.env.NODE_ENV = 'test';
      const regRes = await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'recovery@example.com',
          password: 'OriginalHorseBatteryStaple123!'
        }
      });
      const originalCookie = regRes.headers.get('set-cookie')!.split(';')[0];

      // Request reset
      const forgotRes = await request('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: { email: 'recovery@example.com' }
      });
      expect(forgotRes.status).toBe(200);
      const testToken = forgotRes.body.testToken;
      expect(testToken).toBeDefined();

      // Execute reset
      const resetRes = await request('/api/v1/auth/reset-password', {
        method: 'POST',
        body: {
          token: testToken,
          newPassword: 'BrandNewHorseBatteryStaple999!'
        }
      });
      expect(resetRes.status).toBe(200);

      // Prior session cookie is now revoked
      const oldCheck = await request('/api/v1/users/me', { cookie: originalCookie });
      expect(oldCheck.status).toBe(401);

      // Token cannot be reused
      const reuseRes = await request('/api/v1/auth/reset-password', {
        method: 'POST',
        body: {
          token: testToken,
          newPassword: 'AnotherPasswordAttempt12345!'
        }
      });
      expect(reuseRes.status).toBe(400);

      // Login with new password succeeds
      const newLogin = await request('/api/v1/auth/login', {
        method: 'POST',
        body: {
          email: 'recovery@example.com',
          password: 'BrandNewHorseBatteryStaple999!'
        }
      });
      expect(newLogin.status).toBe(200);
    });
  });

  describe('User AI Provider Secrets Vault (FR-SECR-001)', () => {
    let authCookie: string;

    beforeEach(async () => {
      const reg = await request('/api/v1/auth/register', {
        method: 'POST',
        body: {
          email: 'vault@example.com',
          password: 'CorrectHorseBatteryStaple123!'
        }
      });
      authCookie = reg.headers.get('set-cookie')!.split(';')[0];
    });

    it('stores encrypted key, exposes only masked hint, and never leaks plaintext', async () => {
      // Save Gemini API key
      const saveRes = await request('/api/v1/users/me/secrets', {
        method: 'POST',
        cookie: authCookie,
        body: {
          provider: 'gemini',
          apiKey: 'AIzaSyD_SECRET_GEMINI_KEY_9999'
        }
      });

      expect(saveRes.status).toBe(201);
      expect(saveRes.body.provider).toBe('gemini');
      expect(saveRes.body.keyHint).toBe('...9999');
      expect(saveRes.body.apiKey).toBeUndefined(); // Plaintext stripped

      // List secrets
      const listRes = await request('/api/v1/users/me/secrets', { cookie: authCookie });
      expect(listRes.status).toBe(200);
      expect(listRes.body.secrets).toHaveLength(1);
      expect(listRes.body.secrets[0].keyHint).toBe('...9999');

      // Inspect DB directly: plaintext is NOT stored
      const rawInDb = db.prepare('SELECT ciphertext, nonce, tag FROM user_secrets_vault').get() as any;
      expect(rawInDb.ciphertext).not.toContain('AIzaSyD_SECRET_GEMINI_KEY_9999');

      // Delete secret
      const delRes = await request('/api/v1/users/me/secrets/gemini', {
        method: 'DELETE',
        cookie: authCookie
      });
      expect(delRes.status).toBe(200);

      const afterList = await request('/api/v1/users/me/secrets', { cookie: authCookie });
      expect(afterList.body.secrets).toHaveLength(0);
    });
  });

  describe('IDOR / BOLA Prevention on Sessions (SEC-IDOR)', () => {
    it('prevents user A from revoking user B session', async () => {
      // User A
      const resA = await request('/api/v1/auth/register', {
        method: 'POST',
        body: { email: 'usera@example.com', password: 'CorrectHorseBatteryStaple123!' }
      });
      const cookieA = resA.headers.get('set-cookie')!.split(';')[0];

      // User B
      const resB = await request('/api/v1/auth/register', {
        method: 'POST',
        body: { email: 'userb@example.com', password: 'CorrectHorseBatteryStaple123!' }
      });
      const cookieB = resB.headers.get('set-cookie')!.split(';')[0];

      // Get User B session ID
      const sessionsB = await request('/api/v1/users/me/sessions', { cookie: cookieB });
      const userBSessionId = sessionsB.body.sessions[0].id;

      // User A attempts to delete User B session
      const attackRes = await request(`/api/v1/users/me/sessions/${userBSessionId}`, {
        method: 'DELETE',
        cookie: cookieA
      });
      expect(attackRes.status).toBe(404); // Session not found or belongs to another user

      // Verify User B session is still active
      const checkB = await request('/api/v1/users/me', { cookie: cookieB });
      expect(checkB.status).toBe(200);
    });
  });
});
