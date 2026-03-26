/**
 * Custom hook for responsive chart resizing
 */

import { useEffect, useRef, RefObject } from 'react';
import type { EChartsOption } from 'echarts';

interface UseChartResizeOptions {
  debounceMs?: number;
}

export const useChartResize = (
  chartRef: RefObject<any>,
  options?: UseChartResizeOptions
) => {
  const { debounceMs = 300 } = options || {};
  const timeoutRef = useRef<NodeJS.Timeout>();
  
  useEffect(() => {
    const handleResize = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        if (chartRef.current) {
          const echartsInstance = chartRef.current.getEchartsInstance();
          if (echartsInstance) {
            echartsInstance.resize();
          }
        }
      }, debounceMs);
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [chartRef, debounceMs]);
};
