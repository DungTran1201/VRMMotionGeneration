import { getDatabase, closeDatabase } from './database.js';
import { createServer } from './server.js';

const PORT = parseInt(process.env.PORT || '3000', 10);
const HOST = process.env.HOST || '127.0.0.1';

const db = getDatabase();
const server = createServer({ db });

server.listen(PORT, HOST, () => {
  console.log(`[VRM Backend] Identity & Auth Service listening on http://${HOST}:${PORT}`);
  console.log(`[VRM Backend] Health check available at http://${HOST}:${PORT}/api/v1/health`);
  console.log(`[VRM Backend] Registration policy: NO EMAIL VERIFICATION GATE (Active by default)`);
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
