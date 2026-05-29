/**
 * Building - Base class for all building entities.
 *
 * Renders the building's sprite when a render exists for its type, otherwise
 * falls back to a colored isometric diamond. Implemented as a Container so the
 * sprite and the diamond fallback share one positioned, depth-sortable object.
 */

import Phaser from 'phaser';
import type { BuildingType, BuildingData, BuildingDefinition } from '@shared/types';
import { BUILDINGS, TILE_WIDTH_HALF, TILE_HEIGHT_HALF } from '@shared/constants';
import { getBuildingTexture } from '../ui/buildingCatalog';

/**
 * Sprite alignment calibration.
 *
 * The sprites are building-only renders (no baked ground or shadow), cropped
 * tight and centred on a square with a uniform margin, so the building is
 * horizontally centred and its base sits at ~SPRITE_BASE_Y down the image.
 *
 * We anchor that base point at the footprint's front (south) vertex so the
 * building's base diamond covers the selected tiles, and scale the sprite so
 * its width roughly matches the footprint's isometric width.
 */
const SPRITE_FOOTPRINT_FACTOR = 1.3; // display width as a multiple of isoWidth (visual overhang)
const WALL_FOOTPRINT_FACTOR = 1.15;  // fences just abut along a run (touch end-to-end without heavy overlap, so the line stays even)
const SPRITE_BASE_Y = 0.92;          // building base position within the cropped image

function isoWidthOf(def: BuildingDefinition): number {
  return (def.width + def.height) * TILE_WIDTH_HALF;
}

function isoHeightOf(def: BuildingDefinition): number {
  return (def.width + def.height) * TILE_HEIGHT_HALF;
}

/**
 * Width factor for a building's sprite. Fences (allowAdjacent) are kept tight
 * to the footprint so neighbouring walls abut instead of overlapping; other
 * buildings get a slight overhang for visual heft.
 */
function footprintFactor(def: BuildingDefinition): number {
  return def.allowAdjacent ? WALL_FOOTPRINT_FACTOR : SPRITE_FOOTPRINT_FACTOR;
}

/**
 * Place and scale a building sprite within its container so its base sits on
 * the footprint's front vertex (and thus its base diamond covers the tiles).
 */
function placeSprite(sprite: Phaser.GameObjects.Image, def: BuildingDefinition): void {
  sprite.setOrigin(0.5, SPRITE_BASE_Y);
  sprite.setScale((isoWidthOf(def) * footprintFactor(def)) / sprite.width);
  sprite.y = isoHeightOf(def) / 2; // footprint's front (south) vertex in container space
}

export class Building extends Phaser.GameObjects.Container {
  public readonly buildingType: BuildingType;
  public readonly definition: BuildingDefinition;
  public gridRow: number;
  public gridCol: number;
  public readonly buildingId: string;
  public level: number;
  private sprite: Phaser.GameObjects.Image | null = null;

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
    super(scene, screenX, screenY);

    this.buildingType = buildingType;
    this.definition = BUILDINGS[buildingType];
    this.gridRow = gridRow;
    this.gridCol = gridCol;
    this.buildingId = id || `${buildingType}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.level = level;

    this.buildVisual();

    scene.add.existing(this);
  }

  /**
   * Add the sprite if its texture is loaded, otherwise draw the diamond.
   */
  private buildVisual(): void {
    const texture = getBuildingTexture(this.buildingType);

    if (texture && this.scene.textures.exists(texture.key)) {
      this.sprite = this.scene.add.image(0, 0, texture.key);
      placeSprite(this.sprite, this.definition);
      this.add(this.sprite);
    } else {
      const graphics = this.scene.add.graphics();
      drawDiamond(graphics, this.definition, this.definition.color, 1);
      this.add(graphics);
    }
  }

  /**
   * Swap the sprite texture (used for wall autotiling) and re-fit it to the
   * footprint. No-op if the texture isn't loaded or this building has no sprite.
   */
  setSpriteTexture(key: string): void {
    if (!this.sprite || !this.scene.textures.exists(key)) return;
    if (this.sprite.texture.key === key) return;
    this.sprite.setTexture(key);
    placeSprite(this.sprite, this.definition);
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
 * Draw an isometric diamond for a building footprint into a graphics object.
 */
function drawDiamond(
  graphics: Phaser.GameObjects.Graphics,
  definition: BuildingDefinition,
  color: number,
  alpha: number
): void {
  graphics.clear();

  const isoWidth = (definition.width + definition.height) * TILE_WIDTH_HALF;
  const isoHeight = (definition.width + definition.height) * TILE_HEIGHT_HALF;

  graphics.fillStyle(color, alpha);
  graphics.beginPath();
  graphics.moveTo(0, -isoHeight / 2);
  graphics.lineTo(isoWidth / 2, 0);
  graphics.lineTo(0, isoHeight / 2);
  graphics.lineTo(-isoWidth / 2, 0);
  graphics.closePath();
  graphics.fillPath();

  graphics.lineStyle(2, 0x000000, alpha);
  graphics.beginPath();
  graphics.moveTo(0, -isoHeight / 2);
  graphics.lineTo(isoWidth / 2, 0);
  graphics.lineTo(0, isoHeight / 2);
  graphics.lineTo(-isoWidth / 2, 0);
  graphics.closePath();
  graphics.strokePath();
}

/**
 * Ghost Building - Preview for placement.
 *
 * Shows a validity-tinted footprint diamond plus, when a render exists, a
 * translucent sprite of the building being placed.
 */
export class GhostBuilding extends Phaser.GameObjects.Container {
  public definition: BuildingDefinition;
  private footprint: Phaser.GameObjects.Graphics;
  private sprite: Phaser.GameObjects.Image | null = null;

  constructor(scene: Phaser.Scene, buildingType: BuildingType) {
    super(scene);
    this.definition = BUILDINGS[buildingType];

    this.footprint = scene.add.graphics();
    this.add(this.footprint);

    const texture = getBuildingTexture(buildingType);
    if (texture && scene.textures.exists(texture.key)) {
      this.sprite = scene.add.image(0, 0, texture.key);
      placeSprite(this.sprite, this.definition);
      this.sprite.setAlpha(0.6);
      this.add(this.sprite);
    }

    this.setVisible(false);
    scene.add.existing(this);
  }

  /**
   * Update ghost position and validity state
   */
  update(screenX: number, screenY: number, isValid: boolean): void {
    this.setPosition(screenX, screenY);
    this.setVisible(true);

    const color = isValid ? 0x00ff00 : 0xff0000;
    drawDiamond(this.footprint, this.definition, color, 0.5);
    this.sprite?.setTint(isValid ? 0xffffff : 0xff8888);
  }

  /**
   * Hide the ghost
   */
  hide(): void {
    this.setVisible(false);
  }
}
