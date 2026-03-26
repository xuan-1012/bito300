/**
 * Chart Container Component
 * 
 * Wraps ECharts with common functionality like export and error handling
 */

import React, { useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import { useChartResize } from '../hooks';

interface ChartContainerProps {
  title: string;
  options: EChartsOption;
  height?: number | string;
  className?: string;
}

export function ChartContainer({
  title,
  options,
  height = 400,
  className = '',
}: ChartContainerProps) {
  const chartRef = useRef<any>(null);
  
  // Auto-resize chart on window resize
  useChartResize(chartRef);

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <ReactECharts
        ref={chartRef}
        option={options}
        style={{ height: typeof height === 'number' ? `${height}px` : height }}
        opts={{ renderer: 'canvas' }}
        notMerge={true}
        lazyUpdate={true}
      />
    </div>
  );
}
