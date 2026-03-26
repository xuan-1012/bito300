/**
 * ROC Curve Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { ROCCurveData } from '../types';

export function getROCCurveOptions(data: ROCCurveData): EChartsOption {
  const { fpr, tpr, auc } = data;

  return {
    title: {
      text: `ROC Curve (AUC = ${auc.toFixed(4)})`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
      },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const point = params[0];
        return `FPR: ${point.data[0].toFixed(4)}<br/>TPR: ${point.data[1].toFixed(4)}`;
      },
    },
    legend: {
      data: ['ROC Curve', 'Random Classifier'],
      bottom: 10,
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: 'False Positive Rate',
      nameLocation: 'middle',
      nameGap: 30,
      min: 0,
      max: 1,
      axisLabel: {
        formatter: '{value}',
      },
    },
    yAxis: {
      type: 'value',
      name: 'True Positive Rate',
      nameLocation: 'middle',
      nameGap: 40,
      min: 0,
      max: 1,
      axisLabel: {
        formatter: '{value}',
      },
    },
    series: [
      {
        name: 'ROC Curve',
        type: 'line',
        data: fpr.map((x, i) => [x, tpr[i]]),
        smooth: false,
        lineStyle: {
          width: 2,
          color: '#3b82f6',
        },
        symbol: 'none',
      },
      {
        name: 'Random Classifier',
        type: 'line',
        data: [
          [0, 0],
          [1, 1],
        ],
        lineStyle: {
          type: 'dashed',
          width: 2,
          color: '#9ca3af',
        },
        symbol: 'none',
      },
    ],
    toolbox: {
      feature: {
        saveAsImage: {
          title: 'Save as Image',
          pixelRatio: 2,
        },
      },
      right: 20,
      top: 20,
    },
  };
}
