/**
 * Battle Scene - Renders combat between attacker and defender
 *
 * This scene displays the defender's base and the attacker's units,
 * receiving real-time updates from the server's BattleRoom.
 */

import Phaser from 'phaser';
import { Client, Room } from 'colyseus.js';
import type { UnitData, UnitType } from '../../../../shared/types';
import {
  GRID_SIZE,
  TILE_WIDTH_HALF,
  TILE_HEIGHT_HALF,
  GRID_LINE_COLOR,
  GRID_FILL_COLOR,
  BUILDINGS,
  UNITS,
  DEPLOY_ZONE_DEPTH,
} from '../../../../shared/constants';
import { UnitManager } from '../entities/Unit';

// Battle state schema types (from server)
interface BattleStateSchema {
  phase: string;
  attackerId: string;
  attackerName: string;
  defenderId: string;
  defenderName: string;
  buildings: BuildingSchema[];
  units: UnitSchema[];
  tick: number;
  destructionPercent: number;
  timeRemaining: number;
  result: {
    destructionPercent: number;
    stars: number;
    loot: { food: number; gold: number; oil: number };
  };
}

interface BuildingSchema {
  id: string;
  buildingType: string;
  row: number;
  col: number;
  level: number;
  hp: number;
  maxHp: number;
  destroyed: boolean;
}

interface UnitSchema {
  id: string;
  unitType: string;
  hp: number;
  maxHp: number;
  state: string;
  row: number;
  col: number;
  targetId: string;
}

// Scene data passed from caller (from matchmaking)
interface BattleSceneData {
  serverUrl?: string;
  attackerId?: string;
  defenderId?: string;
  troops?: { type: UnitType; count: number }[];
  // New matchmaking format
  opponentId?: string;
  opponentUsername?: string;
  opponentBase?: import('@shared/types').BuildingData[];
}

/**
 * Convert grid position to isometric screen position
 */
function gridToScreen(row: number, col: number): { x: number; y: number } {
  return {
    x: (col - row) * TILE_WIDTH_HALF,
    y: (col + row) * TILE_HEIGHT_HALF,
  };
}

export class Battle extends Phaser.Scene {
  private client: Client | null = null;
  private room: Room<BattleStateSchema> | null = null;
  private unitManager: UnitManager | null = null;

  // Visual elements
  private gridGraphics: Phaser.GameObjects.Graphics | null = null;
  private buildingSprites: Map<string, Phaser.GameObjects.Container> = new Map();
  private deployZoneGraphics: Phaser.GameObjects.Graphics | null = null;

  // UI elements
  private statusText: Phaser.GameObjects.Text | null = null;
  private destructionText: Phaser.GameObjects.Text | null = null;
  private timeText: Phaser.GameObjects.Text | null = null;
  private troopButtons: Map<UnitType, Phaser.GameObjects.Container> = new Map();
  private selectedTroopType: UnitType | null = null;
  private remainingTroops: Map<UnitType, number> = new Map();

  // Scene data
  private sceneData: BattleSceneData | null = null;

  constructor() {
    super({ key: 'Battle' });
  }

  init(data: BattleSceneData): void {
    this.sceneData = data;

    // Initialize remaining troops (default troops for matchmaking)
    this.remainingTroops.clear();
    const troops = data.troops || [
      { type: 'warrior' as UnitType, count: 10 },
      { type: 'archer' as UnitType, count: 5 },
    ];
    for (const slot of troops) {
      this.remainingTroops.set(slot.type, slot.count);
    }
  }

  create(): void {
    // Center the camera
    const centerX = this.cameras.main.width / 2;
    const centerY = this.cameras.main.height / 2;
    this.cameras.main.setScroll(-centerX, -centerY + 200);

    // Create grid
    this.createGrid();

    // Create deploy zone visualization
    this.createDeployZone();

    // Create UI
    this.createUI();

    // Create unit manager
    this.unitManager = new UnitManager(this);

    // If we have opponent data from matchmaking, render their base and connect to battle server
    if (this.sceneData?.opponentBase) {
      this.renderOpponentBase();
      this.statusText?.setText(`Attacking ${this.sceneData.opponentUsername}'s base`);
      // Connect to BattleRoom for actual combat
      this.connectToBattleRoom();
    } else if (this.sceneData?.serverUrl) {
      // Legacy: direct battle room connection
      this.connectToServer();
    }

    // Enable camera controls
    this.setupCameraControls();

    // Handle input for unit deployment
    this.setupDeploymentInput();

    // Auto-select Warrior for convenience
    this.selectTroop('warrior');
  }

