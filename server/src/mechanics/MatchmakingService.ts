/**
 * MatchmakingService - Finds suitable opponents for players to attack
 *
 * Matchmaking rules:
 * - Cannot match against yourself
 * - Cannot match against players with active shields
 * - Players with at least one building are eligible
 * - Random selection from eligible opponents
 */

import { Base, IBase } from '../models/Base';
import { User, IUser } from '../models/User';
import { Types } from 'mongoose';
import type { BuildingData } from '@shared/types';

export interface MatchmakingResult {
  success: boolean;
  opponent?: {
    odId: string;
    username: string;
    base: BuildingData[];
  };
  error?: string;
}

/**
 * Find a suitable opponent for the given player
 */
export async function findOpponent(attackerId: string): Promise<MatchmakingResult> {
  try {
    const now = new Date();

    // Find eligible bases:
    // 1. Not owned by the attacker
    // 2. Not shielded (shieldUntil is null or in the past)
    // 3. Has at least one building
    const eligibleBases = await Base.find({
      owner: { $ne: new Types.ObjectId(attackerId) },
      $or: [
        { shieldUntil: null },
        { shieldUntil: { $lt: now } },
      ],
      'buildings.0': { $exists: true }, // Has at least one building
    }).limit(50); // Limit to prevent large queries

    if (eligibleBases.length === 0) {
      return {
        success: false,
        error: 'No opponents available',
      };
    }

    // Select a random opponent from eligible bases
    const randomIndex = Math.floor(Math.random() * eligibleBases.length);
    const opponentBase = eligibleBases[randomIndex];

    // Get opponent user info
    const opponentUser = await User.findById(opponentBase.owner);
    if (!opponentUser) {
      return {
        success: false,
        error: 'Opponent user not found',
      };
    }

    // Convert buildings to BuildingData format
    const buildingData: BuildingData[] = opponentBase.buildings.map((b) => ({
      id: b.id,
      type: b.type,
      row: b.row,
      col: b.col,
      level: b.level,
      constructionStartedAt: b.constructionStartedAt?.getTime(),
      constructionEndsAt: b.constructionEndsAt?.getTime(),
    }));

    return {
      success: true,
      opponent: {
        odId: opponentUser._id.toString(),
        username: opponentUser.username,
        base: buildingData,
      },
    };
  } catch (error) {
    console.error('Matchmaking error:', error);
    return {
      success: false,
      error: 'Matchmaking failed',
    };
  }
}

/**
 * Apply a shield to a base after being attacked
 * Default shield duration: 12 hours
 */
export async function applyShield(
  baseId: string,
  durationHours: number = 12
): Promise<boolean> {
  try {
    const shieldUntil = new Date();
    shieldUntil.setHours(shieldUntil.getHours() + durationHours);

    await Base.findByIdAndUpdate(baseId, {
      shieldUntil,
      lastAttacked: new Date(),
    });

    return true;
  } catch (error) {
    console.error('Failed to apply shield:', error);
    return false;
  }
}

/**
 * Check if a player is eligible to attack (not currently shielded themselves)
 * For future use when we implement shield mechanics fully
 */
export async function canAttack(attackerId: string): Promise<boolean> {
  // For now, anyone can attack
  // Future: check if attacker has troops, isn't in cooldown, etc.
  return true;
}

/**
 * Check if a base has an active shield
 */
export function hasActiveShield(base: IBase): boolean {
  if (!base.shieldUntil) return false;
  return base.shieldUntil > new Date();
}
