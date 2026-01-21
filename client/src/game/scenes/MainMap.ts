/**
 * MainMap Scene - Primary game scene for base building
 */

import Phaser from 'phaser';
import { GridSystem } from '../systems/GridSystem';
import { Building, GhostBuilding } from '../entities/Building';
import type { BuildingType, BuildingData, BaseLayout } from '@shared/types';
import {
  GRID_SIZE,
  TILE_WIDTH_HALF,
  TILE_HEIGHT_HALF,
  GRID_LINE_COLOR,
  GRID_FILL_COLOR,
  BUILDINGS,
  STORAGE_KEY,
} from '@shared/constants';

export class MainMap extends Phaser.Scene {
  private gridSystem!: GridSystem;
  private gridGraphics!: Phaser.GameObjects.Graphics;
  private buildings: Building[] = [];
  private ghostBuilding: GhostBuilding | null = null;
  private selectedBuildingType: BuildingType | null = null;
  private lastValidPosition: { row: number; col: number; valid: boolean } | null = null;

  constructor() {
    super({ key: 'MainMap' });
  }

  create(): void {
    // Calculate grid origin (center of screen, offset for isometric view)
    const originX = this.cameras.main.width / 2;
    const originY = 100; // Top padding

    // Initialize grid system
    this.gridSystem = new GridSystem(originX, originY);

    // Draw the grid
    this.drawGrid();

    // Setup input handlers
    this.setupInput();

    // Setup UI button handlers
    this.setupUIButtons();

    // Load saved layout
    this.loadLayout();
  }

