/**
 * Threshold Analysis Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { ThresholdAnalysisData } from '../types';

export function getThresholdAnalysisOptions(data: ThresholdAnalysisData): EChartsOption {
  return {
    title: {
      text: `Threshold Analysis (Optimal: ${data.optimal_threshold.toFixed(3)})`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['Precision', 'Recall', 'F1 Score'],
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
      name: 'Threshold',
      nameLocation: 'middle',
      nameGap: 30,
      data: data.thresholds.map(t => t.toFixed(2)),
    },
    yAxis: {
      type: 'value',
      name: 'Score',
      nameLocation: 'middle',
      nameGap: 50,
      min: 0,
      max: 1,
    },
    series: [
      {
        name: 'Precision',
        type: 'line',
        data: data.precision,
        smooth: true,
        lineStyle: {
          color: '#3b82f6',
          width: 2,
        },
      },
      {
        name: 'Recall',
        type: 'line',
        data: data.recall,
        smooth: true,
        lineStyle: {
          color: '#10b981',
          width: 2,
        },
      },
      {
        name: 'F1 Score',
        type: 'line',
        data: data.f1_score,
        smooth: true,
        lineStyle: {
          color: '#f59e0b',
          width: 2,
        },
      },
      {
        name: 'Optimal Threshold',
        type: 'line',
        markLine: {
          silent: true,
          lineStyle: {
            color: '#ef4444',
            type: 'dashed',
            width: 2,
          },
          data: [
            {
              xAxis: data.optimal_threshold.toFixed(2),
              label: {
                formatter: 'Optimal',
              },
            },
          ],
        },
      },
    ],
  };
}
