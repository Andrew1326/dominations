/**
 * Building - Base class for all building entities
 */

import Phaser from 'phaser';
import type { BuildingType, BuildingData, BuildingDefinition } from '@shared/types';
import { BUILDINGS, TILE_WIDTH_HALF, TILE_HEIGHT_HALF } from '@shared/constants';

export class Building extends Phaser.GameObjects.Graphics {
  public readonly buildingType: BuildingType;
  public readonly definition: BuildingDefinition;
  public gridRow: number;
  public gridCol: number;
  public readonly buildingId: string;
  public level: number;

  constructor(
    scene: Phaser.Scene,
    buildingType: BuildingType,
    gridRow: number,
    gridCol: number,
    screenX: number,
    screenY: number,
    id?: string,
    level: number = 1
  ) {
    super(scene);

    this.buildingType = buildingType;
    this.definition = BUILDINGS[buildingType];
    this.gridRow = gridRow;
    this.gridCol = gridCol;
    this.buildingId = id || `${buildingType}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.level = level;

    // Position at screen coordinates
    this.setPosition(screenX, screenY);

    // Draw the building shape
    this.drawBuilding(this.definition.color, 1);

    // Add to scene
    scene.add.existing(this);
  }

  /**
   * Draw the isometric building shape
   */
  drawBuilding(color: number, alpha: number): void {
    this.clear();

    const width = this.definition.width;
    const height = this.definition.height;

    // Calculate isometric diamond dimensions
    const isoWidth = (width + height) * TILE_WIDTH_HALF;
    const isoHeight = (width + height) * TILE_HEIGHT_HALF;

    // Draw filled isometric rectangle (diamond shape)
    this.fillStyle(color, alpha);
    this.beginPath();

    // Top point
    this.moveTo(0, -isoHeight / 2);
    // Right point
    this.lineTo(isoWidth / 2, 0);
    // Bottom point
    this.lineTo(0, isoHeight / 2);
    // Left point
    this.lineTo(-isoWidth / 2, 0);

    this.closePath();
    this.fillPath();

    // Draw outline
    this.lineStyle(2, 0x000000, alpha);
    this.beginPath();
    this.moveTo(0, -isoHeight / 2);
    this.lineTo(isoWidth / 2, 0);
    this.lineTo(0, isoHeight / 2);
    this.lineTo(-isoWidth / 2, 0);
    this.closePath();
    this.strokePath();
  }

  /**
   * Convert this building to data for serialization
   */
  toData(): BuildingData {
    return {
      id: this.buildingId,
      type: this.buildingType,
      row: this.gridRow,
      col: this.gridCol,
      level: this.level,
    };
  }

  /**
   * Update the building position
   */
  updatePosition(screenX: number, screenY: number, gridRow: number, gridCol: number): void {
    this.setPosition(screenX, screenY);
    this.gridRow = gridRow;
    this.gridCol = gridCol;
  }
}

/**
 * Ghost Building - Preview for placement
 */
export class GhostBuilding extends Phaser.GameObjects.Graphics {
  public readonly definition: BuildingDefinition;

  constructor(scene: Phaser.Scene, buildingType: BuildingType) {
    super(scene);
    this.definition = BUILDINGS[buildingType];
    this.setVisible(false);
    scene.add.existing(this);
  }

  /**
   * Update ghost position and validity state
   */
  update(screenX: number, screenY: number, isValid: boolean): void {
    this.setPosition(screenX, screenY);
    this.setVisible(true);
    this.drawGhost(isValid);
  }

  /**
   * Draw the ghost building with validity indication
   */
  private drawGhost(isValid: boolean): void {
    this.clear();

    const width = this.definition.width;
    const height = this.definition.height;

    const isoWidth = (width + height) * TILE_WIDTH_HALF;
    const isoHeight = (width + height) * TILE_HEIGHT_HALF;

    const color = isValid ? 0x00FF00 : 0xFF0000;
    const alpha = 0.5;

    // Draw filled shape
    this.fillStyle(color, alpha);
    this.beginPath();
    this.moveTo(0, -isoHeight / 2);
    this.lineTo(isoWidth / 2, 0);
    this.lineTo(0, isoHeight / 2);
    this.lineTo(-isoWidth / 2, 0);
    this.closePath();
    this.fillPath();

    // Draw outline
    this.lineStyle(2, color, 0.8);
    this.beginPath();
    this.moveTo(0, -isoHeight / 2);
    this.lineTo(isoWidth / 2, 0);
    this.lineTo(0, isoHeight / 2);
    this.lineTo(-isoWidth / 2, 0);
    this.closePath();
    this.strokePath();
  }

  /**
   * Hide the ghost
   */
  hide(): void {
    this.setVisible(false);
  }

  /**
   * Change the building type
   */
  setBuildingType(buildingType: BuildingType): void {
    (this as { definition: BuildingDefinition }).definition = BUILDINGS[buildingType];
  }
}
