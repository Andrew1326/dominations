/**
 * BattleRoom - Colyseus room for managing combat sessions
 *
 * Handles the real-time combat between attacker and defender,
 * running the simulation on the server and broadcasting state updates.
 */

import { Room, Client } from '@colyseus/core';
import { Schema, ArraySchema, type, MapSchema } from '@colyseus/schema';
import type {
  DeployUnitMessage,
  BattleClientMessage,
  UnitType,
  BattleResult,
} from '@shared/types';
import { Base } from '../models/Base';
import { User } from '../models/User';
import {
  createSimulation,
  deployUnit,
  processTick,
  calculateDestructionPercent,
  calculateStars,
  calculateLoot,
  isBattleOver,
  validateTroops,
  BattleSimulation,
} from '../mechanics/CombatResolver';
import { BATTLE_TICK_RATE, BATTLE_MAX_DURATION } from '@shared/constants';

// ============================================================
// Colyseus Schema Classes
// ============================================================

class UnitSchema extends Schema {
  @type('string') id!: string;
  @type('string') unitType!: string;
  @type('number') hp!: number;
  @type('number') maxHp!: number;
  @type('string') state!: string;
  @type('number') row!: number;
  @type('number') col!: number;
  @type('string') targetId: string = '';
}

class BuildingSchema extends Schema {
  @type('string') id!: string;
  @type('string') buildingType!: string;
  @type('number') row!: number;
  @type('number') col!: number;
  @type('number') level!: number;
  @type('number') hp!: number;
  @type('number') maxHp!: number;
  @type('boolean') destroyed!: boolean;
}

class ResourcesSchema extends Schema {
  @type('number') food: number = 0;
  @type('number') gold: number = 0;
  @type('number') oil: number = 0;
}

class BattleResultSchema extends Schema {
  @type('number') destructionPercent: number = 0;
  @type('number') stars: number = 0;
  @type(ResourcesSchema) loot = new ResourcesSchema();
}

class BattleState extends Schema {
  @type('string') phase: string = 'setup'; // setup, running, ended
  @type('string') attackerId!: string;
  @type('string') attackerName!: string;
  @type('string') defenderId!: string;
  @type('string') defenderName!: string;
  @type([BuildingSchema]) buildings = new ArraySchema<BuildingSchema>();
  @type([UnitSchema]) units = new ArraySchema<UnitSchema>();
  @type('number') tick: number = 0;
  @type('number') destructionPercent: number = 0;
  @type('number') timeRemaining: number = BATTLE_MAX_DURATION;
  @type(BattleResultSchema) result = new BattleResultSchema();
}

// ============================================================
// Room Options
// ============================================================

interface BattleRoomOptions {
  attackerId: string;
  defenderId: string;
  troops: { type: UnitType; count: number }[];
}

// ============================================================
// BattleRoom
// ============================================================

export class BattleRoom extends Room<BattleState> {
  maxClients = 1; // Only attacker joins
  private simulation: BattleSimulation | null = null;
  private tickInterval: NodeJS.Timeout | null = null;
  private defenderResources = { food: 0, gold: 0, oil: 0 };
  private remainingTroops: Map<UnitType, number> = new Map();

  async onCreate(options: BattleRoomOptions): Promise<void> {
    console.log('BattleRoom creating...', options);

    // Validate options
    if (!options.attackerId || !options.defenderId || !options.troops) {
      throw new Error('Missing required options');
    }

    // Validate troops
    const troopValidation = validateTroops(options.troops, 50); // Max 50 troops
    if (!troopValidation.valid) {
      throw new Error(troopValidation.error);
    }

    // Load defender's base
    const defenderBase = await Base.findOne({ owner: options.defenderId });
    if (!defenderBase) {
      throw new Error('Defender base not found');
    }

    // Load attacker and defender info
    const attacker = await User.findById(options.attackerId);
    const defender = await User.findById(options.defenderId);
    if (!attacker || !defender) {
      throw new Error('Player not found');
    }

    // Initialize state
    this.setState(new BattleState());
    this.state.attackerId = options.attackerId;
    this.state.attackerName = attacker.username;
    this.state.defenderId = options.defenderId;
    this.state.defenderName = defender.username;
    this.state.phase = 'setup';

    // Store defender resources for loot calculation
    this.defenderResources = {
      food: defenderBase.resources.food,
      gold: defenderBase.resources.gold,
      oil: defenderBase.resources.oil,
    };

    // Store troop counts for deployment
    for (const slot of options.troops) {
      this.remainingTroops.set(slot.type, slot.count);
    }

    // Create simulation
    const buildingsData = defenderBase.buildings.map((b) => ({
      id: b.id,
      type: b.type,
      row: b.row,
      col: b.col,
      level: b.level,
      constructionStartedAt: b.constructionStartedAt?.getTime(),
      constructionEndsAt: b.constructionEndsAt?.getTime(),
    }));

    this.simulation = createSimulation(buildingsData, this.defenderResources);

    // Populate initial building state
    for (const building of this.simulation.buildings) {
      const schema = new BuildingSchema();
      schema.id = building.id;
      schema.buildingType = building.type;
      schema.row = building.row;
      schema.col = building.col;
      schema.level = building.level;
      schema.hp = building.hp;
      schema.maxHp = building.maxHp;
      schema.destroyed = building.destroyed;
      this.state.buildings.push(schema);
    }

    // Handle messages
    this.onMessage('deployUnit', (client, message: DeployUnitMessage) => {
      this.handleDeployUnit(client, message);
    });

    this.onMessage('startBattle', () => {
      this.startBattle();
    });

    this.onMessage('endBattle', () => {
      this.endBattle();
    });

    console.log(`BattleRoom created: ${attacker.username} vs ${defender.username}`);
  }

