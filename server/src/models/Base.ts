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
  resources: Resources;
  resourcesLastUpdated: Date;
  buildings: IBuilding[];
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
    enum: ['townCenter', 'house', 'farm', 'goldMine', 'oilWell'],
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
