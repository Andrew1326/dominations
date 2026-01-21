/**
 * Seed script - creates multiple test players with bases for matchmaking testing
 * Run: npx tsx scripts/seed-players.ts
 */

import mongoose from 'mongoose';
import { User } from '../src/models/User';
import { Base } from '../src/models/Base';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/opencivilizations';

const testPlayers = [
  {
    username: 'warrior_alex',
    email: 'alex@test.com',
    buildings: [
      { id: 'tc1', type: 'townCenter', row: 10, col: 10, level: 2 },
      { id: 'f1', type: 'farm', row: 8, col: 8, level: 1 },
      { id: 'f2', type: 'farm', row: 8, col: 12, level: 1 },
      { id: 'gm1', type: 'goldMine', row: 12, col: 8, level: 1 },
    ],
    resources: { food: 1500, gold: 1200, oil: 50 },
  },
  {
    username: 'builder_bob',
    email: 'bob@test.com',
    buildings: [
      { id: 'tc1', type: 'townCenter', row: 15, col: 15, level: 3 },
      { id: 'h1', type: 'house', row: 13, col: 13, level: 2 },
      { id: 'h2', type: 'house', row: 13, col: 17, level: 2 },
      { id: 'f1', type: 'farm', row: 17, col: 13, level: 2 },
      { id: 'gm1', type: 'goldMine', row: 17, col: 17, level: 2 },
    ],
    resources: { food: 3000, gold: 2500, oil: 200 },
  },
  {
    username: 'commander_chen',
    email: 'chen@test.com',
    buildings: [
      { id: 'tc1', type: 'townCenter', row: 8, col: 8, level: 1 },
      { id: 'f1', type: 'farm', row: 6, col: 6, level: 1 },
      { id: 'gm1', type: 'goldMine', row: 6, col: 10, level: 1 },
      { id: 'h1', type: 'house', row: 10, col: 6, level: 1 },
    ],
    resources: { food: 800, gold: 900, oil: 0 },
  },
  {
    username: 'defender_diana',
    email: 'diana@test.com',
    buildings: [
      { id: 'tc1', type: 'townCenter', row: 12, col: 12, level: 2 },
      { id: 'f1', type: 'farm', row: 10, col: 10, level: 1 },
      { id: 'f2', type: 'farm', row: 10, col: 14, level: 1 },
      { id: 'f3', type: 'farm', row: 14, col: 10, level: 1 },
      { id: 'gm1', type: 'goldMine', row: 14, col: 14, level: 2 },
      { id: 'ow1', type: 'oilWell', row: 16, col: 12, level: 1 },
    ],
    resources: { food: 5000, gold: 4000, oil: 500 },
  },
];

async function seed() {
  console.log('Connecting to MongoDB...');
  await mongoose.connect(MONGODB_URI);
  console.log('Connected!');

  console.log('\nSeeding test players...');

  for (const player of testPlayers) {
    // Check if user already exists
    const existing = await User.findOne({ username: player.username });
    if (existing) {
      console.log(`  - ${player.username} already exists, skipping`);
      continue;
    }

    // Create user
    const user = await User.create({
      username: player.username,
      email: player.email,
      passwordHash: 'test_hash_' + player.username,
    });

    // Create base
    await Base.create({
      owner: user._id,
      resources: player.resources,
      buildings: player.buildings,
    });

    console.log(`  + Created ${player.username} with ${player.buildings.length} buildings`);
  }

  // Show summary
  const userCount = await User.countDocuments();
  const baseCount = await Base.countDocuments();
  console.log(`\nDatabase now has ${userCount} users and ${baseCount} bases`);

  await mongoose.disconnect();
  console.log('Done!');
}

seed().catch((err) => {
  console.error('Seed failed:', err);
  process.exit(1);
});
