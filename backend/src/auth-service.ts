import type { DatabaseSync } from 'node:sqlite';
import crypto from 'node:crypto';
import type { UserProfile, UserSession, ProviderSecretItem } from '@vrm/platform-contracts';
import { hashPassword, verifyPassword, generateRandomToken, hashToken, encryptSecret } from './crypto.js';

export interface UserRow {
  id: string;
  email: string;
  password_hash: string;
  status: string;
  failed_login_attempts: number;
  lockout_until: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileRow {
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  locale: string;
  timezone: string;
  updated_at: string;
}

export interface SessionRow {
  id: string;
  user_id: string;
  token_hash: string;
  client_type: 'web' | 'desktop';
  device_name: string;
  ip_subnet: string;
  idle_expires_at: string;
  absolute_expires_at: string;
  revoked_at: string | null;
  created_at: string;
  last_seen_at: string;
}

export class AuthService {
  constructor(private db: DatabaseSync) {}

  public async register(
    emailRaw: string,
    passwordRaw: string,
    displayNameRaw?: string,
    ipSubnet: string = '127.0.0.1/32',
    clientType: 'web' | 'desktop' = 'web'
  ): Promise<{ user: UserProfile; sessionToken: string; csrfToken: string }> {
    const email = emailRaw.trim().toLowerCase();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      throw new Error('invalid_email_format');
    }

    if (!passwordRaw || passwordRaw.length < 15) {
      throw new Error('password_too_short');
    }

    if (passwordRaw.length > 128) {
      throw new Error('password_too_long');
    }

    // Check existing email
    const existing = this.db.prepare('SELECT id FROM users WHERE email = ?').get(email) as { id: string } | undefined;
    if (existing) {
      // Execute dummy work to equalize timing
      hashPassword(passwordRaw);
      throw new Error('email_already_registered');
    }

    const userId = crypto.randomUUID();
    const now = new Date().toISOString();
    const passwordHash = hashPassword(passwordRaw);
    const displayName = displayNameRaw?.trim() || email.split('@')[0] || 'User';

    this.db.exec('BEGIN TRANSACTION;');
    try {
      this.db
        .prepare('INSERT INTO users (id, email, password_hash, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(userId, email, passwordHash, 'active', now, now);

      this.db
        .prepare('INSERT INTO user_profiles (user_id, display_name, locale, timezone, updated_at) VALUES (?, ?, ?, ?, ?)')
        .run(userId, displayName, 'en-US', 'UTC', now);

      this.db.exec('COMMIT;');
    } catch (err) {
      this.db.exec('ROLLBACK;');
      throw err;
    }

    const session = this.createSession(userId, clientType, `${clientType}-client`, ipSubnet);
    const user = this.getUserProfile(userId);
    if (!user) throw new Error('user_creation_failed');

    return {
      user,
      sessionToken: session.rawToken,
      csrfToken: session.csrfToken
    };
  }

  public async login(
    emailRaw: string,
    passwordRaw: string,
    ipSubnet: string = '127.0.0.1/32',
    clientType: 'web' | 'desktop' = 'web',
    deviceName: string = 'web-browser'
  ): Promise<{ user: UserProfile; sessionToken: string; csrfToken: string }> {
    const email = emailRaw.trim().toLowerCase();
    const userRow = this.db.prepare('SELECT * FROM users WHERE email = ?').get(email) as UserRow | undefined;

    if (!userRow) {
      // Timing attack equalization
      hashPassword(passwordRaw);
      throw new Error('invalid_credentials');
    }

    if (userRow.status !== 'active') {
      throw new Error('account_suspended');
    }

    const isMatch = verifyPassword(passwordRaw, userRow.password_hash);
    if (!isMatch) {
      this.db
        .prepare('UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = ?')
        .run(userRow.id);
      throw new Error('invalid_credentials');
    }

    // Reset failed login counter on success
    this.db.prepare('UPDATE users SET failed_login_attempts = 0 WHERE id = ?').run(userRow.id);

    const session = this.createSession(userRow.id, clientType, deviceName, ipSubnet);
    const user = this.getUserProfile(userRow.id);
    if (!user) throw new Error('user_not_found');

    return {
      user,
      sessionToken: session.rawToken,
      csrfToken: session.csrfToken
    };
  }

