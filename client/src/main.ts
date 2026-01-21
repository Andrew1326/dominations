/**
 * OpenCivilizations - Main Entry Point
 */

import Phaser from 'phaser';
import { MainMap } from './game/scenes/MainMap';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  parent: 'game-container',
  width: 1280,
  height: 720,
  backgroundColor: '#0f0f23',
  scene: [MainMap],
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
};

// Create the game instance
const game = new Phaser.Game(config);

// Export for potential external access
export { game };
