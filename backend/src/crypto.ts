import crypto from 'node:crypto';

const SCRYPT_N = 16384;
const SCRYPT_R = 8;
const SCRYPT_P = 1;
const SCRYPT_KEYLEN = 64;
const SCRYPT_MAXMEM = 64 * 1024 * 1024; // 64 MB memory hard

/**
 * Hash a password using scrypt with a unique 16-byte random salt.
 * Formats hash string: $scrypt$N=16384,r=8,p=1$<saltHex>$<derivedKeyHex>
 */
export function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString('hex');
  const derivedKey = crypto.scryptSync(password, salt, SCRYPT_KEYLEN, {
    N: SCRYPT_N,
    r: SCRYPT_R,
    p: SCRYPT_P,
    maxmem: SCRYPT_MAXMEM
  });
  return `$scrypt$N=${SCRYPT_N},r=${SCRYPT_R},p=${SCRYPT_P}$${salt}$${derivedKey.toString('hex')}`;
}

/**
 * Verify a candidate password against the stored scrypt hash using timing-safe comparison.
 */
export function verifyPassword(password: string, storedHash: string): boolean {
  try {
    const parts = storedHash.split('$');
    // Format: ["", "scrypt", "N=...,r=...,p=...", saltHex, derivedKeyHex]
    if (parts.length !== 5 || parts[1] !== 'scrypt') {
      return false;
    }
    const salt = parts[3];
    const expectedKeyHex = parts[4];
    if (!salt || !expectedKeyHex) {
      return false;
    }

    const expectedKey = Buffer.from(expectedKeyHex, 'hex');
    const actualKey = crypto.scryptSync(password, salt, expectedKey.length, {
      N: SCRYPT_N,
      r: SCRYPT_R,
      p: SCRYPT_P,
      maxmem: SCRYPT_MAXMEM
    });

    if (actualKey.length !== expectedKey.length) {
      return false;
    }
    return crypto.timingSafeEqual(actualKey, expectedKey);
  } catch {
    return false;
  }
}

/**
 * Generate a cryptographically secure random token (e.g. for sessions or reset tokens).
 */
export function generateRandomToken(bytes: number = 32): string {
  return crypto.randomBytes(bytes).toString('hex');
}

/**
 * Compute SHA-256 hash of a string (used to index session tokens and reset tokens).
 */
export function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token, 'utf8').digest('hex');
}

/**
 * Master Key for AES-256-GCM envelope encryption (derives from env KMS_MASTER_KEY or fallback dev seed).
 */
function getMasterKey(): Buffer {
  const rawKey = process.env.KMS_MASTER_KEY || 'default-vrm-kms-master-key-dev-seed-32bytes!';
  return crypto.createHash('sha256').update(rawKey).digest();
}

/**
 * Envelope encryption for user-supplied third-party API keys (Gemini, OpenAI).
 */
export function encryptSecret(plaintextKey: string): {
  ciphertext: string;
  nonce: string;
  tag: string;
  keyHint: string;
} {
  const masterKey = getMasterKey();
  const nonce = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', masterKey, nonce);
  
  let ciphertext = cipher.update(plaintextKey, 'utf8', 'hex');
  ciphertext += cipher.final('hex');
  const tag = cipher.getAuthTag().toString('hex');
  
  const keyHint = plaintextKey.length > 4 ? `...${plaintextKey.slice(-4)}` : '****';

  return {
    ciphertext,
    nonce: nonce.toString('hex'),
    tag,
    keyHint
  };
}

/**
 * Decrypt envelope-encrypted secret.
 */
export function decryptSecret(ciphertext: string, nonceHex: string, tagHex: string): string {
  const masterKey = getMasterKey();
  const decipher = crypto.createDecipheriv('aes-256-gcm', masterKey, Buffer.from(nonceHex, 'hex'));
  decipher.setAuthTag(Buffer.from(tagHex, 'hex'));
  
  let plaintext = decipher.update(ciphertext, 'hex', 'utf8');
  plaintext += decipher.final('utf8');
  return plaintext;
}