  public async desktopLogin(
    emailRaw: string,
    passwordRaw: string,
    deviceName: string = 'Desktop Workstation',
    ipSubnet: string = '127.0.0.1/32'
  ): Promise<{
    accessToken: string;
    expiresIn: number;
    refreshToken: string;
    refreshExpiresIn: number;
    user: UserProfile;
  }> {
    const loginResult = await this.login(emailRaw, passwordRaw, ipSubnet, 'desktop', deviceName);
    
    // For desktop: sessionToken acts as the long-lived refresh token
    const refreshToken = loginResult.sessionToken;
    const accessToken = generateRandomToken(24);

    return {
      accessToken,
      expiresIn: 900, // 15 minutes
      refreshToken,
      refreshExpiresIn: 90 * 86400, // 90 days
      user: loginResult.user
    };
  }

  public async desktopRefresh(refreshToken: string): Promise<{
    accessToken: string;
    expiresIn: number;
    refreshToken: string;
  }> {
    const tokenHash = hashToken(refreshToken);
    const sessionRow = this.db
      .prepare('SELECT * FROM sessions WHERE token_hash = ? AND revoked_at IS NULL')
      .get(tokenHash) as SessionRow | undefined;

    if (!sessionRow) {
      throw new Error('invalid_or_revoked_token');
    }

    const now = new Date();
    if (new Date(sessionRow.absolute_expires_at) < now) {
      this.db.prepare('UPDATE sessions SET revoked_at = ? WHERE id = ?').run(now.toISOString(), sessionRow.id);
      throw new Error('session_expired');
    }

    // Rotate refresh token
    const newRefreshToken = generateRandomToken(32);
    const newTokenHash = hashToken(newRefreshToken);
    const idleExpiry = new Date(Date.now() + 7 * 86400 * 1000).toISOString();

    this.db
      .prepare('UPDATE sessions SET token_hash = ?, idle_expires_at = ?, last_seen_at = ? WHERE id = ?')
      .run(newTokenHash, idleExpiry, now.toISOString(), sessionRow.id);

    return {
      accessToken: generateRandomToken(24),
      expiresIn: 900,
      refreshToken: newRefreshToken
    };
  }

  public logout(sessionToken: string): void {
    const tokenHash = hashToken(sessionToken);
    const now = new Date().toISOString();
    this.db.prepare('UPDATE sessions SET revoked_at = ? WHERE token_hash = ?').run(now, tokenHash);
  }

  public logoutAll(userId: string): void {
    const now = new Date().toISOString();
    this.db
      .prepare('UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL')
      .run(now, userId);
  }