  /**
   * Render opponent's base from matchmaking data
   */
  private renderOpponentBase(): void {
    if (!this.sceneData?.opponentBase) return;

    console.log('Opponent base data:', this.sceneData.opponentBase);

    for (const building of this.sceneData.opponentBase) {
      const def = BUILDINGS[building.type as keyof typeof BUILDINGS];
      if (!def) {
        console.warn(`Unknown building type: ${building.type}`);
        continue;
      }

      console.log(`Rendering ${building.type} at row=${building.row}, col=${building.col}`);

      const buildingSchema: BuildingSchema = {
        id: building.id,
        buildingType: building.type,
        row: building.row,
        col: building.col,
        level: building.level,
        hp: def.hp * building.level,
        maxHp: def.hp * building.level,
        destroyed: false,
      };

      const container = this.createBuildingVisual(buildingSchema);
      this.buildingSprites.set(building.id, container);
      this.updateBuildingVisual(container, buildingSchema);
    }

    console.log(`Rendered ${this.sceneData.opponentBase.length} buildings from opponent's base`);
  }

  /**
   * Create the isometric grid
   */
  private createGrid(): void {
    this.gridGraphics = this.add.graphics();

    // Draw grid fill
    this.gridGraphics.fillStyle(GRID_FILL_COLOR, 0.5);

    const points: { x: number; y: number }[] = [];
    points.push(gridToScreen(0, 0));
    points.push(gridToScreen(0, GRID_SIZE));
    points.push(gridToScreen(GRID_SIZE, GRID_SIZE));
    points.push(gridToScreen(GRID_SIZE, 0));

    this.gridGraphics.fillPoints(
      points.map((p) => new Phaser.Geom.Point(p.x, p.y)),
      true
    );

    // Draw grid lines
    this.gridGraphics.lineStyle(1, GRID_LINE_COLOR, 0.3);

    for (let i = 0; i <= GRID_SIZE; i++) {
      const start = gridToScreen(i, 0);
      const end = gridToScreen(i, GRID_SIZE);
      this.gridGraphics.lineBetween(start.x, start.y, end.x, end.y);
    }

    for (let j = 0; j <= GRID_SIZE; j++) {
      const start = gridToScreen(0, j);
      const end = gridToScreen(GRID_SIZE, j);
      this.gridGraphics.lineBetween(start.x, start.y, end.x, end.y);
    }
  }

  /**
   * Create deploy zone visualization
   */
  private createDeployZone(): void {
    this.deployZoneGraphics = this.add.graphics();
    this.deployZoneGraphics.lineStyle(2, 0x00ff00, 0.5);
    this.deployZoneGraphics.fillStyle(0x00ff00, 0.1);

    // Draw deploy zones (edges of the grid)
    // Top zone
    for (let row = 0; row < DEPLOY_ZONE_DEPTH; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        this.drawDeployTile(row, col);
      }
    }

