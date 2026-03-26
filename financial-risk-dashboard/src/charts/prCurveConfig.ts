/**
 * Precision-Recall Curve Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { PRCurveData } from '../types';

export function getPRCurveOptions(data: PRCurveData): EChartsOption {
  const chartData = data.recall.map((recall, index) => [recall, data.precision[index]]);

  return {
    title: {
      text: `PR Curve (AP: ${data.average_precision.toFixed(3)})`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const point = params[0];
        return `Recall: ${point.value[0].toFixed(3)}<br/>Precision: ${point.value[1].toFixed(3)}`;
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
      name: 'Recall',
      nameLocation: 'middle',
      nameGap: 30,
      min: 0,
      max: 1,
    },
    yAxis: {
      type: 'value',
      name: 'Precision',
      nameLocation: 'middle',
      nameGap: 50,
      min: 0,
      max: 1,
    },
    series: [
      {
        name: 'PR Curve',
        type: 'line',
        data: chartData,
        smooth: false,
        lineStyle: {
          color: '#8b5cf6',
          width: 2,
        },
        itemStyle: {
          color: '#8b5cf6',
        },
        showSymbol: false,
      },
    ],
  };
}
