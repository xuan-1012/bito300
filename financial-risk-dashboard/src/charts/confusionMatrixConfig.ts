/**
 * Confusion Matrix Chart Configuration
 */

import type { EChartsOption } from 'echarts';
import type { ConfusionMatrixData } from '../types';

export function getConfusionMatrixOptions(data: ConfusionMatrixData): EChartsOption {
  const { matrix, labels } = data;
  
  // Flatten matrix for heatmap
  const heatmapData: [number, number, number][] = [];
  matrix.forEach((row, i) => {
    row.forEach((value, j) => {
      heatmapData.push([j, i, value]);
    });
  });

  // Find max value for color scale
  const maxValue = Math.max(...matrix.flat());

  return {
    title: {
      text: 'Confusion Matrix',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
      },
    },
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const [x, y, value] = params.data;
        return `Predicted: ${labels[x]}<br/>Actual: ${labels[y]}<br/>Count: ${value}`;
      },
    },
    grid: {
      left: '15%',
      right: '10%',
      bottom: '15%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: labels,
      name: 'Predicted',
      nameLocation: 'middle',
      nameGap: 30,
      splitArea: {
        show: true,
      },
    },
    yAxis: {
      type: 'category',
      data: labels,
      name: 'Actual',
      nameLocation: 'middle',
      nameGap: 40,
      splitArea: {
        show: true,
      },
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#f0f9ff', '#0ea5e9', '#0369a1'],
      },
    },
    series: [
      {
        name: 'Confusion Matrix',
        type: 'heatmap',
        data: heatmapData,
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
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