    // Bottom zone
    for (let row = GRID_SIZE - DEPLOY_ZONE_DEPTH; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        this.drawDeployTile(row, col);
      }
    }

    // Left zone (excluding corners already drawn)
    for (let row = DEPLOY_ZONE_DEPTH; row < GRID_SIZE - DEPLOY_ZONE_DEPTH; row++) {
      for (let col = 0; col < DEPLOY_ZONE_DEPTH; col++) {
        this.drawDeployTile(row, col);
      }
    }

    // Right zone (excluding corners already drawn)
    for (let row = DEPLOY_ZONE_DEPTH; row < GRID_SIZE - DEPLOY_ZONE_DEPTH; row++) {
      for (let col = GRID_SIZE - DEPLOY_ZONE_DEPTH; col < GRID_SIZE; col++) {
        this.drawDeployTile(row, col);
      }
    }
  }

  /**
   * Draw a single deploy zone tile
   */
  private drawDeployTile(row: number, col: number): void {
    if (!this.deployZoneGraphics) return;

    const points = [
      gridToScreen(row, col),
      gridToScreen(row, col + 1),
      gridToScreen(row + 1, col + 1),
      gridToScreen(row + 1, col),
    ];

    this.deployZoneGraphics.fillPoints(
      points.map((p) => new Phaser.Geom.Point(p.x, p.y)),
      true
    );
  }

  /**
   * Create UI elements
   */
  private createUI(): void {
    const { width } = this.cameras.main;

    // Status text (top center)
    this.statusText = this.add.text(width / 2, 20, 'Connecting...', {
      fontSize: '24px',
      color: '#ffffff',
      backgroundColor: '#000000aa',
      padding: { x: 10, y: 5 },
    });
    this.statusText.setOrigin(0.5, 0);
    this.statusText.setScrollFactor(0);
    this.statusText.setDepth(2000);

    // Destruction percentage (top left)
    this.destructionText = this.add.text(20, 20, 'Destruction: 0%', {
      fontSize: '20px',
      color: '#ffffff',
      backgroundColor: '#000000aa',
      padding: { x: 10, y: 5 },
    });
    this.destructionText.setScrollFactor(0);
    this.destructionText.setDepth(2000);

    // Time remaining (top right)
    this.timeText = this.add.text(width - 20, 20, 'Time: 3:00', {
      fontSize: '20px',
      color: '#ffffff',
      backgroundColor: '#000000aa',
      padding: { x: 10, y: 5 },
    });
    this.timeText.setOrigin(1, 0);
    this.timeText.setScrollFactor(0);
    this.timeText.setDepth(2000);

    // Troop selection buttons (bottom)
    this.createTroopButtons();
  }

  /**
   * Create troop selection buttons
   */
  private createTroopButtons(): void {
    const { width, height } = this.cameras.main;
    const troopTypes: UnitType[] = ['warrior', 'archer', 'cavalry', 'catapult'];
    const buttonWidth = 80;
    const buttonHeight = 60;
    const spacing = 10;
    const totalWidth = troopTypes.length * buttonWidth + (troopTypes.length - 1) * spacing;
    let startX = (width - totalWidth) / 2;

    for (const type of troopTypes) {
      const count = this.remainingTroops.get(type) || 0;
      if (count === 0) continue;

      const container = this.add.container(startX + buttonWidth / 2, height - 50);
      container.setScrollFactor(0);
      container.setDepth(2000);

      // Button background
      const bg = this.add.rectangle(0, 0, buttonWidth, buttonHeight, UNITS[type].color);
      bg.setStrokeStyle(2, 0xffffff);
      container.add(bg);

      // Troop name
      const nameText = this.add.text(0, -15, UNITS[type].name, {
        fontSize: '12px',
        color: '#ffffff',
      });
      nameText.setOrigin(0.5);
      container.add(nameText);

      // Count text
      const countText = this.add.text(0, 10, `x${count}`, {
        fontSize: '16px',
        color: '#ffffff',
      });
      countText.setOrigin(0.5);
      container.add(countText);

      // Make interactive
      bg.setInteractive({ useHandCursor: true });
      bg.on('pointerdown', () => {
        this.selectTroop(type);
      });

      this.troopButtons.set(type, container);
      startX += buttonWidth + spacing;
    }
  }

  /**
   * Select a troop type for deployment
   */
  private selectTroop(type: UnitType): void {
    // Deselect previous
    if (this.selectedTroopType) {
      const prevContainer = this.troopButtons.get(this.selectedTroopType);
      if (prevContainer) {
        const bg = prevContainer.list[0] as Phaser.GameObjects.Rectangle;
        bg.setStrokeStyle(2, 0xffffff);
      }
    }

    this.selectedTroopType = type;

    // Highlight selected
    const container = this.troopButtons.get(type);
    if (container) {
      const bg = container.list[0] as Phaser.GameObjects.Rectangle;
      bg.setStrokeStyle(3, 0xffff00);
    }

    this.statusText?.setText(`Selected: ${UNITS[type].name} - Click to deploy`);
  }

  /**
   * Update troop button count (called when server confirms deployment)
   */
  public updateTroopButton(type: UnitType): void {
    const count = this.remainingTroops.get(type) || 0;
    const container = this.troopButtons.get(type);
    if (container && container.list.length >= 3) {
      const countText = container.list[2] as Phaser.GameObjects.Text;
      countText.setText(`x${count}`);

      if (count === 0) {
        container.setAlpha(0.5);
        const bg = container.list[0] as Phaser.GameObjects.Rectangle;
        bg.disableInteractive();
      }
    }
  }

  /**
   * Setup camera controls (pan/zoom)
   */
  private setupCameraControls(): void {
    // Pan with middle mouse or drag
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (pointer.isDown && pointer.middleButtonDown()) {
        this.cameras.main.scrollX -= pointer.velocity.x / 10;
        this.cameras.main.scrollY -= pointer.velocity.y / 10;
      }
    });

    // Zoom with scroll wheel
    this.input.on('wheel', (_pointer: Phaser.Input.Pointer, _gameObjects: unknown[], _dx: number, dy: number) => {
      const zoom = this.cameras.main.zoom;
      const newZoom = Phaser.Math.Clamp(zoom - dy * 0.001, 0.5, 2);
      this.cameras.main.setZoom(newZoom);
    });
  }

  /**
   * Setup input for unit deployment
   */
  private setupDeploymentInput(): void {
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      if (pointer.leftButtonDown() && this.selectedTroopType) {
        this.handleDeployClick(pointer);
      }
    });
  }

  /**
   * Handle click for unit deployment
   */
  private handleDeployClick(pointer: Phaser.Input.Pointer): void {
    if (!this.room || !this.selectedTroopType) return;

    // Check phase
    const state = this.room.state;
    if (state.phase !== 'setup') {
      return;
    }

    // Check if we have troops remaining
    const remaining = this.remainingTroops.get(this.selectedTroopType) || 0;
    if (remaining <= 0) {
      this.statusText?.setText('No more troops of this type!');
      return;
    }

    // Convert screen position to world position
    const worldPoint = this.cameras.main.getWorldPoint(pointer.x, pointer.y);

    // Convert to grid position
    const gridPos = this.screenToGrid(worldPoint.x, worldPoint.y);

    // Send deploy message to server
    this.room.send('deployUnit', {
      type: 'deployUnit',
      unitType: this.selectedTroopType,
      row: Math.floor(gridPos.row),
      col: Math.floor(gridPos.col),
    });
  }

  /**
   * Convert screen position to grid position
   */
  private screenToGrid(x: number, y: number): { row: number; col: number } {
    const col = (x / TILE_WIDTH_HALF + y / TILE_HEIGHT_HALF) / 2;
    const row = (y / TILE_HEIGHT_HALF - x / TILE_WIDTH_HALF) / 2;
    return { row, col };
  }

  /**
   * Connect to the battle server (legacy)
   */
  private async connectToServer(): Promise<void> {
    if (!this.sceneData) return;

    try {
      this.client = new Client(this.sceneData.serverUrl);

      this.room = await this.client.joinOrCreate<BattleStateSchema>('battle', {
        attackerId: this.sceneData.attackerId,
        defenderId: this.sceneData.defenderId,
        troops: this.sceneData.troops,
      });

      this.statusText?.setText('Setup Phase - Deploy your troops!');
      this.setupRoomListeners();
    } catch (error) {
      console.error('Failed to connect to battle:', error);
      this.statusText?.setText('Failed to connect to battle server');
    }
  }

  /**
   * Connect to BattleRoom after matchmaking
   */
  private async connectToBattleRoom(): Promise<void> {
    if (!this.sceneData?.attackerId || !this.sceneData?.opponentId) {
      console.error('Missing attackerId or opponentId for BattleRoom');
      return;
    }

    try {
      // Connect to the same server as GameRoom
      this.client = new Client('ws://localhost:2567');

      // Default troops for matchmaking battles
      const troops = this.sceneData.troops || [
        { type: 'warrior' as UnitType, count: 10 },
        { type: 'archer' as UnitType, count: 5 },
      ];

      console.log('Connecting to BattleRoom...', {
        attackerId: this.sceneData.attackerId,
        defenderId: this.sceneData.opponentId,
        troops,
      });

      this.room = await this.client.joinOrCreate<BattleStateSchema>('battle', {
        attackerId: this.sceneData.attackerId,
        defenderId: this.sceneData.opponentId,
        troops,
      });

      console.log('Connected to BattleRoom:', this.room.sessionId);
      this.statusText?.setText('Setup Phase - Select troops and deploy!');
      this.setupRoomListeners();
    } catch (error) {
      console.error('Failed to connect to BattleRoom:', error);
      this.statusText?.setText('Failed to start battle - click to retry');
    }
  }

  /**
   * Setup room event listeners
   */
  private setupRoomListeners(): void {
    if (!this.room) return;

    // Listen for state changes
    this.room.onStateChange((state) => {
      this.onStateChange(state);
    });

    // Listen for errors
    this.room.onMessage('error', (message) => {
      console.error('Battle error:', message);
      this.statusText?.setText(`Error: ${message.message}`);
    });

    // Listen for disconnect
    this.room.onLeave(() => {
      this.statusText?.setText('Disconnected from battle');
    });
  }

  /**
   * Handle state changes from server
   */
  private onStateChange(state: BattleStateSchema): void {
    // Update phase-specific UI
    switch (state.phase) {
      case 'setup':
        this.statusText?.setText('Setup Phase - Deploy your troops! Press SPACE to start');
        this.deployZoneGraphics?.setVisible(true);
        break;
      case 'running':
        this.statusText?.setText(`Battle in progress - ${state.defenderName}'s base`);
        this.deployZoneGraphics?.setVisible(false);
        break;
      case 'ended':
        this.showBattleResult(state);
        break;
    }

    // Update destruction text
    this.destructionText?.setText(`Destruction: ${state.destructionPercent}%`);

    // Update time text
    const minutes = Math.floor(state.timeRemaining / 60);
    const seconds = Math.floor(state.timeRemaining % 60);
    this.timeText?.setText(`Time: ${minutes}:${seconds.toString().padStart(2, '0')}`);

    // Update buildings
    this.updateBuildings(state.buildings);

    // Update units
    this.updateUnits(state.units);
  }

  /**
   * Update building visuals
   */
  private updateBuildings(buildings: BuildingSchema[]): void {
    for (const buildingData of buildings) {
      let container = this.buildingSprites.get(buildingData.id);

      if (!container) {
        // Create new building visual
        container = this.createBuildingVisual(buildingData);
        this.buildingSprites.set(buildingData.id, container);
      }

      // Update building state
      this.updateBuildingVisual(container, buildingData);
    }
  }

  /**
   * Create visual representation of a building
   */
  private createBuildingVisual(building: BuildingSchema): Phaser.GameObjects.Container {
    const def = BUILDINGS[building.buildingType as keyof typeof BUILDINGS];
    const pos = gridToScreen(building.row + def.height / 2, building.col + def.width / 2);

    const container = this.add.container(pos.x, pos.y);

    // Building shape - draw as isometric diamond
    const isoWidth = (def.width + def.height) * TILE_WIDTH_HALF;
    const isoHeight = (def.width + def.height) * TILE_HEIGHT_HALF;

    const graphics = this.add.graphics();
    graphics.fillStyle(def.color, 1);
    graphics.beginPath();
    graphics.moveTo(0, -isoHeight / 2);           // Top
    graphics.lineTo(isoWidth / 2, 0);             // Right
    graphics.lineTo(0, isoHeight / 2);            // Bottom
    graphics.lineTo(-isoWidth / 2, 0);            // Left
    graphics.closePath();
    graphics.fillPath();
    graphics.lineStyle(2, 0x000000, 1);
    graphics.strokePath();
    container.add(graphics);
    container.setData('buildingGraphics', graphics);

    // HP bar
    const hpBar = this.add.graphics();
    container.add(hpBar);
    container.setData('hpBar', hpBar);

    // Set depth based on position
    container.setDepth(building.row + building.col);

    return container;
  }

  /**
   * Update building visual state
   */
  private updateBuildingVisual(container: Phaser.GameObjects.Container, building: BuildingSchema): void {
    const hpBar = container.getData('hpBar') as Phaser.GameObjects.Graphics;
    const buildingGraphics = container.getData('buildingGraphics') as Phaser.GameObjects.Graphics;
    const def = BUILDINGS[building.buildingType as keyof typeof BUILDINGS];
    const isoHeight = (def.width + def.height) * TILE_HEIGHT_HALF;

    if (building.destroyed) {
      // Redraw building as gray/destroyed
      buildingGraphics.clear();
      const isoWidth = (def.width + def.height) * TILE_WIDTH_HALF;
      buildingGraphics.fillStyle(0x333333, 0.5);
      buildingGraphics.beginPath();
      buildingGraphics.moveTo(0, -isoHeight / 2);
      buildingGraphics.lineTo(isoWidth / 2, 0);
      buildingGraphics.lineTo(0, isoHeight / 2);
      buildingGraphics.lineTo(-isoWidth / 2, 0);
      buildingGraphics.closePath();
      buildingGraphics.fillPath();
      hpBar.clear();
    } else {
      // Update HP bar
      hpBar.clear();
      const barWidth = 50;
      const barHeight = 6;
      const barY = isoHeight / 2 + 5;

      hpBar.fillStyle(0x330000);
      hpBar.fillRect(-barWidth / 2, barY, barWidth, barHeight);

      const hpPercent = building.hp / building.maxHp;
      const fillColor = hpPercent > 0.5 ? 0x00ff00 : hpPercent > 0.25 ? 0xffff00 : 0xff0000;
      hpBar.fillStyle(fillColor);
      hpBar.fillRect(-barWidth / 2, barY, barWidth * hpPercent, barHeight);
    }
  }

  /**
   * Update unit visuals
   */
  private updateUnits(units: UnitSchema[]): void {
    if (!this.unitManager) return;

    const unitData: UnitData[] = units.map((u) => ({
      id: u.id,
      type: u.unitType as UnitType,
      hp: u.hp,
      maxHp: u.maxHp,
      state: u.state as UnitData['state'],
      row: u.row,
      col: u.col,
      targetId: u.targetId || undefined,
    }));

    this.unitManager.updateFromServer(unitData);

    // Update remaining troop counts based on deployed units
    // (Server handles this, but we track locally for UI)
  }

  /**
   * Show battle result screen
   */
  private showBattleResult(state: BattleStateSchema): void {
    const { width, height } = this.cameras.main;

    // Dim background
    const overlay = this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.7);
    overlay.setScrollFactor(0);
    overlay.setDepth(3000);

    // Result panel
    const panel = this.add.container(width / 2, height / 2);
    panel.setScrollFactor(0);
    panel.setDepth(3001);

    // Background
    const bg = this.add.rectangle(0, 0, 400, 300, 0x222222);
    bg.setStrokeStyle(3, 0xffffff);
    panel.add(bg);

    // Title
    const title = this.add.text(0, -120, 'Battle Complete!', {
      fontSize: '32px',
      color: '#ffffff',
    });
    title.setOrigin(0.5);
    panel.add(title);

    // Stars
    const starsText = this.add.text(0, -70, '⭐'.repeat(state.result.stars), {
      fontSize: '40px',
    });
    starsText.setOrigin(0.5);
    panel.add(starsText);

    // Destruction
    const destruction = this.add.text(0, -20, `Destruction: ${state.result.destructionPercent}%`, {
      fontSize: '24px',
      color: '#ffffff',
    });
    destruction.setOrigin(0.5);
    panel.add(destruction);

    // Loot
    const loot = this.add.text(
      0,
      30,
      `Loot: 🍖${state.result.loot.food} 💰${state.result.loot.gold} 🛢️${state.result.loot.oil}`,
      { fontSize: '20px', color: '#ffffff' }
    );
    loot.setOrigin(0.5);
    panel.add(loot);

    // Return button
    const returnBtn = this.add.rectangle(0, 100, 150, 40, 0x4444ff);
    returnBtn.setStrokeStyle(2, 0xffffff);
    returnBtn.setInteractive({ useHandCursor: true });
    returnBtn.on('pointerdown', () => {
      this.scene.start('MainMap');
    });
    panel.add(returnBtn);

    const returnText = this.add.text(0, 100, 'Return Home', {
      fontSize: '18px',
      color: '#ffffff',
    });
    returnText.setOrigin(0.5);
    panel.add(returnText);
  }

  update(time: number, delta: number): void {
    // Update all units
    this.unitManager?.update(time, delta);

    if (!this.input.keyboard) return;

    // Keyboard shortcuts for troop selection (1 = warrior, 2 = archer)
    if (Phaser.Input.Keyboard.JustDown(this.input.keyboard.addKey('ONE'))) {
      this.selectTroop('warrior');
    }
    if (Phaser.Input.Keyboard.JustDown(this.input.keyboard.addKey('TWO'))) {
      this.selectTroop('archer');
    }

    // Handle start battle key
    if (this.room?.state.phase === 'setup' && Phaser.Input.Keyboard.JustDown(this.input.keyboard.addKey('SPACE'))) {
      this.room.send('startBattle');
    }
  }

  shutdown(): void {
    // Cleanup
    this.room?.leave();
    this.unitManager?.clear();
    this.buildingSprites.clear();
    this.troopButtons.clear();
  }
}
