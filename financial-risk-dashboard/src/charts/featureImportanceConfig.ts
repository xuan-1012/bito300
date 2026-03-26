/**
 * Feature Importance Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { FeatureImportanceData } from '../types';

export function getFeatureImportanceOptions(data: FeatureImportanceData): EChartsOption {
  // Sort by importance and take top 10
  const sortedIndices = data.importance
    .map((value, index) => ({ value, index }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  const topFeatures = sortedIndices.map(item => data.features[item.index]);
  const topImportance = sortedIndices.map(item => item.value);

  return {
    title: {
      text: 'Feature Importance (Top 10)',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
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
      type: 'value',
      name: 'Importance',
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: {
      type: 'category',
      name: 'Feature',
      data: topFeatures,
      axisLabel: {
        interval: 0,
        rotate: 0,
      },
    },
    series: [
      {
        name: 'Importance',
        type: 'bar',
        data: topImportance,
        itemStyle: {
          color: '#8b5cf6',
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}',
        },
      },
    ],
  };
}
