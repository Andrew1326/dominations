/**
 * Tests for MongoDB models (User, Base)
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { User } from '../src/models/User';
import { Base } from '../src/models/Base';
import type { BuildingType } from '@shared/types';

let mongoServer: MongoMemoryServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  const mongoUri = mongoServer.getUri();
  await mongoose.connect(mongoUri);
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

beforeEach(async () => {
  // Clear all collections before each test
  await User.deleteMany({});
  await Base.deleteMany({});
});

describe('User Model', () => {
  it('creates a user with required fields', async () => {
    const user = new User({
      username: 'testuser',
      email: 'test@example.com',
      passwordHash: 'hashedpassword123',
    });
    await user.save();

    const found = await User.findOne({ username: 'testuser' });
    expect(found).not.toBeNull();
    expect(found!.email).toBe('test@example.com');
  });

  it('enforces unique username', async () => {
    const user1 = new User({
      username: 'uniqueuser',
      email: 'user1@example.com',
      passwordHash: 'hash1',
    });
    await user1.save();

    const user2 = new User({
      username: 'uniqueuser',
      email: 'user2@example.com',
      passwordHash: 'hash2',
    });

    await expect(user2.save()).rejects.toThrow();
  });

  it('enforces unique email', async () => {
    const user1 = new User({
      username: 'user1',
      email: 'same@example.com',
      passwordHash: 'hash1',
    });
    await user1.save();

    const user2 = new User({
      username: 'user2',
      email: 'same@example.com',
      passwordHash: 'hash2',
    });

    await expect(user2.save()).rejects.toThrow();
  });

  it('sets default createdAt and lastLogin', async () => {
    const before = new Date();
    const user = new User({
      username: 'dateuser',
      email: 'date@example.com',
      passwordHash: 'hash',
    });
    await user.save();
    const after = new Date();

    expect(user.createdAt.getTime()).toBeGreaterThanOrEqual(before.getTime());
    expect(user.createdAt.getTime()).toBeLessThanOrEqual(after.getTime());
    expect(user.lastLogin.getTime()).toBeGreaterThanOrEqual(before.getTime());
  });
});

describe('Base Model', () => {
  let testUser: mongoose.Document;

  beforeEach(async () => {
    // Create a test user for base ownership
    testUser = await new User({
      username: 'baseowner',
      email: 'owner@example.com',
      passwordHash: 'hash',
    }).save();
  });

  it('creates a base with default resources', async () => {
    const base = new Base({
      owner: testUser._id,
    });
    await base.save();

    expect(base.resources.food).toBe(500);
    expect(base.resources.gold).toBe(500);
    expect(base.resources.oil).toBe(0);
    expect(base.buildings).toHaveLength(0);
  });

  it('stores buildings with correct fields', async () => {
    const base = new Base({
      owner: testUser._id,
      buildings: [
        {
          id: 'tc_1',
          type: 'townCenter' as BuildingType,
          row: 5,
          col: 5,
          level: 1,
        },
        {
          id: 'farm_1',
          type: 'farm' as BuildingType,
          row: 10,
          col: 10,
          level: 2,
        },
      ],
    });
    await base.save();

    const found = await Base.findOne({ owner: testUser._id });
    expect(found!.buildings).toHaveLength(2);
    expect(found!.buildings[0].type).toBe('townCenter');
    expect(found!.buildings[0].level).toBe(1);
    expect(found!.buildings[1].type).toBe('farm');
    expect(found!.buildings[1].level).toBe(2);
  });

  it('enforces unique owner (one base per user)', async () => {
    const base1 = new Base({ owner: testUser._id });
    await base1.save();

    const base2 = new Base({ owner: testUser._id });
    await expect(base2.save()).rejects.toThrow();
  });

  it('updates resources correctly', async () => {
    const base = new Base({
      owner: testUser._id,
      resources: { food: 100, gold: 100, oil: 0 },
    });
    await base.save();

    base.resources.food = 200;
    base.resources.gold = 150;
    await base.save();

    const found = await Base.findOne({ owner: testUser._id });
    expect(found!.resources.food).toBe(200);
    expect(found!.resources.gold).toBe(150);
  });

  it('validates building type enum', async () => {
    const base = new Base({
      owner: testUser._id,
      buildings: [
        {
          id: 'invalid_1',
          type: 'invalidType' as BuildingType, // Invalid type
          row: 0,
          col: 0,
          level: 1,
        },
      ],
    });

    await expect(base.save()).rejects.toThrow();
  });

  it('stores construction timestamps', async () => {
    const now = new Date();
    const endsAt = new Date(now.getTime() + 60000); // 1 minute later

    const base = new Base({
      owner: testUser._id,
      buildings: [
        {
          id: 'building_1',
          type: 'house' as BuildingType,
          row: 0,
          col: 0,
          level: 1,
          constructionStartedAt: now,
          constructionEndsAt: endsAt,
        },
      ],
    });
    await base.save();

    const found = await Base.findOne({ owner: testUser._id });
    expect(found!.buildings[0].constructionStartedAt).toEqual(now);
    expect(found!.buildings[0].constructionEndsAt).toEqual(endsAt);
  });
});
