/**
 * NetworkService - Client-side connection to Colyseus server
 */

import * as Colyseus from 'colyseus.js';
import type { BuildingType, Resources, BuildingData, MatchFoundMessage, NoMatchFoundMessage } from '@shared/types';
import { DEFAULT_SERVER_URL } from '@shared/constants';

export interface ServerState {
  resources: Resources;
  buildings: Map<string, BuildingData>;
}

export type StateChangeCallback = (state: ServerState) => void;
export type ErrorCallback = (error: { code: string; message: string }) => void;
export type BuildingPlacedCallback = (building: BuildingData) => void;
export type MatchFoundCallback = (attackerId: string, opponent: MatchFoundMessage['opponent']) => void;
export type NoMatchCallback = (reason: string) => void;

class NetworkService {
  private client: Colyseus.Client | null = null;
  private room: Colyseus.Room | null = null;
  private connected = false;

  // Callbacks
  private onStateChange: StateChangeCallback | null = null;
  private onError: ErrorCallback | null = null;
  private onBuildingPlaced: BuildingPlacedCallback | null = null;
  private onMatchFoundCallback: MatchFoundCallback | null = null;
  private onNoMatchCallback: NoMatchCallback | null = null;

  /**
   * Check if connected to server
   */
  isConnected(): boolean {
    return this.connected && this.room !== null;
  }

  /**
   * Connect to the game server
   */
  async connect(serverUrl: string = DEFAULT_SERVER_URL): Promise<boolean> {
    try {
      console.log(`Connecting to server: ${serverUrl}`);
      this.client = new Colyseus.Client(serverUrl);

      // Generate or get guest ID (server adds 'guest_' prefix, so keep this short)
      let guestId = localStorage.getItem('opencivilizations_guest_id');
      if (!guestId) {
        // Generate short ID: 8 random chars (server will prefix with 'guest_' for 14 total)
        guestId = Math.random().toString(36).substr(2, 8) + Math.random().toString(36).substr(2, 8);
        localStorage.setItem('opencivilizations_guest_id', guestId);
      }

      // Join or create game room
      this.room = await this.client.joinOrCreate('game', {
        odUserId: guestId,
      });

      this.connected = true;
      console.log('Connected to room:', this.room.sessionId);

      // Set up state synchronization
      this.setupStateSync();

      return true;
    } catch (error) {
      console.error('Failed to connect:', error);
      this.connected = false;
      return false;
    }
  }

  /**
   * Disconnect from the server
   */
  async disconnect(): Promise<void> {
    if (this.room) {
      await this.room.leave();
      this.room = null;
    }
    this.connected = false;
    console.log('Disconnected from server');
  }

  /**
   * Set up state synchronization listeners
   */
  private setupStateSync(): void {
    if (!this.room) return;

    // Listen for state changes
    this.room.state.players.onAdd((player: any, sessionId: string) => {
      if (sessionId === this.room?.sessionId) {
        console.log('Player state added:', sessionId);
        this.notifyStateChange(player);

        // Listen for resource changes
        player.resources.onChange(() => {
          this.notifyStateChange(player);
        });

        // Listen for building changes
        player.buildings.onAdd((_building: any, id: string) => {
          console.log('Building added:', id);
          this.notifyStateChange(player);
        });

        player.buildings.onRemove((_building: any, id: string) => {
          console.log('Building removed:', id);
          this.notifyStateChange(player);
        });
      }
    });

    // Listen for server messages
    this.room.onMessage('error', (message: { code: string; message: string }) => {
      console.error('Server error:', message);
      if (this.onError) {
        this.onError(message);
      }
    });

    this.room.onMessage('buildingPlaced', (message: { building: BuildingData }) => {
      console.log('Building placed:', message.building);
      if (this.onBuildingPlaced) {
        this.onBuildingPlaced(message.building);
      }
    });

    // Matchmaking messages
    this.room.onMessage('matchFound', (message: MatchFoundMessage) => {
      console.log('Match found:', message.opponent.username);
      if (this.onMatchFoundCallback) {
        this.onMatchFoundCallback(message.attackerId, message.opponent);
      }
    });

    this.room.onMessage('noMatchFound', (message: NoMatchFoundMessage) => {
      console.log('No match found:', message.reason);
      if (this.onNoMatchCallback) {
        this.onNoMatchCallback(message.reason);
      }
    });
  }

  /**
   * Notify state change callback
   */
  private notifyStateChange(player: any): void {
    if (!this.onStateChange) return;

    const state: ServerState = {
      resources: {
        food: player.resources.food,
        gold: player.resources.gold,
        oil: player.resources.oil,
      },
      buildings: new Map(),
    };

    player.buildings.forEach((building: any, id: string) => {
      state.buildings.set(id, {
        id: building.id,
        type: building.buildingType as BuildingType,
        row: building.row,
        col: building.col,
        level: building.level,
        constructionStartedAt: building.constructionStartedAt || undefined,
        constructionEndsAt: building.constructionEndsAt || undefined,
      });
    });

    this.onStateChange(state);
  }

  /**
   * Send place building request to server
   */
  placeBuilding(buildingType: BuildingType, row: number, col: number): void {
    if (!this.room) {
      console.error('Not connected to server');
      return;
    }

    this.room.send('placeBuilding', {
      type: 'placeBuilding',
      buildingType,
      row,
      col,
    });
  }

  /**
   * Send collect resources request to server
   */
  collectResources(): void {
    if (!this.room) {
      console.error('Not connected to server');
      return;
    }

    this.room.send('collectResources', {
      type: 'collectResources',
    });
  }

  /**
   * Register state change callback
   */
  onState(callback: StateChangeCallback): void {
    this.onStateChange = callback;
  }

  /**
   * Register error callback
   */
  onServerError(callback: ErrorCallback): void {
    this.onError = callback;
  }

  /**
   * Register building placed callback
   */
  onBuilding(callback: BuildingPlacedCallback): void {
    this.onBuildingPlaced = callback;
  }

  /**
   * Get current resources from server state
   */
  getResources(): Resources | null {
    if (!this.room) return null;

    const player = this.room.state.players.get(this.room.sessionId);
    if (!player) return null;

    return {
      food: player.resources.food,
      gold: player.resources.gold,
      oil: player.resources.oil,
    };
  }

  /**
   * Send find match request to server
   */
  findMatch(): void {
    if (!this.room) {
      console.error('Not connected to server');
      return;
    }

    this.room.send('findMatch', {
      type: 'findMatch',
    });
  }

  /**
   * Register match found callback
   */
  onMatchFound(callback: MatchFoundCallback): void {
    this.onMatchFoundCallback = callback;
  }

  /**
   * Register no match found callback
   */
  onNoMatch(callback: NoMatchCallback): void {
    this.onNoMatchCallback = callback;
  }
}

// Export singleton instance
export const networkService = new NetworkService();
