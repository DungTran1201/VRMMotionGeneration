import { getDatabase, closeDatabase } from './database.js';
import { createServer } from './server.js';

const PORT = parseInt(process.env.PORT || '3000', 10);
const HOST = process.env.HOST || '127.0.0.1';

const db = getDatabase();
const server = createServer({ db });

server.listen(PORT, HOST, () => {
  console.log(`\n================================================================`);
  console.log(`[VRM Backend] Identity & Auth Service is RUNNING on http://${HOST}:${PORT}`);
  console.log(`[VRM Backend] Health check endpoint: http://${HOST}:${PORT}/api/v1/health`);
  console.log(`[VRM Backend] Registration policy: NO EMAIL VERIFICATION GATE (Active)`);
  console.log(`----------------------------------------------------------------`);
  console.log(`[INFO] Server is actively listening for API requests.`);
  console.log(`[INFO] KEEP THIS TERMINAL RUNNING (it is supposed to stay open).`);
  console.log(`[INFO] In a NEW terminal, run your client:`);
  console.log(`       - Web Browser:       pnpm dev:web`);
  console.log(`       - Electron Desktop:  pnpm dev:desktop`);
  console.log(`================================================================\n`);
});

function handleShutdown() {
  console.log('\n[VRM Backend] Shutting down gracefully...');
  server.close(() => {
    closeDatabase();
    console.log('[VRM Backend] Closed HTTP server and database.');
    process.exit(0);
  });
}

process.on('SIGINT', handleShutdown);
process.on('SIGTERM', handleShutdown);
