/**
 * OpenCivilizations Server - Entry Point
 */

import { createServer } from 'http';
import express from 'express';
import { Server } from '@colyseus/core';
import { WebSocketTransport } from '@colyseus/ws-transport';
import { GameRoom } from './rooms/GameRoom';
import { connectDatabase } from './db';

const app = express();
const port = parseInt(process.env.PORT || '2567', 10);

// Middleware
app.use(express.json());

// Health check endpoint
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: Date.now() });
});

async function main() {
  // Connect to MongoDB
  await connectDatabase();

  // Create HTTP server
  const httpServer = createServer(app);

  // Create Colyseus server
  const gameServer = new Server({
    transport: new WebSocketTransport({ server: httpServer }),
  });

  // Register game room
  gameServer.define('game', GameRoom);

  // Start listening
  httpServer.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
    console.log(`WebSocket available at ws://localhost:${port}`);
  });
}

main().catch((err) => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
