/**
 * MainMap Scene - Primary game scene for base building
 *
 * Supports both online (server) and offline (localStorage) modes.
 * Server mode is primary; falls back to offline if unavailable.
 */

import Phaser from 'phaser';
import { GridSystem } from '../systems/GridSystem';
import { Building, GhostBuilding } from '../entities/Building';
import type { BuildingType, BuildingData, BaseLayout, Resources, MatchFoundMessage } from '@shared/types';
import {
  GRID_SIZE,
  TILE_WIDTH,
  TILE_HEIGHT,
  TILE_WIDTH_HALF,
  TILE_HEIGHT_HALF,
  GRID_LINE_COLOR,
  GRID_FILL_COLOR,
  BUILDINGS,
  STORAGE_KEY,
} from '@shared/constants';
import { networkService, ServerState } from '../../services/NetworkService';

export class MainMap extends Phaser.Scene {
  private gridSystem!: GridSystem;
  private gridGraphics!: Phaser.GameObjects.Graphics;
  private buildings: Building[] = [];
  private buildingMap: Map<string, Building> = new Map();
  private ghostBuilding: GhostBuilding | null = null;
  private selectedBuildingType: BuildingType | null = null;
  private lastValidPosition: { row: number; col: number; valid: boolean } | null = null;

  // Online/offline mode
  private isOnline = false;
  private resources: Resources = { food: 500, gold: 500, oil: 0 };

  // UI elements (HTML-based)
  private foodElement: HTMLElement | null = null;
  private goldElement: HTMLElement | null = null;
  private oilElement: HTMLElement | null = null;
  private statusElement: HTMLElement | null = null;

  constructor() {
    super({ key: 'MainMap' });
  }

  async create(): Promise<void> {
    // Calculate grid dimensions for camera setup
    const gridPixelWidth = GRID_SIZE * TILE_WIDTH;
    const gridPixelHeight = GRID_SIZE * TILE_HEIGHT;

    // Calculate zoom to fit entire grid in view with padding
    const paddingFactor = 0.85; // 85% of viewport used for grid
    const zoomX = (this.cameras.main.width * paddingFactor) / gridPixelWidth;
    const zoomY = (this.cameras.main.height * paddingFactor) / gridPixelHeight;
    const zoom = Math.min(zoomX, zoomY);

    // Set camera zoom
    this.cameras.main.setZoom(zoom);

    // Grid origin at a fixed world position - top point of the isometric grid
    // The grid extends down and to both sides from this point
    const originX = gridPixelWidth / 2;
    const originY = 50; // Small top padding

    // Initialize grid system
    this.gridSystem = new GridSystem(originX, originY);

    // Draw the grid
    this.drawGrid();

    // Center the camera on the grid center
    // Grid center in world coords is at (originX, originY + gridPixelHeight/2)
    const gridCenterX = originX;
    const gridCenterY = originY + gridPixelHeight / 2;
    this.cameras.main.centerOn(gridCenterX, gridCenterY);

    // Setup input handlers
    this.setupInput();

    // Setup UI button handlers
    this.setupUIButtons();

    // Create UI text displays
    this.createUIOverlay();

    // Attempt to connect to server
    this.updateStatus('Connecting to server...');
    const connected = await networkService.connect();

    if (connected) {
      this.isOnline = true;
      this.updateStatus('Online - Connected to server');
      this.setupServerSync();
    } else {
      this.isOnline = false;
      this.updateStatus('Offline - Using local storage');
      this.loadLayout();
    }
  }

