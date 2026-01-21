/**
 * Tests for MatchmakingService
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { User } from '../src/models/User';
import { Base } from '../src/models/Base';
import { findOpponent, applyShield, hasActiveShield } from '../src/mechanics/MatchmakingService';

let mongoServer: MongoMemoryServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  await mongoose.connect(mongoServer.getUri());
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

beforeEach(async () => {
  // Clear database before each test
  await User.deleteMany({});
  await Base.deleteMany({});
});

describe('MatchmakingService', () => {
  describe('findOpponent', () => {
    it('should not match a player against themselves', async () => {
      // Create a user with a base
      const user = await User.create({
        username: 'player1',
        email: 'player1@test.com',
        passwordHash: 'hash123',
      });

      await Base.create({
        owner: user._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [{ id: 'b1', type: 'house', row: 5, col: 5, level: 1 }],
      });

      // Try to find opponent (should fail since only one player exists)
      const result = await findOpponent(user._id.toString());

      expect(result.success).toBe(false);
      expect(result.error).toBe('No opponents available');
    });

    it('should find a valid opponent', async () => {
      // Create attacker
      const attacker = await User.create({
        username: 'attacker',
        email: 'attacker@test.com',
        passwordHash: 'hash123',
      });

      await Base.create({
        owner: attacker._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [{ id: 'b1', type: 'house', row: 5, col: 5, level: 1 }],
      });

      // Create defender
      const defender = await User.create({
        username: 'defender',
        email: 'defender@test.com',
        passwordHash: 'hash456',
      });

      await Base.create({
        owner: defender._id,
        resources: { food: 1000, gold: 1000, oil: 100 },
        buildings: [
          { id: 'b2', type: 'townCenter', row: 10, col: 10, level: 2 },
          { id: 'b3', type: 'farm', row: 8, col: 8, level: 1 },
        ],
      });

      // Find opponent for attacker
      const result = await findOpponent(attacker._id.toString());

      expect(result.success).toBe(true);
      expect(result.opponent).toBeDefined();
      expect(result.opponent!.odId).toBe(defender._id.toString());
      expect(result.opponent!.username).toBe('defender');
      expect(result.opponent!.base).toHaveLength(2);
    });

    it('should not match against shielded players', async () => {
      // Create attacker
      const attacker = await User.create({
        username: 'attacker',
        email: 'attacker@test.com',
        passwordHash: 'hash123',
      });

      await Base.create({
        owner: attacker._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [{ id: 'b1', type: 'house', row: 5, col: 5, level: 1 }],
      });

      // Create shielded defender
      const defender = await User.create({
        username: 'shielded',
        email: 'shielded@test.com',
        passwordHash: 'hash456',
      });

      const futureDate = new Date();
      futureDate.setHours(futureDate.getHours() + 12); // Shield for 12 hours

      await Base.create({
        owner: defender._id,
        resources: { food: 1000, gold: 1000, oil: 100 },
        buildings: [{ id: 'b2', type: 'townCenter', row: 10, col: 10, level: 2 }],
        shieldUntil: futureDate,
      });

      // Try to find opponent (should fail - defender is shielded)
      const result = await findOpponent(attacker._id.toString());

      expect(result.success).toBe(false);
      expect(result.error).toBe('No opponents available');
    });

    it('should match against players with expired shields', async () => {
      // Create attacker
      const attacker = await User.create({
        username: 'attacker',
        email: 'attacker@test.com',
        passwordHash: 'hash123',
      });

      await Base.create({
        owner: attacker._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [{ id: 'b1', type: 'house', row: 5, col: 5, level: 1 }],
      });

      // Create defender with expired shield
      const defender = await User.create({
        username: 'unshielded',
        email: 'unshielded@test.com',
        passwordHash: 'hash456',
      });

      const pastDate = new Date();
      pastDate.setHours(pastDate.getHours() - 1); // Shield expired 1 hour ago

      await Base.create({
        owner: defender._id,
        resources: { food: 1000, gold: 1000, oil: 100 },
        buildings: [{ id: 'b2', type: 'townCenter', row: 10, col: 10, level: 2 }],
        shieldUntil: pastDate,
      });

      // Find opponent (should succeed - shield expired)
      const result = await findOpponent(attacker._id.toString());

      expect(result.success).toBe(true);
      expect(result.opponent).toBeDefined();
      expect(result.opponent!.username).toBe('unshielded');
    });

    it('should not match against players with no buildings', async () => {
      // Create attacker
      const attacker = await User.create({
        username: 'attacker',
        email: 'attacker@test.com',
        passwordHash: 'hash123',
      });

      await Base.create({
        owner: attacker._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [{ id: 'b1', type: 'house', row: 5, col: 5, level: 1 }],
      });

      // Create defender with empty base
      const defender = await User.create({
        username: 'emptybase',
        email: 'emptybase@test.com',
        passwordHash: 'hash456',
      });

      await Base.create({
        owner: defender._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [], // No buildings
      });

      // Try to find opponent (should fail - no buildings)
      const result = await findOpponent(attacker._id.toString());

      expect(result.success).toBe(false);
      expect(result.error).toBe('No opponents available');
    });
  });

  describe('applyShield', () => {
    it('should apply a shield to a base', async () => {
      const user = await User.create({
        username: 'player',
        email: 'player@test.com',
        passwordHash: 'hash123',
      });

      const base = await Base.create({
        owner: user._id,
        resources: { food: 500, gold: 500, oil: 0 },
        buildings: [{ id: 'b1', type: 'house', row: 5, col: 5, level: 1 }],
      });

      const result = await applyShield(base._id.toString(), 12);

      expect(result).toBe(true);

      // Verify shield was applied
      const updatedBase = await Base.findById(base._id);
      expect(updatedBase?.shieldUntil).toBeDefined();
      expect(updatedBase?.lastAttacked).toBeDefined();

      // Shield should be approximately 12 hours in the future
      const now = new Date();
      const shieldEnd = updatedBase!.shieldUntil!;
      const hoursDiff = (shieldEnd.getTime() - now.getTime()) / (1000 * 60 * 60);
      expect(hoursDiff).toBeGreaterThan(11);
      expect(hoursDiff).toBeLessThan(13);
    });
  });

  describe('hasActiveShield', () => {
    it('should return true for active shield', () => {
      const futureDate = new Date();
      futureDate.setHours(futureDate.getHours() + 12);

      const base = {
        shieldUntil: futureDate,
      } as any;

      expect(hasActiveShield(base)).toBe(true);
    });

    it('should return false for expired shield', () => {
      const pastDate = new Date();
      pastDate.setHours(pastDate.getHours() - 1);

      const base = {
        shieldUntil: pastDate,
      } as any;

      expect(hasActiveShield(base)).toBe(false);
    });

    it('should return false for null shield', () => {
      const base = {
        shieldUntil: null,
      } as any;

      expect(hasActiveShield(base)).toBe(false);
    });
  });
});
