/**
 * Building Catalog Tests - the data behind the "Add Building" menu.
 */

import { describe, it, expect } from 'vitest';
import {
  getBuildingCatalog,
  getBuildingImageUrl,
  getBuildingTexture,
  hasBuildingImage,
  colorToHex,
  formatCost,
} from '../src/game/ui/buildingCatalog';
import { BUILDINGS, BUILDING_COSTS, AGE_ORDER } from '../../shared/constants';
import { BUILDING_IMAGE_AGES } from '../src/game/ui/buildingImageManifest';
import type { BuildingType } from '../../shared/types';

describe('buildingCatalog', () => {
  describe('getBuildingCatalog', () => {
    const catalog = getBuildingCatalog();

    it('includes every building type exactly once', () => {
      const allTypes = Object.keys(BUILDINGS) as BuildingType[];
      expect(catalog).toHaveLength(allTypes.length);

      const catalogTypes = catalog.map((e) => e.type).sort();
      expect(catalogTypes).toEqual([...allTypes].sort());
    });

    it('carries the correct name, size and cost for each entry', () => {
      for (const entry of catalog) {
        const def = BUILDINGS[entry.type];
        expect(entry.name).toBe(def.name);
        expect(entry.width).toBe(def.width);
        expect(entry.height).toBe(def.height);
        expect(entry.cost).toEqual(BUILDING_COSTS[entry.type]);
      }
    });

    it('is sorted by age progression', () => {
      for (let i = 1; i < catalog.length; i++) {
        const prev = AGE_ORDER.indexOf(catalog[i - 1].age);
        const curr = AGE_ORDER.indexOf(catalog[i].age);
        expect(curr).toBeGreaterThanOrEqual(prev);
      }
    });

    it('places known stone-age buildings first', () => {
      const firstAge = catalog[0].age;
      expect(firstAge).toBe('stone');
      const stoneTypes = catalog.filter((e) => e.age === 'stone').map((e) => e.type);
      expect(stoneTypes).toContain('townCenter');
      expect(stoneTypes).toContain('house');
      expect(stoneTypes).toContain('farm');
    });

    it('resolves an image url only for buildings that have a render', () => {
      for (const entry of catalog) {
        expect(entry.imageUrl).toBe(getBuildingImageUrl(entry.type));
        expect(entry.color).toMatch(/^#[0-9a-f]{6}$/);
        if (BUILDING_IMAGE_AGES[entry.type]) {
          expect(entry.imageUrl).toBeDefined();
        } else {
          expect(entry.imageUrl).toBeUndefined();
        }
      }
    });
  });

  describe('getBuildingImageUrl', () => {
    it('prefers the unlock age when art exists there', () => {
      // townCenter and farm both have a stone-age render
      expect(getBuildingImageUrl('townCenter')).toBe('assets/buildings/stone/romans/townCenter.png');
      expect(getBuildingImageUrl('farm')).toBe('assets/buildings/stone/romans/farm.png');
    });

    it('falls back to an age that has art when the unlock age has none', () => {
      // goldMine unlocks in bronze but is only rendered for medieval
      expect(getBuildingImageUrl('goldMine')).toBe('assets/buildings/medieval/romans/goldMine.png');
      expect(getBuildingImageUrl('tower')).toBe('assets/buildings/medieval/romans/tower.png');
    });

    it('returns undefined for buildings with no render', () => {
      // No Blender model/render exists for these yet
      expect(getBuildingImageUrl('blacksmith')).toBeUndefined();
      expect(getBuildingImageUrl('castle')).toBeUndefined();
      expect(getBuildingImageUrl('dataCentre')).toBeUndefined();
    });

    it('respects the nation argument', () => {
      expect(getBuildingImageUrl('farm', 'greeks')).toBe('assets/buildings/stone/greeks/farm.png');
    });
  });

  describe('hasBuildingImage / getBuildingTexture', () => {
    it('reports whether a building has a render', () => {
      expect(hasBuildingImage('townCenter')).toBe(true);
      expect(hasBuildingImage('goldMine')).toBe(true);
      expect(hasBuildingImage('blacksmith')).toBe(false);
    });

    it('builds a stable texture key + url for rendered buildings', () => {
      const tex = getBuildingTexture('barracks');
      expect(tex).toEqual({
        key: 'building-barracks',
        url: 'assets/buildings/medieval/romans/barracks.png',
      });
    });

    it('returns undefined texture for buildings with no render', () => {
      expect(getBuildingTexture('castle')).toBeUndefined();
    });
  });

  describe('colorToHex', () => {
    it('formats numeric colors as zero-padded css hex', () => {
      expect(colorToHex(0x8b4513)).toBe('#8b4513');
      expect(colorToHex(0x0000ff)).toBe('#0000ff');
      expect(colorToHex(0x000000)).toBe('#000000');
    });
  });

  describe('formatCost', () => {
    it('formats present resources with emoji', () => {
      expect(formatCost({ gold: 150 })).toBe('💰150');
      expect(formatCost({ gold: 1000, food: 500 })).toBe('💰1000  🍖500');
      expect(formatCost({ gold: 10000, food: 6000, oil: 2000 })).toBe('💰10000  🍖6000  🛢️2000');
    });

    it('shows Free for an empty cost', () => {
      expect(formatCost({})).toBe('Free');
    });
  });
});
