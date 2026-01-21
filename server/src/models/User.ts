/**
 * User Model - MongoDB schema for player accounts
 */

import mongoose, { Schema, Document } from 'mongoose';

export interface IUser extends Document {
  username: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
  lastLogin: Date;
}

const UserSchema = new Schema<IUser>({
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    minlength: 3,
    maxlength: 30, // Increased to accommodate guest usernames
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
  },
  passwordHash: {
    type: String,
    required: true,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  lastLogin: {
    type: Date,
    default: Date.now,
  },
});

// Note: unique: true already creates indexes for username and email

export const User = mongoose.model<IUser>('User', UserSchema);