  /**
   * Draw the isometric grid
   */
  private drawGrid(): void {
    this.gridGraphics = this.add.graphics();

    // Draw filled grid background
    this.gridGraphics.fillStyle(GRID_FILL_COLOR, 0.3);

    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        const pos = this.gridSystem.gridToScreen(row, col);
        this.drawTile(pos.x, pos.y, GRID_FILL_COLOR, 0.3);
      }
    }

    // Draw grid lines
    this.gridGraphics.lineStyle(1, GRID_LINE_COLOR, 0.5);

    for (let row = 0; row <= GRID_SIZE; row++) {
      const start = this.gridSystem.gridToScreen(row, 0);
      const end = this.gridSystem.gridToScreen(row, GRID_SIZE);
      this.gridGraphics.lineBetween(start.x, start.y, end.x, end.y);
    }

    for (let col = 0; col <= GRID_SIZE; col++) {
      const start = this.gridSystem.gridToScreen(0, col);
      const end = this.gridSystem.gridToScreen(GRID_SIZE, col);
      this.gridGraphics.lineBetween(start.x, start.y, end.x, end.y);
    }
  }

  /**
   * Draw a single isometric tile
   */
  private drawTile(x: number, y: number, color: number, alpha: number): void {
    this.gridGraphics.fillStyle(color, alpha);
    this.gridGraphics.beginPath();
    this.gridGraphics.moveTo(x, y - TILE_HEIGHT_HALF);
    this.gridGraphics.lineTo(x + TILE_WIDTH_HALF, y);
    this.gridGraphics.lineTo(x, y + TILE_HEIGHT_HALF);
    this.gridGraphics.lineTo(x - TILE_WIDTH_HALF, y);
    this.gridGraphics.closePath();
    this.gridGraphics.fillPath();
  }

  /**
   * Setup mouse/touch input handlers
   */
  private setupInput(): void {
    // Pointer move - update ghost building position
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (!this.selectedBuildingType || !this.ghostBuilding) return;

      const gridPos = this.gridSystem.screenToGrid(pointer.x, pointer.y);
      const def = BUILDINGS[this.selectedBuildingType];

      // Check if placement is valid
      const isValid = this.gridSystem.canPlace(
        gridPos.row,
        gridPos.col,
        def.width,
        def.height
      );

      // Get screen position for the building center
      const centerRow = gridPos.row + def.height / 2;
      const centerCol = gridPos.col + def.width / 2;
      const screenPos = this.gridSystem.gridToScreen(centerRow, centerCol);

      // Update ghost building
      this.ghostBuilding.update(screenPos.x, screenPos.y, isValid);
      this.lastValidPosition = { row: gridPos.row, col: gridPos.col, valid: isValid };
    });

    // Pointer down - place building
    this.input.on('pointerdown', () => {
      if (!this.selectedBuildingType || !this.lastValidPosition) return;
      if (!this.lastValidPosition.valid) return;

      this.placeBuilding(
        this.selectedBuildingType,
        this.lastValidPosition.row,
        this.lastValidPosition.col
      );
    });
  }

  /**
   * Setup UI button handlers
   */
  private setupUIButtons(): void {
    const buttons = document.querySelectorAll('.building-btn');

    buttons.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const buildingType = target.dataset.building as BuildingType;

        // Update selection state
        buttons.forEach((b) => b.classList.remove('selected'));
        target.classList.add('selected');

        this.selectBuildingType(buildingType);
      });
    });
  }

  /**
   * Select a building type for placement
   */
  private selectBuildingType(type: BuildingType): void {
    this.selectedBuildingType = type;

    // Remove existing ghost
    if (this.ghostBuilding) {
      this.ghostBuilding.destroy();
    }

    // Create new ghost building
    this.ghostBuilding = new GhostBuilding(this, type);
  }

  /**
   * Place a building on the grid
   */
  private placeBuilding(type: BuildingType, row: number, col: number): void {
    const def = BUILDINGS[type];

    // Double-check placement is valid
    if (!this.gridSystem.canPlace(row, col, def.width, def.height)) {
      return;
    }

    // Mark grid as occupied
    this.gridSystem.occupy(row, col, def.width, def.height);

    // Calculate screen position
    const centerRow = row + def.height / 2;
    const centerCol = col + def.width / 2;
    const screenPos = this.gridSystem.gridToScreen(centerRow, centerCol);

    // Create building
    const building = new Building(this, type, row, col, screenPos.x, screenPos.y);

    // Sort by depth for correct rendering
    building.setDepth(row + col);

    this.buildings.push(building);

    // Save layout
    this.saveLayout();
  }

  /**
   * Save current layout to localStorage
   */
  private saveLayout(): void {
    const layout: BaseLayout = {
      buildings: this.buildings.map((b) => b.toData()),
      lastSaved: Date.now(),
    };

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
    } catch (e) {
      console.error('Failed to save layout:', e);
    }
  }

  /**
   * Load layout from localStorage
   */
  private loadLayout(): void {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) return;

      const layout: BaseLayout = JSON.parse(saved);

      // Restore buildings
      layout.buildings.forEach((data: BuildingData) => {
        const def = BUILDINGS[data.type];

        // Mark grid as occupied
        this.gridSystem.occupy(data.row, data.col, def.width, def.height);

        // Calculate screen position
        const centerRow = data.row + def.height / 2;
        const centerCol = data.col + def.width / 2;
        const screenPos = this.gridSystem.gridToScreen(centerRow, centerCol);

        // Create building
        const building = new Building(
          this,
          data.type,
          data.row,
          data.col,
          screenPos.x,
          screenPos.y,
          data.id
        );

        building.setDepth(data.row + data.col);
        this.buildings.push(building);
      });

      console.log(`Loaded ${layout.buildings.length} buildings from storage`);
    } catch (e) {
      console.error('Failed to load layout:', e);
    }
  }

  /**
   * Clear all buildings (for testing/reset)
   */
  public clearAllBuildings(): void {
    this.buildings.forEach((b) => b.destroy());
    this.buildings = [];
    this.gridSystem.clearAll();
    localStorage.removeItem(STORAGE_KEY);
  }

  /**
   * Get all buildings (for testing)
   */
  public getBuildings(): Building[] {
    return this.buildings;
  }

  /**
   * Get grid system (for testing)
   */
  public getGridSystem(): GridSystem {
    return this.gridSystem;
  }
}
