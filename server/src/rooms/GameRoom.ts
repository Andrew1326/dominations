/**
 * GameRoom - Colyseus room for managing player game state
 */

import { Room, Client } from '@colyseus/core';
import { Schema, MapSchema, type } from '@colyseus/schema';
import type { PlaceBuildingMessage, ClientMessage, BuildingType } from '@shared/types';
import { getOrCreateGuestUser, saveUserBase } from '../services/AuthService';
import { Base, IBase, IBuilding } from '../models/Base';
import { startConstruction } from '../mechanics/ConstructionManager';
import { updateResources } from '../mechanics/ResourceCalculator';

// Colyseus Schema classes for state synchronization
class BuildingSchema extends Schema {
  @type('string') id!: string;
  @type('string') buildingType!: string;
  @type('number') row!: number;
  @type('number') col!: number;
  @type('number') level!: number;
  @type('number') constructionStartedAt: number = 0;
  @type('number') constructionEndsAt: number = 0;
}

class ResourcesSchema extends Schema {
  @type('number') food: number = 0;
  @type('number') gold: number = 0;
  @type('number') oil: number = 0;
}

class PlayerSchema extends Schema {
  @type('string') odId!: string;
  @type('string') odUsername!: string;
  @type(ResourcesSchema) resources = new ResourcesSchema();
  @type({ map: BuildingSchema }) buildings = new MapSchema<BuildingSchema>();
}

class GameState extends Schema {
  @type({ map: PlayerSchema }) players = new MapSchema<PlayerSchema>();
}

// Store MongoDB document reference for each client
interface ClientData {
  base: IBase;
  odUserId: string;
}

export class GameRoom extends Room<GameState> {
  maxClients = 1; // Single player per room for now
  private clientData = new Map<string, ClientData>();

  onCreate(_options: unknown): void {
    this.setState(new GameState());

    // Handle client messages
    this.onMessage('*', (client: Client, type: string | number, message: unknown) => {
      this.handleMessage(client, type as string, message as ClientMessage);
    });

    console.log('GameRoom created');
  }

  async onJoin(client: Client, options: { odUserId?: string; odUsername?: string }): Promise<void> {
    console.log(`Client ${client.sessionId} joining...`);

    try {
      // Get or create guest user (for MVP, all users are guests)
      const guestId = options.odUserId || client.sessionId;
      const authResult = await getOrCreateGuestUser(guestId);

      if (!authResult.success || !authResult.base || !authResult.user) {
        console.error(`Failed to load/create user: ${authResult.error}`);
        client.send('error', { type: 'error', code: 'AUTH_FAILED', message: authResult.error });
        client.leave();
        return;
      }

      // Store MongoDB document reference
      this.clientData.set(client.sessionId, {
        base: authResult.base,
        odUserId: authResult.user._id.toString(),
      });

      // Create player state from database
      const player = new PlayerSchema();
      player.odId = authResult.user._id.toString();
      player.odUsername = authResult.user.username;

      // Load resources from database
      player.resources.food = authResult.base.resources.food;
      player.resources.gold = authResult.base.resources.gold;
      player.resources.oil = authResult.base.resources.oil;

      // Load buildings from database
      for (const building of authResult.base.buildings) {
        const buildingSchema = this.buildingToSchema(building);
        player.buildings.set(building.id, buildingSchema);
      }

      this.state.players.set(client.sessionId, player);

      console.log(`Client ${client.sessionId} joined as ${authResult.user.username}`);
      console.log(`  Resources: food=${player.resources.food}, gold=${player.resources.gold}, oil=${player.resources.oil}`);
      console.log(`  Buildings: ${authResult.base.buildings.length}`);
    } catch (error) {
      console.error('Error during join:', error);
      client.send('error', { type: 'error', code: 'JOIN_FAILED', message: 'Failed to join game' });
      client.leave();
    }
  }

  async onLeave(client: Client, _consented: boolean): Promise<void> {
    console.log(`Client ${client.sessionId} leaving...`);

    try {
      // Save player data to MongoDB
      const data = this.clientData.get(client.sessionId);
      const player = this.state.players.get(client.sessionId);

      if (data && player) {
        // Update base with current state
        data.base.resources.food = player.resources.food;
        data.base.resources.gold = player.resources.gold;
        data.base.resources.oil = player.resources.oil;

        // Update buildings
        data.base.buildings = [];
        player.buildings.forEach((building) => {
          data.base.buildings.push(this.schemaToBuilding(building));
        });

        await saveUserBase(data.base);
        console.log(`Saved data for client ${client.sessionId}`);
      }
    } catch (error) {
      console.error('Error saving on leave:', error);
    }

    this.clientData.delete(client.sessionId);
    this.state.players.delete(client.sessionId);
  }

