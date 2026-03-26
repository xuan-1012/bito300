/**
 * Validation Curve Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { ValidationCurveData } from '../types';

export function getValidationCurveOptions(data: ValidationCurveData): EChartsOption {
  return {
    title: {
      text: `Validation Curve (${data.param_name})`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['Training Score', 'Validation Score'],
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
      name: data.param_name,
      nameLocation: 'middle',
      nameGap: 30,
      data: data.param_values.map(String),
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
        name: 'Training Score',
        type: 'line',
        data: data.train_scores,
        smooth: true,
        lineStyle: {
          color: '#3b82f6',
          width: 2,
        },
        itemStyle: {
          color: '#3b82f6',
        },
      },
      {
        name: 'Validation Score',
        type: 'line',
        data: data.validation_scores,
        smooth: true,
        lineStyle: {
          color: '#10b981',
          width: 2,
        },
        itemStyle: {
          color: '#10b981',
        },
      },
    ],
  };
}
