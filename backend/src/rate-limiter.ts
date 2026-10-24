export interface RateLimitResult {
  allowed: boolean;
  limit: number;
  remaining: number;
  resetSeconds: number;
}

interface WindowRecord {
  timestamps: number[];
}

export class MemoryRateLimiter {
  private records = new Map<string, WindowRecord>();
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor() {
    // Run periodic cleanup every 5 minutes
    this.cleanupInterval = setInterval(() => this.cleanup(), 5 * 60 * 1000);
    if (this.cleanupInterval.unref) {
      this.cleanupInterval.unref();
    }
  }

  /**
   * Consume a request quota for a key in a given window (seconds).
   */
  public check(key: string, limit: number, windowSeconds: number): RateLimitResult {
    const now = Date.now();
    const windowMs = windowSeconds * 1000;
    const cutoff = now - windowMs;

    let record = this.records.get(key);
    if (!record) {
      record = { timestamps: [] };
      this.records.set(key, record);
    }

    // Filter out timestamps outside window
    record.timestamps = record.timestamps.filter((ts) => ts > cutoff);

    if (record.timestamps.length >= limit) {
      const oldest = record.timestamps[0] || now;
      const resetSeconds = Math.max(1, Math.ceil((oldest + windowMs - now) / 1000));
      return {
        allowed: false,
        limit,
        remaining: 0,
        resetSeconds
      };
    }

    record.timestamps.push(now);
    const remaining = Math.max(0, limit - record.timestamps.length);
    const resetSeconds = windowSeconds;

    return {
      allowed: true,
      limit,
      remaining,
      resetSeconds
    };
  }

  public reset(key: string): void {
    this.records.delete(key);
  }

  public clear(): void {
    this.records.clear();
  }

  private cleanup(): void {
    const now = Date.now();
    const maxWindow = 3600 * 1000; // 1 hour max window
    for (const [key, record] of this.records.entries()) {
      record.timestamps = record.timestamps.filter((ts) => now - ts < maxWindow);
      if (record.timestamps.length === 0) {
        this.records.delete(key);
      }
    }
  }

  public close(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
  }
}

export const globalRateLimiter = new MemoryRateLimiter();
