/**
 * OpenCivilizations - Main Entry Point
 */

import Phaser from 'phaser';
import { MainMap } from './game/scenes/MainMap';
import { Battle } from './game/scenes/Battle';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  parent: 'game-container',
  width: window.innerWidth,
  height: window.innerHeight,
  backgroundColor: '#0f0f23',
  scene: [MainMap, Battle],
  scale: {
    mode: Phaser.Scale.RESIZE,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
};

// Create the game instance
const game = new Phaser.Game(config);

// Export for potential external access
export { game };
