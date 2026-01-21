/**
 * Database connection module
 */

import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/opencivilizations';

export async function connectDatabase(): Promise<typeof mongoose> {
  try {
    const connection = await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB');
    return connection;
  } catch (error) {
    console.error('MongoDB connection error:', error);
    throw error;
  }
}

export async function disconnectDatabase(): Promise<void> {
  await mongoose.disconnect();
  console.log('Disconnected from MongoDB');
}
