/**
 * Unit - Client-side unit entity with Finite State Machine
 *
 * Visual representation of combat units. The actual game logic
 * runs on the server; this class handles rendering and animations.
 */

import Phaser from 'phaser';
import type { UnitData, UnitState, UnitType } from '../../../../shared/types';
import { UNITS, TILE_WIDTH_HALF, TILE_HEIGHT_HALF } from '../../../../shared/constants';

/**
 * Convert grid position to isometric screen position
 */
function gridToScreen(row: number, col: number): { x: number; y: number } {
  return {
    x: (col - row) * TILE_WIDTH_HALF,
    y: (col + row) * TILE_HEIGHT_HALF,
  };
}

/**
 * Unit entity class for Phaser
 */
export class Unit extends Phaser.GameObjects.Container {
  private unitId: string;
  private unitType: UnitType;
  private currentState: UnitState = 'idle';
  private hp: number;
  private maxHp: number;
  private gridRow: number;
  private gridCol: number;

  // Visual components
  private sprite: Phaser.GameObjects.Ellipse;
  private hpBar: Phaser.GameObjects.Graphics;
  private stateText: Phaser.GameObjects.Text;

  // Animation state
  private targetX: number = 0;
  private targetY: number = 0;
  private isMoving: boolean = false;

  constructor(scene: Phaser.Scene, data: UnitData) {
    const pos = gridToScreen(data.row, data.col);
    super(scene, pos.x, pos.y);

    this.unitId = data.id;
    this.unitType = data.type;
    this.hp = data.hp;
    this.maxHp = data.maxHp;
    this.currentState = data.state;
    this.gridRow = data.row;
    this.gridCol = data.col;

    // Get unit definition for visual properties
    const def = UNITS[this.unitType];

    // Create unit sprite (ellipse for now, will be replaced with actual sprites)
    this.sprite = scene.add.ellipse(0, 0, 20, 15, def.color);
    this.sprite.setStrokeStyle(2, 0x000000);
    this.add(this.sprite);

    // Create HP bar
    this.hpBar = scene.add.graphics();
    this.add(this.hpBar);
    this.updateHpBar();

    // Create state text (debug)
    this.stateText = scene.add.text(0, -20, '', {
      fontSize: '10px',
      color: '#ffffff',
      backgroundColor: '#000000',
    });
    this.stateText.setOrigin(0.5);
    this.add(this.stateText);
    this.stateText.setVisible(false); // Hide by default

    // Set depth for proper layering
    this.setDepth(1000 + data.row + data.col);

    scene.add.existing(this);
  }

  /**
   * Get the unit's ID
   */
  getId(): string {
    return this.unitId;
  }

  /**
   * Get the unit's type
   */
  getType(): UnitType {
    return this.unitType;
  }

  /**
   * Get current state
   */
  getState(): UnitState {
    return this.currentState;
  }

  /**
   * Update unit from server state
   */
  updateFromServer(data: UnitData): void {
    const oldState = this.currentState;
    this.currentState = data.state;
    this.hp = data.hp;
    this.maxHp = data.maxHp;

    // Update position if changed
    if (data.row !== this.gridRow || data.col !== this.gridCol) {
      this.gridRow = data.row;
      this.gridCol = data.col;

      const pos = gridToScreen(data.row, data.col);
      this.targetX = pos.x;
      this.targetY = pos.y;
      this.isMoving = true;
    }

    // Handle state changes
    if (oldState !== this.currentState) {
      this.onStateChange(oldState, this.currentState);
    }

    // Update visuals
    this.updateHpBar();
    this.updateStateText();
    this.updateDepth();
  }

  /**
   * Handle state transitions (FSM)
   */
  private onStateChange(_from: UnitState, to: UnitState): void {
    switch (to) {
      case 'idle':
        this.playIdleAnimation();
        break;
      case 'moving':
        this.playMoveAnimation();
        break;
      case 'attacking':
        this.playAttackAnimation();
        break;
      case 'dead':
        this.playDeathAnimation();
        break;
    }
  }

  /**
   * Play idle animation
   */
  private playIdleAnimation(): void {
    this.sprite.setAlpha(1);
    // Could add breathing/idle tween here
  }

  /**
   * Play movement animation
   */
  private playMoveAnimation(): void {
    this.sprite.setAlpha(1);
    // Movement is handled in update() with lerping
  }

