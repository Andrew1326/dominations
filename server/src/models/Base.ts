/**
 * Base Model - MongoDB schema for player's base (buildings, resources)
 */

import mongoose, { Schema, Document, Types } from 'mongoose';
import type { BuildingType, Resources } from '@shared/types';

// Building subdocument interface
export interface IBuilding {
  id: string;
  type: BuildingType;
  row: number;
  col: number;
  level: number;
  constructionStartedAt?: Date;
  constructionEndsAt?: Date;
}

// Base document interface
export interface IBase extends Document {
  owner: Types.ObjectId;
  age: string;
  nation: string | null;
  ageAdvanceStartedAt: Date | null;
  ageAdvanceEndsAt: Date | null;
  resources: Resources;
  resourcesLastUpdated: Date;
  buildings: IBuilding[];
  shieldUntil: Date | null;  // Protection from attacks until this time
  lastAttacked: Date | null; // When this base was last attacked
  createdAt: Date;
  updatedAt: Date;
}

const BuildingSchema = new Schema<IBuilding>({
  id: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    required: true,
    enum: [
      'townCenter', 'house', 'farm', 'goldMine', 'oilWell',
      'barracks', 'wall', 'tower', 'storage',
      'blacksmith', 'market', 'temple', 'library',
      'stable', 'castle', 'university', 'factory',
      'airfield', 'dataCentre',
    ],
  },
  row: {
    type: Number,
    required: true,
    min: 0,
  },
  col: {
    type: Number,
    required: true,
    min: 0,
  },
  level: {
    type: Number,
    required: true,
    default: 1,
    min: 1,
  },
  constructionStartedAt: {
    type: Date,
    default: null,
  },
  constructionEndsAt: {
    type: Date,
    default: null,
  },
});

const BaseSchema = new Schema<IBase>({
  owner: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true,
  },
  age: {
    type: String,
    default: 'stone',
    enum: [
      'stone', 'bronze', 'iron', 'classical', 'medieval',
      'gunpowder', 'enlightenment', 'industrial', 'modern', 'digital',
    ],
  },
  nation: {
    type: String,
    default: null,
    enum: [
      null, 'romans', 'greeks', 'egyptians', 'chinese',
      'japanese', 'vikings', 'british', 'persians',
    ],
  },
  ageAdvanceStartedAt: {
    type: Date,
    default: null,
  },
  ageAdvanceEndsAt: {
    type: Date,
    default: null,
  },
  resources: {
    food: {
      type: Number,
      default: 500,
      min: 0,
    },
    gold: {
      type: Number,
      default: 500,
      min: 0,
    },
    oil: {
      type: Number,
      default: 0,
      min: 0,
    },
  },
  resourcesLastUpdated: {
    type: Date,
    default: Date.now,
  },
  buildings: {
    type: [BuildingSchema],
    default: [],
  },
  shieldUntil: {
    type: Date,
    default: null,
  },
  lastAttacked: {
    type: Date,
    default: null,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Update the updatedAt timestamp before saving
BaseSchema.pre('save', function (next) {
  this.updatedAt = new Date();
  next();
});

// Note: unique: true on owner already creates an index

export const Base = mongoose.model<IBase>('Base', BaseSchema);
