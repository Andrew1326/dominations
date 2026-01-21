/**
 * Tests for AuthService
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { User } from '../src/models/User';
import { Base } from '../src/models/Base';
import {
  registerUser,
  loginUser,
  getOrCreateGuestUser,
} from '../src/services/AuthService';

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
  await User.deleteMany({});
  await Base.deleteMany({});
});

describe('AuthService', () => {
  describe('registerUser', () => {
    it('registers a new user successfully', async () => {
      const result = await registerUser('newuser', 'new@example.com', 'password123');

      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user!.username).toBe('newuser');
      expect(result.base).toBeDefined();
      expect(result.base!.resources.food).toBe(500);
      expect(result.base!.resources.gold).toBe(500);
    });

    it('fails when username is taken', async () => {
      await registerUser('existinguser', 'user1@example.com', 'pass1');
      const result = await registerUser('existinguser', 'user2@example.com', 'pass2');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Username already taken');
    });

    it('fails when email is taken', async () => {
      await registerUser('user1', 'same@example.com', 'pass1');
      const result = await registerUser('user2', 'same@example.com', 'pass2');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Email already registered');
    });

    it('creates a base with starting resources for new user', async () => {
      const result = await registerUser('resourceuser', 'res@example.com', 'pass');

      expect(result.base!.resources.food).toBe(500);
      expect(result.base!.resources.gold).toBe(500);
      expect(result.base!.resources.oil).toBe(0);
      expect(result.base!.buildings).toHaveLength(0);
    });
  });

  describe('loginUser', () => {
    beforeEach(async () => {
      await registerUser('loginuser', 'login@example.com', 'correctpassword');
    });

    it('logs in with correct username and password', async () => {
      const result = await loginUser('loginuser', 'correctpassword');

      expect(result.success).toBe(true);
      expect(result.user!.username).toBe('loginuser');
      expect(result.base).toBeDefined();
    });

    it('logs in with email instead of username', async () => {
      const result = await loginUser('login@example.com', 'correctpassword');

      expect(result.success).toBe(true);
      expect(result.user!.username).toBe('loginuser');
    });

    it('fails with wrong password', async () => {
      const result = await loginUser('loginuser', 'wrongpassword');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid password');
    });

    it('fails with non-existent user', async () => {
      const result = await loginUser('nonexistent', 'anypassword');

      expect(result.success).toBe(false);
      expect(result.error).toBe('User not found');
    });

    it('updates lastLogin on successful login', async () => {
      const before = new Date();
      await new Promise((resolve) => setTimeout(resolve, 10)); // Small delay

      await loginUser('loginuser', 'correctpassword');

      const user = await User.findOne({ username: 'loginuser' });
      expect(user!.lastLogin.getTime()).toBeGreaterThan(before.getTime());
    });
  });

  describe('getOrCreateGuestUser', () => {
    it('creates a new guest user', async () => {
      const result = await getOrCreateGuestUser('test_guest_123');

      expect(result.success).toBe(true);
      expect(result.user!.username).toBe('guest_test_guest_123');
      expect(result.base).toBeDefined();
    });

    it('returns existing guest user on second call', async () => {
      const result1 = await getOrCreateGuestUser('returning_guest');
      const result2 = await getOrCreateGuestUser('returning_guest');

      expect(result1.success).toBe(true);
      expect(result2.success).toBe(true);
      expect(result1.user!._id.toString()).toBe(result2.user!._id.toString());
    });

    it('preserves guest base data between sessions', async () => {
      // Create guest and modify their base
      const result1 = await getOrCreateGuestUser('persistent_guest');
      result1.base!.resources.gold = 1000;
      await result1.base!.save();

      // Get guest again
      const result2 = await getOrCreateGuestUser('persistent_guest');

      expect(result2.base!.resources.gold).toBe(1000);
    });
  });
});