  onDispose(): void {
    console.log('GameRoom disposed');
  }

  /**
   * Convert MongoDB building to Colyseus schema
   */
  private buildingToSchema(building: IBuilding): BuildingSchema {
    const schema = new BuildingSchema();
    schema.id = building.id;
    schema.buildingType = building.type;
    schema.row = building.row;
    schema.col = building.col;
    schema.level = building.level;
    schema.constructionStartedAt = building.constructionStartedAt?.getTime() || 0;
    schema.constructionEndsAt = building.constructionEndsAt?.getTime() || 0;
    return schema;
  }

  /**
   * Convert Colyseus schema to MongoDB building
   */
  private schemaToBuilding(schema: BuildingSchema): IBuilding {
    return {
      id: schema.id,
      type: schema.buildingType as IBuilding['type'],
      row: schema.row,
      col: schema.col,
      level: schema.level,
      constructionStartedAt: schema.constructionStartedAt ? new Date(schema.constructionStartedAt) : undefined,
      constructionEndsAt: schema.constructionEndsAt ? new Date(schema.constructionEndsAt) : undefined,
    };
  }

  private handleMessage(client: Client, type: string, message: ClientMessage): void {
    const player = this.state.players.get(client.sessionId);
    if (!player) {
      console.error(`Player not found for client ${client.sessionId}`);
      return;
    }

    switch (type) {
      case 'placeBuilding':
        this.handlePlaceBuilding(client, player, message as PlaceBuildingMessage);
        break;

      case 'collectResources':
        this.handleCollectResources(client, player);
        break;

      default:
        console.warn(`Unknown message type: ${type}`);
    }
  }

  private handlePlaceBuilding(
    client: Client,
    player: PlayerSchema,
    message: PlaceBuildingMessage
  ): void {
    // Get current resources
    const currentResources = {
      food: player.resources.food,
      gold: player.resources.gold,
      oil: player.resources.oil,
    };

    // Get existing buildings as IBuilding array
    const existingBuildings: IBuilding[] = [];
    player.buildings.forEach((b) => {
      existingBuildings.push(this.schemaToBuilding(b));
    });

    // Attempt to start construction (validates resources and placement)
    const result = startConstruction(
      message.buildingType as BuildingType,
      message.row,
      message.col,
      currentResources,
      existingBuildings
    );

    if (!result.success) {
      client.send('error', {
        type: 'error',
        code: 'BUILD_FAILED',
        message: result.error,
      });
      console.log(`Build failed for ${message.buildingType}: ${result.error}`);
      return;
    }

    // Update resources
    player.resources.food = result.newResources!.food;
    player.resources.gold = result.newResources!.gold;
    player.resources.oil = result.newResources!.oil;

    // Add building to player state
    const buildingSchema = this.buildingToSchema(result.building!);
    player.buildings.set(result.building!.id, buildingSchema);

    // Send success message
    client.send('buildingPlaced', {
      type: 'buildingPlaced',
      building: {
        id: result.building!.id,
        type: result.building!.type,
        row: result.building!.row,
        col: result.building!.col,
        level: result.building!.level,
        constructionEndsAt: result.building!.constructionEndsAt?.getTime(),
      },
    });

    console.log(`Building ${result.building!.id} placed at (${result.building!.row}, ${result.building!.col})`);
    console.log(`  Resources remaining: food=${player.resources.food}, gold=${player.resources.gold}`);
  }

  private handleCollectResources(client: Client, player: PlayerSchema): void {
    // Get client data for last update time
    const data = this.clientData.get(client.sessionId);
    if (!data) {
      client.send('error', { type: 'error', code: 'NO_DATA', message: 'Player data not found' });
      return;
    }

    // Get existing buildings
    const buildings: IBuilding[] = [];
    player.buildings.forEach((b) => {
      buildings.push(this.schemaToBuilding(b));
    });

    // Calculate updated resources
    const currentResources = {
      food: player.resources.food,
      gold: player.resources.gold,
      oil: player.resources.oil,
    };

    const updatedResources = updateResources(
      currentResources,
      buildings,
      data.base.resourcesLastUpdated
    );

    // Update player state
    player.resources.food = updatedResources.food;
    player.resources.gold = updatedResources.gold;
    player.resources.oil = updatedResources.oil;

    // Update last updated time
    data.base.resourcesLastUpdated = new Date();

    console.log(`Resources collected: food=${updatedResources.food}, gold=${updatedResources.gold}, oil=${updatedResources.oil}`);
  }
}
