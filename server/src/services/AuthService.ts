/**
 * AuthService - Simple authentication for MVP
 *
 * For production, this should use proper password hashing (bcrypt),
 * JWT tokens, and more robust session management.
 */

import { User, IUser } from '../models/User';
import { Base, IBase } from '../models/Base';
import { STARTING_RESOURCES } from '@shared/constants';
import crypto from 'crypto';

export interface AuthResult {
  success: boolean;
  user?: IUser;
  base?: IBase;
  error?: string;
}

/**
 * Simple hash function for MVP (use bcrypt in production)
 */
function hashPassword(password: string): string {
  return crypto.createHash('sha256').update(password).digest('hex');
}

/**
 * Register a new user
 */
export async function registerUser(
  username: string,
  email: string,
  password: string
): Promise<AuthResult> {
  try {
    // Check if username already exists
    const existingUsername = await User.findOne({ username });
    if (existingUsername) {
      return { success: false, error: 'Username already taken' };
    }

    // Check if email already exists
    const existingEmail = await User.findOne({ email });
    if (existingEmail) {
      return { success: false, error: 'Email already registered' };
    }

    // Create user
    const user = new User({
      username,
      email,
      passwordHash: hashPassword(password),
    });
    await user.save();

    // Create initial base for user
    const base = new Base({
      owner: user._id,
      resources: { ...STARTING_RESOURCES },
      buildings: [],
    });
    await base.save();

    return { success: true, user, base };
  } catch (error) {
    console.error('Registration error:', error);
    return { success: false, error: 'Registration failed' };
  }
}

/**
 * Login user
 */
export async function loginUser(
  usernameOrEmail: string,
  password: string
): Promise<AuthResult> {
  try {
    // Find user by username or email
    const user = await User.findOne({
      $or: [{ username: usernameOrEmail }, { email: usernameOrEmail }],
    });

    if (!user) {
      return { success: false, error: 'User not found' };
    }

    // Verify password
    if (user.passwordHash !== hashPassword(password)) {
      return { success: false, error: 'Invalid password' };
    }

    // Update last login
    user.lastLogin = new Date();
    await user.save();

    // Load user's base
    const base = await Base.findOne({ owner: user._id });
    if (!base) {
      return { success: false, error: 'Base not found' };
    }

    return { success: true, user, base };
  } catch (error) {
    console.error('Login error:', error);
    return { success: false, error: 'Login failed' };
  }
}

/**
 * Get or create guest user (for development/testing)
 */
export async function getOrCreateGuestUser(guestId: string): Promise<AuthResult> {
  try {
    const guestUsername = `guest_${guestId}`;
    const guestEmail = `${guestUsername}@guest.local`;

    // Try to find existing guest
    let user = await User.findOne({ username: guestUsername });
    let base: IBase | null = null;

    if (user) {
      // Load existing base
      base = await Base.findOne({ owner: user._id });
      user.lastLogin = new Date();
      await user.save();
    } else {
      // Create new guest user
      user = new User({
        username: guestUsername,
        email: guestEmail,
        passwordHash: hashPassword(guestId), // Guest uses their ID as password
      });
      await user.save();

      // Create initial base
      base = new Base({
        owner: user._id,
        resources: { ...STARTING_RESOURCES },
        buildings: [],
      });
      await base.save();
    }

    if (!base) {
      return { success: false, error: 'Failed to load base' };
    }

    return { success: true, user, base };
  } catch (error) {
    console.error('Guest user error:', error);
    return { success: false, error: 'Failed to create guest user' };
  }
}

/**
 * Load user's base by user ID
 */
export async function loadUserBase(userId: string): Promise<IBase | null> {
  try {
    return await Base.findOne({ owner: userId });
  } catch (error) {
    console.error('Load base error:', error);
    return null;
  }
}

/**
 * Save user's base
 */
export async function saveUserBase(base: IBase): Promise<boolean> {
  try {
    await base.save();
    return true;
  } catch (error) {
    console.error('Save base error:', error);
    return false;
  }
}