  /**
   * Draw the isometric grid
   */
  private drawGrid(): void {
    this.gridGraphics = this.add.graphics();

    // Draw filled grid background
    // Tiles are drawn centered between grid lines (at row+0.5, col+0.5)
    this.gridGraphics.fillStyle(GRID_FILL_COLOR, 0.3);

    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        // Center tile between grid intersections
        const pos = this.gridSystem.gridToScreen(row + 0.5, col + 0.5);
        this.drawTile(pos.x, pos.y, GRID_FILL_COLOR, 0.3);
      }
    }

    // Draw grid lines (pass through grid intersections 0 to GRID_SIZE)
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
    // Track dragging state for camera pan
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let cameraStartX = 0;
    let cameraStartY = 0;

    // Pointer move - update ghost building position and handle drag
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      // Handle camera dragging
      if (isDragging && pointer.isDown) {
        const dx = pointer.x - dragStartX;
        const dy = pointer.y - dragStartY;
        this.cameras.main.scrollX = cameraStartX - dx / this.cameras.main.zoom;
        this.cameras.main.scrollY = cameraStartY - dy / this.cameras.main.zoom;
        return;
      }

      if (!this.selectedBuildingType || !this.ghostBuilding) return;

      // Convert screen coordinates to world coordinates (accounting for camera)
      const worldPoint = this.cameras.main.getWorldPoint(pointer.x, pointer.y);
      const gridPos = this.gridSystem.screenToGrid(worldPoint.x, worldPoint.y);
      const def = BUILDINGS[this.selectedBuildingType];

      // Check if placement is valid
      const isValid = this.gridSystem.canPlace(
        gridPos.row,
        gridPos.col,
        def.width,
        def.height
      );

      // Get screen position for the building center (centered over the footprint)
      const centerRow = gridPos.row + def.height / 2;
      const centerCol = gridPos.col + def.width / 2;
      const screenPos = this.gridSystem.gridToScreen(centerRow, centerCol);

      // Update ghost building
      this.ghostBuilding.update(screenPos.x, screenPos.y, isValid);
      this.lastValidPosition = { row: gridPos.row, col: gridPos.col, valid: isValid };
    });

    // Pointer down - start drag or place building
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      // If no building selected, start camera drag
      if (!this.selectedBuildingType) {
        isDragging = true;
        dragStartX = pointer.x;
        dragStartY = pointer.y;
        cameraStartX = this.cameras.main.scrollX;
        cameraStartY = this.cameras.main.scrollY;
        return;
      }

      // Place building if valid position
      if (!this.lastValidPosition || !this.lastValidPosition.valid) return;

      this.placeBuilding(
        this.selectedBuildingType,
        this.lastValidPosition.row,
        this.lastValidPosition.col
      );
    });

    // Pointer up - stop dragging
    this.input.on('pointerup', () => {
      isDragging = false;
    });

    // Mouse wheel - zoom in/out (Google Maps style: zoom toward cursor)
    this.input.on('wheel', (pointer: Phaser.Input.Pointer, _gameObjects: Phaser.GameObjects.GameObject[], _deltaX: number, deltaY: number) => {
      const camera = this.cameras.main;
      const oldZoom = camera.zoom;

      // Calculate world point under cursor manually (more reliable than getWorldPoint)
      const worldX = camera.scrollX + (pointer.x - camera.width / 2) / oldZoom;
      const worldY = camera.scrollY + (pointer.y - camera.height / 2) / oldZoom;

      // Calculate new zoom level
      const zoomChange = deltaY > 0 ? -0.1 : 0.1;
      const newZoom = Phaser.Math.Clamp(oldZoom + zoomChange, 0.2, 2);

      // Calculate new scroll so the world point stays under cursor
      // Formula: worldX = scrollX + (pointerX - width/2) / zoom
      // Solving for scrollX: scrollX = worldX - (pointerX - width/2) / zoom
      const newScrollX = worldX - (pointer.x - camera.width / 2) / newZoom;
      const newScrollY = worldY - (pointer.y - camera.height / 2) / newZoom;

      // Apply new scroll and zoom
      camera.setScroll(newScrollX, newScrollY);
      camera.setZoom(newZoom);
    });

    // Keyboard zoom - Ctrl + / Ctrl -
    // Escape - cancel building placement
    this.input.keyboard?.on('keydown', (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        this.cancelBuildingPlacement();
      } else if (event.ctrlKey || event.metaKey) {
        if (event.key === '=' || event.key === '+') {
          event.preventDefault();
          const newZoom = Phaser.Math.Clamp(this.cameras.main.zoom + 0.1, 0.2, 2);
          this.cameras.main.setZoom(newZoom);
        } else if (event.key === '-') {
          event.preventDefault();
          const newZoom = Phaser.Math.Clamp(this.cameras.main.zoom - 0.1, 0.2, 2);
          this.cameras.main.setZoom(newZoom);
        }
      }
    });

    // Right-click - cancel building placement
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      if (pointer.rightButtonDown() && this.selectedBuildingType) {
        this.cancelBuildingPlacement();
      }
    });
  }

  /**
   * Cancel building placement mode
   */
  private cancelBuildingPlacement(): void {
    this.selectedBuildingType = null;
    this.lastValidPosition = null;

    if (this.ghostBuilding) {
      this.ghostBuilding.hide();
    }

    // Remove selected state from all buttons
    document.querySelectorAll('.building-btn').forEach((btn) => {
      btn.classList.remove('selected');
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

        // Toggle: clicking same button again deselects
        if (this.selectedBuildingType === buildingType) {
          this.cancelBuildingPlacement();
          return;
        }

        // Update selection state
        buttons.forEach((b) => b.classList.remove('selected'));
        target.classList.add('selected');

        this.selectBuildingType(buildingType);
      });
    });

    // Attack button
    const attackBtn = document.getElementById('attack-btn');
    if (attackBtn) {
      attackBtn.addEventListener('click', () => {
        this.findMatch();
      });
    }
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
   * Create UI overlay for resources and status
   */
  private createUIOverlay(): void {
    // Get HTML elements for resource display
    this.foodElement = document.getElementById('food-value');
    this.goldElement = document.getElementById('gold-value');
    this.oilElement = document.getElementById('oil-value');
    this.statusElement = document.getElementById('status-display');

    this.updateResourceDisplay();
  }

  /**
   * Update the resource display
   */
  private updateResourceDisplay(): void {
    if (this.foodElement) this.foodElement.textContent = String(this.resources.food);
    if (this.goldElement) this.goldElement.textContent = String(this.resources.gold);
    if (this.oilElement) this.oilElement.textContent = String(this.resources.oil);
  }

  /**
   * Update the status display
   */
  private updateStatus(message: string): void {
    if (this.statusElement) {
      this.statusElement.textContent = message;
    }
    console.log(`[Status] ${message}`);
  }

  /**
   * Setup server state synchronization
   */
  private setupServerSync(): void {
    // Handle state changes from server
    networkService.onState((state: ServerState) => {
      this.handleServerState(state);
    });

    // Handle errors from server
    networkService.onServerError((error) => {
      this.updateStatus(`Error: ${error.message}`);
    });

    // Handle building placed confirmation
    networkService.onBuilding((building: BuildingData) => {
      // Building will be added through state sync
      console.log('Building placed confirmed:', building.id);
    });

    // Handle matchmaking responses
    networkService.onMatchFound((attackerId: string, opponent: MatchFoundMessage['opponent']) => {
      this.handleMatchFound(attackerId, opponent);
    });

    networkService.onNoMatch((reason: string) => {
      this.updateStatus(`No match found: ${reason}`);
    });
  }

  /**
   * Handle server state update
   */
  private handleServerState(state: ServerState): void {
    // Update resources
    this.resources = state.resources;
    this.updateResourceDisplay();

    // Sync buildings
    this.syncBuildings(state.buildings);
  }

  /**
   * Sync buildings with server state
   */
  private syncBuildings(serverBuildings: Map<string, BuildingData>): void {
    // Track which buildings we've seen from server
    const serverIds = new Set<string>();

    // Add or update buildings from server
    serverBuildings.forEach((data, id) => {
      serverIds.add(id);

      if (!this.buildingMap.has(id)) {
        // New building from server
        this.addBuildingFromData(data);
      }
    });

    // Remove buildings that no longer exist on server
    this.buildingMap.forEach((_, id) => {
      if (!serverIds.has(id)) {
        this.removeBuildingById(id);
      }
    });
  }

  /**
   * Add a building from server data
   */
  private addBuildingFromData(data: BuildingData): void {
    const def = BUILDINGS[data.type];

    // Mark grid as occupied
    this.gridSystem.occupy(data.row, data.col, def.width, def.height);

    // Calculate screen position (centered over the footprint)
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
      data.id,
      data.level
    );

    building.setDepth(data.row + data.col);
    this.buildings.push(building);
    this.buildingMap.set(data.id, building);
  }

  /**
   * Remove a building by ID
   */
  private removeBuildingById(id: string): void {
    const building = this.buildingMap.get(id);
    if (building) {
      const def = BUILDINGS[building.buildingType];
      this.gridSystem.vacate(building.gridRow, building.gridCol, def.width, def.height);
      building.destroy();
      this.buildingMap.delete(id);
      this.buildings = this.buildings.filter((b) => b.buildingId !== id);
    }
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

    if (this.isOnline) {
      // Online mode: send request to server
      networkService.placeBuilding(type, row, col);
      // Building will be added when server confirms via state sync
    } else {
      // Offline mode: handle locally
      this.placeBuildingLocally(type, row, col);
    }
  }

  /**
   * Place building locally (offline mode)
   */
  private placeBuildingLocally(type: BuildingType, row: number, col: number): void {
    const def = BUILDINGS[type];

    // Mark grid as occupied
    this.gridSystem.occupy(row, col, def.width, def.height);

    // Calculate screen position (centered over the footprint)
    const centerRow = row + def.height / 2;
    const centerCol = col + def.width / 2;
    const screenPos = this.gridSystem.gridToScreen(centerRow, centerCol);

    // Create building
    const building = new Building(this, type, row, col, screenPos.x, screenPos.y);

    // Sort by depth for correct rendering
    building.setDepth(row + col);

    this.buildings.push(building);
    this.buildingMap.set(building.buildingId, building);

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

        // Calculate screen position (centered over the footprint)
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
          data.id,
          data.level || 1
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

  /**
   * Initiate matchmaking
   */
  private findMatch(): void {
    if (!this.isOnline) {
      this.updateStatus('Cannot attack in offline mode');
      return;
    }

    this.updateStatus('Searching for opponent...');
    networkService.findMatch();
  }

  /**
   * Handle successful match found
   */
  private handleMatchFound(attackerId: string, opponent: MatchFoundMessage['opponent']): void {
    console.log(`Match found: ${opponent.username} with ${opponent.base.length} buildings`);
    this.updateStatus(`Found opponent: ${opponent.username}`);

    // Store opponent data for Battle scene (including attackerId for BattleRoom)
    this.scene.start('Battle', {
      attackerId,
      opponentId: opponent.odId,
      opponentUsername: opponent.username,
      opponentBase: opponent.base,
    });
  }
}