  public forgotPassword(emailRaw: string, ipSubnet: string = '127.0.0.1/32'): { message: string; testToken?: string } {
    const email = emailRaw.trim().toLowerCase();
    const userRow = this.db.prepare('SELECT id, status FROM users WHERE email = ?').get(email) as UserRow | undefined;

    let testToken: string | undefined;

    if (userRow && userRow.status === 'active') {
      const rawToken = generateRandomToken(32);
      const tokenHash = hashToken(rawToken);
      const now = new Date();
      const expiresAt = new Date(now.getTime() + 15 * 60 * 1000).toISOString();

      this.db
        .prepare('INSERT INTO password_reset_tokens (id, user_id, token_hash, expires_at, ip_subnet, created_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(crypto.randomUUID(), userRow.id, tokenHash, expiresAt, ipSubnet, now.toISOString());

      testToken = rawToken;
    } else {
      // Timing equalization
      generateRandomToken(32);
    }

    return {
      message: 'If that email address is in our system, we have dispatched a password reset link to it.',
      testToken: process.env.NODE_ENV === 'test' ? testToken : undefined
    };
  }

  public resetPassword(tokenRaw: string, newPasswordRaw: string): void {
    if (!newPasswordRaw || newPasswordRaw.length < 15) {
      throw new Error('password_too_short');
    }
    if (newPasswordRaw.length > 128) {
      throw new Error('password_too_long');
    }

    const tokenHash = hashToken(tokenRaw);
    const tokenRow = this.db
      .prepare('SELECT * FROM password_reset_tokens WHERE token_hash = ?')
      .get(tokenHash) as { id: string; user_id: string; expires_at: string; used_at: string | null } | undefined;

    if (!tokenRow || tokenRow.used_at !== null) {
      throw new Error('invalid_or_expired_token');
    }

    const now = new Date();
    if (new Date(tokenRow.expires_at) < now) {
      throw new Error('invalid_or_expired_token');
    }

    const newHash = hashPassword(newPasswordRaw);

    this.db.exec('BEGIN TRANSACTION;');
    try {
      this.db
        .prepare('UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?')
        .run(newHash, now.toISOString(), tokenRow.user_id);

      this.db
        .prepare('UPDATE password_reset_tokens SET used_at = ? WHERE id = ?')
        .run(now.toISOString(), tokenRow.id);

      // Invalidate all prior sessions
      this.db
        .prepare('UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL')
        .run(now.toISOString(), tokenRow.user_id);

      this.db.exec('COMMIT;');
    } catch (err) {
      this.db.exec('ROLLBACK;');
      throw err;
    }
  }

  public getUserProfile(userId: string): UserProfile | null {
    const userRow = this.db.prepare('SELECT * FROM users WHERE id = ?').get(userId) as UserRow | undefined;
    if (!userRow) return null;

    const profileRow = this.db.prepare('SELECT * FROM user_profiles WHERE user_id = ?').get(userId) as ProfileRow | undefined;

    return {
      id: userRow.id,
      email: userRow.email,
      status: userRow.status as 'active' | 'suspended' | 'deactivated',
      emailVerified: false,
      emailStatusNotice: 'Email address is self-asserted and unverified.',
      displayName: profileRow?.display_name || 'User',
      avatarUrl: profileRow?.avatar_url || null,
      locale: profileRow?.locale || 'en-US',
      timezone: profileRow?.timezone || 'UTC',
      createdAt: userRow.created_at
    };
  }

  public updateProfile(
    userId: string,
    updates: { displayName?: string; avatarUrl?: string | null; locale?: string; timezone?: string }
  ): UserProfile {
    const now = new Date().toISOString();
    const current = this.getUserProfile(userId);
    if (!current) throw new Error('user_not_found');

    const displayName = updates.displayName !== undefined ? updates.displayName.trim() : current.displayName;
    const avatarUrl = updates.avatarUrl !== undefined ? updates.avatarUrl : current.avatarUrl;
    const locale = updates.locale !== undefined ? updates.locale.trim() : current.locale;
    const timezone = updates.timezone !== undefined ? updates.timezone.trim() : current.timezone;

    this.db
      .prepare('UPDATE user_profiles SET display_name = ?, avatar_url = ?, locale = ?, timezone = ?, updated_at = ? WHERE user_id = ?')
      .run(displayName, avatarUrl, locale, timezone, now, userId);

    return this.getUserProfile(userId)!;
  }

  public changePassword(
    userId: string,
    currentPasswordRaw: string,
    newPasswordRaw: string,
    revokeOthers: boolean = true,
    currentSessionId?: string
  ): void {
    if (!newPasswordRaw || newPasswordRaw.length < 15) {
      throw new Error('password_too_short');
    }

    const userRow = this.db.prepare('SELECT * FROM users WHERE id = ?').get(userId) as UserRow | undefined;
    if (!userRow) throw new Error('user_not_found');

    const isMatch = verifyPassword(currentPasswordRaw, userRow.password_hash);
    if (!isMatch) {
      throw new Error('invalid_current_password');
    }

    const now = new Date().toISOString();
    const newHash = hashPassword(newPasswordRaw);

    this.db.exec('BEGIN TRANSACTION;');
    try {
      this.db.prepare('UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?').run(newHash, now, userId);

      if (revokeOthers) {
        if (currentSessionId) {
          this.db
            .prepare('UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND id != ? AND revoked_at IS NULL')
            .run(now, userId, currentSessionId);
        } else {
          this.db
            .prepare('UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL')
            .run(now, userId);
        }
      }

      this.db.exec('COMMIT;');
    } catch (err) {
      this.db.exec('ROLLBACK;');
      throw err;
    }
  }

  public getSessions(userId: string, currentSessionId?: string): UserSession[] {
    const rows = this.db
      .prepare('SELECT * FROM sessions WHERE user_id = ? AND revoked_at IS NULL ORDER BY created_at DESC')
      .all(userId) as unknown as SessionRow[];

    return rows.map((r) => ({
      id: r.id,
      clientType: r.client_type,
      deviceName: r.device_name,
      ipSubnet: r.ip_subnet,
      isCurrent: r.id === currentSessionId,
      lastSeenAt: r.last_seen_at,
      createdAt: r.created_at
    }));
  }

  public revokeSession(userId: string, sessionId: string): void {
    const session = this.db.prepare('SELECT user_id FROM sessions WHERE id = ?').get(sessionId) as { user_id: string } | undefined;
    if (!session || session.user_id !== userId) {
      throw new Error('session_not_found');
    }

    const now = new Date().toISOString();
    this.db.prepare('UPDATE sessions SET revoked_at = ? WHERE id = ?').run(now, sessionId);
  }

  public deleteAccount(userId: string, currentPasswordRaw: string, confirmationPhrase: string): void {
    if (confirmationPhrase !== 'DELETE MY ACCOUNT') {
      throw new Error('invalid_confirmation_phrase');
    }

    const userRow = this.db.prepare('SELECT * FROM users WHERE id = ?').get(userId) as UserRow | undefined;
    if (!userRow) throw new Error('user_not_found');

    const isMatch = verifyPassword(currentPasswordRaw, userRow.password_hash);
    if (!isMatch) {
      throw new Error('invalid_current_password');
    }

    // Delete user cascades to profiles, sessions, tokens, secrets
    this.db.prepare('DELETE FROM users WHERE id = ?').run(userId);
  }

  public getSecrets(userId: string): ProviderSecretItem[] {
    const rows = this.db
      .prepare('SELECT provider, key_hint, created_at, updated_at FROM user_secrets_vault WHERE user_id = ?')
      .all(userId) as unknown as Array<{ provider: 'gemini' | 'openai' | 'anthropic'; key_hint: string; created_at: string; updated_at: string }>;

    return rows.map((r) => ({
      provider: r.provider,
      keyHint: r.key_hint,
      createdAt: r.created_at,
      updatedAt: r.updated_at
    }));
  }

  public saveSecret(userId: string, provider: 'gemini' | 'openai' | 'anthropic', apiKey: string): ProviderSecretItem {
    if (!apiKey || apiKey.trim().length < 8) {
      throw new Error('invalid_api_key');
    }

    const encrypted = encryptSecret(apiKey.trim());
    const now = new Date().toISOString();
    const id = crypto.randomUUID();

    this.db
      .prepare(`
        INSERT INTO user_secrets_vault (id, user_id, provider, ciphertext, nonce, tag, key_hint, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, provider) DO UPDATE SET
          ciphertext = excluded.ciphertext,
          nonce = excluded.nonce,
          tag = excluded.tag,
          key_hint = excluded.key_hint,
          updated_at = excluded.updated_at
      `)
      .run(id, userId, provider, encrypted.ciphertext, encrypted.nonce, encrypted.tag, encrypted.keyHint, now, now);

    return {
      provider,
      keyHint: encrypted.keyHint,
      createdAt: now,
      updatedAt: now
    };
  }

  public deleteSecret(userId: string, provider: string): void {
    this.db.prepare('DELETE FROM user_secrets_vault WHERE user_id = ? AND provider = ?').run(userId, provider);
  }

  public resolveSession(sessionToken: string): { user: UserProfile; sessionId: string } | null {
    const tokenHash = hashToken(sessionToken);
    const sessionRow = this.db
      .prepare('SELECT * FROM sessions WHERE token_hash = ? AND revoked_at IS NULL')
      .get(tokenHash) as SessionRow | undefined;

    if (!sessionRow) return null;

    const now = new Date();
    if (new Date(sessionRow.idle_expires_at) < now || new Date(sessionRow.absolute_expires_at) < now) {
      this.db.prepare('UPDATE sessions SET revoked_at = ? WHERE id = ?').run(now.toISOString(), sessionRow.id);
      return null;
    }

    // Slide idle window
    const newIdle = new Date(now.getTime() + 24 * 3600 * 1000).toISOString();
    this.db
      .prepare('UPDATE sessions SET last_seen_at = ?, idle_expires_at = ? WHERE id = ?')
      .run(now.toISOString(), newIdle, sessionRow.id);

    const user = this.getUserProfile(sessionRow.user_id);
    if (!user || user.status !== 'active') return null;

    return { user, sessionId: sessionRow.id };
  }

  private createSession(
    userId: string,
    clientType: 'web' | 'desktop',
    deviceName: string,
    ipSubnet: string
  ): { rawToken: string; csrfToken: string; sessionId: string } {
    const sessionId = crypto.randomUUID();
    const rawToken = generateRandomToken(32);
    const csrfToken = generateRandomToken(16);
    const tokenHash = hashToken(rawToken);

    const now = new Date();
    const idleHours = clientType === 'desktop' ? 7 * 24 : 24;
    const absDays = clientType === 'desktop' ? 90 : 30;

    const idleExpiresAt = new Date(now.getTime() + idleHours * 3600 * 1000).toISOString();
    const absExpiresAt = new Date(now.getTime() + absDays * 86400 * 1000).toISOString();

    this.db
      .prepare(`
        INSERT INTO sessions (id, user_id, token_hash, client_type, device_name, ip_subnet, idle_expires_at, absolute_expires_at, created_at, last_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `)
      .run(
        sessionId,
        userId,
        tokenHash,
        clientType,
        deviceName,
        ipSubnet,
        idleExpiresAt,
        absExpiresAt,
        now.toISOString(),
        now.toISOString()
      );

    return { rawToken, csrfToken, sessionId };
  }
}
