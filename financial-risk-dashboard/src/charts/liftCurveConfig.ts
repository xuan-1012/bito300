/**
 * Lift Curve Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { LiftCurveData } from '../types';

export function getLiftCurveOptions(data: LiftCurveData): EChartsOption {
  return {
    title: {
      text: 'Lift Curve',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['Model', 'Baseline'],
      top: 30,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    toolbox: {
      feature: {
        saveAsImage: { title: 'Save' },
      },
    },
    xAxis: {
      type: 'category',
      name: 'Percentile',
      nameLocation: 'middle',
      nameGap: 30,
      data: data.percentiles.map(p => `${p}%`),
    },
    yAxis: {
      type: 'value',
      name: 'Cumulative Positives',
      nameLocation: 'middle',
      nameGap: 50,
    },
    series: [
      {
        name: 'Model',
        type: 'line',
        data: data.cumulative_positives,
        smooth: true,
        lineStyle: {
          color: '#3b82f6',
          width: 2,
        },
        itemStyle: {
          color: '#3b82f6',
        },
        areaStyle: {
          color: 'rgba(59, 130, 246, 0.1)',
        },
      },
      {
        name: 'Baseline',
        type: 'line',
        data: data.baseline,
        smooth: false,
        lineStyle: {
          color: '#9ca3af',
          width: 2,
          type: 'dashed',
        },
        itemStyle: {
          color: '#9ca3af',
        },
      },
    ],
  };
}