  /**
   * Play attack animation
   */
  private playAttackAnimation(): void {
    // Flash the unit
    this.scene.tweens.add({
      targets: this.sprite,
      scaleX: 1.2,
      scaleY: 1.2,
      duration: 100,
      yoyo: true,
      ease: 'Power2',
    });
  }

  /**
   * Play death animation
   */
  private playDeathAnimation(): void {
    this.scene.tweens.add({
      targets: this,
      alpha: 0,
      y: this.y + 10,
      duration: 500,
      onComplete: () => {
        this.destroy();
      },
    });
  }

  /**
   * Update HP bar visual
   */
  private updateHpBar(): void {
    this.hpBar.clear();

    const barWidth = 24;
    const barHeight = 4;
    const barY = -15;

    // Background (dark red)
    this.hpBar.fillStyle(0x330000);
    this.hpBar.fillRect(-barWidth / 2, barY, barWidth, barHeight);

    // HP fill (green to red gradient based on HP)
    const hpPercent = this.hp / this.maxHp;
    const fillWidth = barWidth * hpPercent;

    let color = 0x00ff00; // Green
    if (hpPercent < 0.3) {
      color = 0xff0000; // Red
    } else if (hpPercent < 0.6) {
      color = 0xffff00; // Yellow
    }

    this.hpBar.fillStyle(color);
    this.hpBar.fillRect(-barWidth / 2, barY, fillWidth, barHeight);

    // Border
    this.hpBar.lineStyle(1, 0x000000);
    this.hpBar.strokeRect(-barWidth / 2, barY, barWidth, barHeight);
  }

  /**
   * Update state text (debug)
   */
  private updateStateText(): void {
    this.stateText.setText(this.currentState);
  }

  /**
   * Update depth for proper z-ordering
   */
  private updateDepth(): void {
    this.setDepth(1000 + this.gridRow + this.gridCol);
  }

  /**
   * Show/hide debug info
   */
  setDebugVisible(visible: boolean): void {
    this.stateText.setVisible(visible);
  }

  /**
   * Update method called every frame
   */
  update(_time: number, _delta: number): void {
    // Smooth movement interpolation
    if (this.isMoving) {
      const speed = 0.1; // Interpolation speed
      this.x = Phaser.Math.Linear(this.x, this.targetX, speed);
      this.y = Phaser.Math.Linear(this.y, this.targetY, speed);

      // Check if close enough to target
      const dist = Phaser.Math.Distance.Between(this.x, this.y, this.targetX, this.targetY);
      if (dist < 1) {
        this.x = this.targetX;
        this.y = this.targetY;
        this.isMoving = false;
      }
    }
  }
}

/**
 * Unit manager to handle all units in a scene
 */
export class UnitManager {
  private scene: Phaser.Scene;
  private units: Map<string, Unit> = new Map();

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * Create a new unit
   */
  createUnit(data: UnitData): Unit {
    const unit = new Unit(this.scene, data);
    this.units.set(data.id, unit);
    return unit;
  }

  /**
   * Get unit by ID
   */
  getUnit(id: string): Unit | undefined {
    return this.units.get(id);
  }

  /**
   * Update all units from server state
   */
  updateFromServer(unitsData: UnitData[]): void {
    const serverIds = new Set(unitsData.map((u) => u.id));

    // Update or create units
    for (const data of unitsData) {
      let unit = this.units.get(data.id);
      if (unit) {
        unit.updateFromServer(data);
      } else {
        unit = this.createUnit(data);
      }
    }

    // Remove units that no longer exist on server
    for (const [id, unit] of this.units) {
      if (!serverIds.has(id)) {
        unit.destroy();
        this.units.delete(id);
      }
    }
  }

  /**
   * Update all units (called every frame)
   */
  update(time: number, delta: number): void {
    for (const unit of this.units.values()) {
      unit.update(time, delta);
    }
  }

  /**
   * Clear all units
   */
  clear(): void {
    for (const unit of this.units.values()) {
      unit.destroy();
    }
    this.units.clear();
  }

  /**
   * Get all units
   */
  getAllUnits(): Unit[] {
    return Array.from(this.units.values());
  }

  /**
   * Get unit count
   */
  getCount(): number {
    return this.units.size;
  }
}
