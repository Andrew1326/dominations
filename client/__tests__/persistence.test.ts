/**
 * Persistence Tests - localStorage save/load functionality
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import type { BaseLayout, BuildingData, BuildingType } from '../../shared/types';
import { STORAGE_KEY, BUILDINGS } from '../../shared/constants';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(global, 'localStorage', { value: localStorageMock });

describe('Persistence', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  describe('BuildingData serialization', () => {
    it('creates valid BuildingData structure', () => {
      const buildingData: BuildingData = {
        id: 'townCenter_123_abc',
        type: 'townCenter',
        row: 5,
        col: 5,
      };

      expect(buildingData.id).toBeDefined();
      expect(buildingData.type).toBe('townCenter');
      expect(buildingData.row).toBe(5);
      expect(buildingData.col).toBe(5);
    });

    it('validates building type matches definition', () => {
      const types: BuildingType[] = ['townCenter', 'house', 'farm'];

      types.forEach((type) => {
        expect(BUILDINGS[type]).toBeDefined();
        expect(BUILDINGS[type].type).toBe(type);
      });
    });
  });

  describe('BaseLayout serialization', () => {
    it('serializes layout to JSON correctly', () => {
      const layout: BaseLayout = {
        buildings: [
          { id: 'townCenter_1', type: 'townCenter', row: 5, col: 5 },
          { id: 'house_1', type: 'house', row: 2, col: 8 },
          { id: 'farm_1', type: 'farm', row: 10, col: 3 },
        ],
        lastSaved: Date.now(),
      };

      const json = JSON.stringify(layout);
      const parsed = JSON.parse(json) as BaseLayout;

      expect(parsed.buildings).toHaveLength(3);
      expect(parsed.buildings[0].type).toBe('townCenter');
      expect(parsed.buildings[1].type).toBe('house');
      expect(parsed.buildings[2].type).toBe('farm');
    });

    it('preserves building positions through serialization', () => {
      const layout: BaseLayout = {
        buildings: [
          { id: 'test_1', type: 'townCenter', row: 7, col: 12 },
        ],
        lastSaved: Date.now(),
      };

      const json = JSON.stringify(layout);
      const parsed = JSON.parse(json) as BaseLayout;

      expect(parsed.buildings[0].row).toBe(7);
      expect(parsed.buildings[0].col).toBe(12);
    });
  });

  describe('localStorage operations', () => {
    it('saves layout to localStorage', () => {
      const layout: BaseLayout = {
        buildings: [
          { id: 'townCenter_1', type: 'townCenter', row: 5, col: 5 },
        ],
        lastSaved: Date.now(),
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));

      expect(localStorage.setItem).toHaveBeenCalledWith(
        STORAGE_KEY,
        expect.any(String)
      );
    });

    it('loads layout from localStorage', () => {
      const layout: BaseLayout = {
        buildings: [
          { id: 'townCenter_1', type: 'townCenter', row: 5, col: 5 },
          { id: 'house_1', type: 'house', row: 8, col: 2 },
        ],
        lastSaved: 1234567890,
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));

      const saved = localStorage.getItem(STORAGE_KEY);
      expect(saved).not.toBeNull();

      const loaded = JSON.parse(saved!) as BaseLayout;
      expect(loaded.buildings).toHaveLength(2);
      expect(loaded.lastSaved).toBe(1234567890);
    });

    it('returns null for missing layout', () => {
      const saved = localStorage.getItem(STORAGE_KEY);
      expect(saved).toBeNull();
    });

    it('handles multiple buildings with unique IDs', () => {
      const layout: BaseLayout = {
        buildings: [
          { id: 'house_1', type: 'house', row: 2, col: 2 },
          { id: 'house_2', type: 'house', row: 2, col: 5 },
          { id: 'house_3', type: 'house', row: 5, col: 2 },
        ],
        lastSaved: Date.now(),
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
      const loaded = JSON.parse(localStorage.getItem(STORAGE_KEY)!) as BaseLayout;

      const ids = loaded.buildings.map((b) => b.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('clears layout when removed', () => {
      const layout: BaseLayout = {
        buildings: [{ id: 'test', type: 'farm', row: 0, col: 0 }],
        lastSaved: Date.now(),
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
      localStorage.removeItem(STORAGE_KEY);

      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    });
  });

  describe('building placement restoration', () => {
    it('restores buildings to correct grid positions', () => {
      const savedBuildings: BuildingData[] = [
        { id: 'tc_1', type: 'townCenter', row: 8, col: 8 },
        { id: 'h_1', type: 'house', row: 3, col: 12 },
        { id: 'f_1', type: 'farm', row: 15, col: 5 },
      ];

      const layout: BaseLayout = {
        buildings: savedBuildings,
        lastSaved: Date.now(),
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
      const loaded = JSON.parse(localStorage.getItem(STORAGE_KEY)!) as BaseLayout;

      // Verify each building has correct position
      loaded.buildings.forEach((building, index) => {
        expect(building.row).toBe(savedBuildings[index].row);
        expect(building.col).toBe(savedBuildings[index].col);
        expect(building.type).toBe(savedBuildings[index].type);
      });
    });

    it('validates building types during restoration', () => {
      const loaded: BaseLayout = {
        buildings: [
          { id: 'tc', type: 'townCenter', row: 0, col: 0 },
          { id: 'h', type: 'house', row: 5, col: 5 },
          { id: 'f', type: 'farm', row: 10, col: 10 },
        ],
        lastSaved: Date.now(),
      };

      // All building types should have valid definitions
      loaded.buildings.forEach((building) => {
        const def = BUILDINGS[building.type];
        expect(def).toBeDefined();
        expect(def.width).toBeGreaterThan(0);
        expect(def.height).toBeGreaterThan(0);
      });
    });
  });
});