  onJoin(client: Client): void {
    console.log(`Client ${client.sessionId} joined battle`);
  }

  async onLeave(client: Client): Promise<void> {
    console.log(`Client ${client.sessionId} left battle`);

    // If battle is running, end it
    if (this.state.phase === 'running') {
      this.endBattle();
    }
  }

  onDispose(): void {
    console.log('BattleRoom disposed');
    if (this.tickInterval) {
      clearInterval(this.tickInterval);
    }
  }

  /**
   * Handle unit deployment during setup phase
   */
  private handleDeployUnit(client: Client, message: DeployUnitMessage): void {
    if (this.state.phase !== 'setup') {
      client.send('error', { type: 'error', code: 'INVALID_PHASE', message: 'Can only deploy during setup' });
      return;
    }

    if (!this.simulation) {
      client.send('error', { type: 'error', code: 'NO_SIMULATION', message: 'Simulation not ready' });
      return;
    }

    // Check if player has this troop available
    const remaining = this.remainingTroops.get(message.unitType) || 0;
    if (remaining <= 0) {
      client.send('error', { type: 'error', code: 'NO_TROOPS', message: 'No more troops of this type' });
      return;
    }

    // Deploy unit
    const unit = deployUnit(this.simulation, message.unitType, message.row, message.col);
    if (!unit) {
      client.send('error', { type: 'error', code: 'INVALID_POSITION', message: 'Cannot deploy at this position' });
      return;
    }

    // Decrement troop count
    this.remainingTroops.set(message.unitType, remaining - 1);

    // Add to state
    const schema = new UnitSchema();
    schema.id = unit.id;
    schema.unitType = unit.type;
    schema.hp = unit.hp;
    schema.maxHp = unit.maxHp;
    schema.state = unit.state;
    schema.row = unit.row;
    schema.col = unit.col;
    this.state.units.push(schema);

    console.log(`Unit deployed: ${unit.type} at (${unit.row}, ${unit.col})`);
  }

  /**
   * Start the battle simulation
   */
  private startBattle(): void {
    if (this.state.phase !== 'setup') {
      return;
    }

    if (this.state.units.length === 0) {
      return; // Need at least one unit
    }

    console.log('Battle starting...');
    this.state.phase = 'running';

    // Start simulation tick
    const tickIntervalMs = 1000 / BATTLE_TICK_RATE;
    this.tickInterval = setInterval(() => {
      this.processBattleTick();
    }, tickIntervalMs);
  }

  /**
   * Process a single battle tick
   */
  private processBattleTick(): void {
    if (!this.simulation || this.state.phase !== 'running') {
      return;
    }

    const deltaTime = 1 / BATTLE_TICK_RATE;
    processTick(this.simulation, deltaTime);

    // Update state from simulation
    this.syncState();

    // Update time remaining
    this.state.timeRemaining = Math.max(
      0,
      BATTLE_MAX_DURATION - this.simulation.tick / BATTLE_TICK_RATE
    );

    // Check if battle is over
    if (isBattleOver(this.simulation)) {
      this.endBattle();
    }
  }

  /**
   * Sync Colyseus state with simulation
   */
  private syncState(): void {
    if (!this.simulation) return;

    this.state.tick = this.simulation.tick;
    this.state.destructionPercent = calculateDestructionPercent(this.simulation);

    // Update units
    for (let i = 0; i < this.simulation.units.length; i++) {
      const simUnit = this.simulation.units[i];
      const stateUnit = this.state.units[i];
      if (stateUnit) {
        stateUnit.hp = simUnit.hp;
        stateUnit.state = simUnit.state;
        stateUnit.row = simUnit.row;
        stateUnit.col = simUnit.col;
        stateUnit.targetId = simUnit.targetId || '';
      }
    }

    // Update buildings
    for (const simBuilding of this.simulation.buildings) {
      const stateBuilding = this.state.buildings.find((b) => b.id === simBuilding.id);
      if (stateBuilding) {
        stateBuilding.hp = simBuilding.hp;
        stateBuilding.destroyed = simBuilding.destroyed;
      }
    }
  }

  /**
   * End the battle and calculate results
   */
  private async endBattle(): Promise<void> {
    if (this.state.phase === 'ended') {
      return;
    }

    console.log('Battle ending...');
    this.state.phase = 'ended';

    if (this.tickInterval) {
      clearInterval(this.tickInterval);
      this.tickInterval = null;
    }

    if (!this.simulation) {
      return;
    }

    // Calculate final results
    const destructionPercent = calculateDestructionPercent(this.simulation);
    const stars = calculateStars(destructionPercent);
    const loot = calculateLoot(destructionPercent, this.defenderResources);

    // Update result state
    this.state.result.destructionPercent = destructionPercent;
    this.state.result.stars = stars;
    this.state.result.loot.food = loot.food;
    this.state.result.loot.gold = loot.gold;
    this.state.result.loot.oil = loot.oil;

    console.log(`Battle ended: ${destructionPercent}% destruction, ${stars} stars`);
    console.log(`Loot: food=${loot.food}, gold=${loot.gold}, oil=${loot.oil}`);

    // Apply loot to attacker (in a real implementation)
    // await this.applyBattleRewards(loot);

    // Close room after a delay
    setTimeout(() => {
      this.disconnect();
    }, 5000);
  }
}
