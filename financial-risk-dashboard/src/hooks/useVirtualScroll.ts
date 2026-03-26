import { useState, useMemo } from 'react';
import type { Account } from '../types';

// Virtual scroll configuration
export interface VirtualScrollConfig {
  itemHeight: number;
  containerHeight: number;
  overscan: number;
}

// Virtual scroll result
export interface VirtualScrollResult {
  visibleItems: Account[];
  totalHeight: number;
  offsetY: number;
  onScroll: (e: React.UIEvent<HTMLDivElement>) => void;
}

/**
 * Custom hook for virtual scrolling optimization
 * Only renders visible items plus overscan buffer
 * 
 * @param items - Array of accounts to virtualize
 * @param config - Virtual scroll configuration
 * @returns Virtual scroll result with visible items and handlers
 */
export function useVirtualScroll(
  items: Account[],
  config: VirtualScrollConfig
): VirtualScrollResult {
  const [scrollTop, setScrollTop] = useState(0);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / config.itemHeight);
    const visibleCount = Math.ceil(config.containerHeight / config.itemHeight);
    const end = start + visibleCount + config.overscan;

    return {
      start: Math.max(0, start - config.overscan),
      end: Math.min(items.length, end),
    };
  }, [scrollTop, items.length, config.itemHeight, config.containerHeight, config.overscan]);

  // Get visible items
  const visibleItems = useMemo(
    () => items.slice(visibleRange.start, visibleRange.end),
    [items, visibleRange.start, visibleRange.end]
  );

  // Scroll handler
  const onScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return {
    visibleItems,
    totalHeight: items.length * config.itemHeight,
    offsetY: visibleRange.start * config.itemHeight,
    onScroll,
  };
}
