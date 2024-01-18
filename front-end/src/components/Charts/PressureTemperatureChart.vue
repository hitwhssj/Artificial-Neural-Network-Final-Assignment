<template>
  <div :id="id" :class="className" :style="{height:height,width:width}" class="pressure-temperature-chart-container" />
</template>

<script>
import resize from './mixins/resize'
import { mapState } from 'vuex'

export default {
  name: 'PressureTemperatureChart',
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: 'pressure-temperature-chart-container'
    },
    id: {
      type: String,
      default: 'pressureTemperatureChart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '100%'
    }
  },
  data() {
    return {
      pressureTemperatureChart: null,
      line1: [
        [344.7, 15.5],
        [342.6, 15.1],
        [337.1, 14.1],
        [331.3, 13.1],
        [325.1, 12.1],
        [318.5, 11.1],
        [311.5, 10.1],
        [303.9, 9.1],
        [295.6, 8.1],
        [286.6, 7.1],
        [276.5, 6.1],
        [265.0, 5.1],
        [251.7, 4.1],
        [235.6, 3.1],
        [214.8, 2.1],
        [184.1, 1.1],
        [99.7, 0.1],
        [81.4, 0.05],
        [60.6, 0.02]
      ],
      line2: [
        [329.7, 16.5],
        [323.9, 15.5],
        [317.8, 14.5],
        [311.3, 13.5],
        [304.3, 12.5],
        [296.8, 11.5],
        [288.6, 10.5],
        [279.7, 9.5],
        [269.7, 8.5],
        [258.5, 7.5],
        [245.4, 6.5],
        [233.2, 5.7],
        [193.8, 3.5],
        [180.6, 3.1],
        [163.4, 2.7],
        [96.8, 2],
        [60.0, 2]
      ],
      line3: [
        [319.7, 16.5],
        [313.9, 15.5],
        [307.8, 14.5],
        [301.3, 13.5],
        [294.3, 12.5],
        [286.8, 11.5],
        [278.6, 10.5],
        [269.7, 9.5],
        [259.7, 8.5],
        [248.5, 7.5],
        [235.4, 6.5],
        [223.2, 5.7],
        [183.8, 3.5],
        [177.6, 3.3],
        [153.4, 2.7],
        [48.0, 2.7]
      ],
      line4: [
        [274.7, 16.5],
        [268.9, 15.5],
        [262.8, 14.5],
        [256.3, 13.5],
        [249.3, 12.5],
        [241.8, 11.5],
        [233.6, 10.5],
        [224.7, 9.5],
        [214.7, 8.5],
        [203.5, 7.5],
        [190.4, 6.5],
        [187.4, 6.29],
        [138.8, 3.5],
        [132.6, 3.3],
        [125.6, 3.1],
        [121.8, 3],
        [117.7, 2.9],
        [51.9, 2.9]
      ],
      line5: [
        [169.9, 16.5],
        [164.7, 15.5],
        [162.6, 15.1],
        [157.1, 14.1],
        [151.3, 13.1],
        [145.1, 12.1],
        [138.5, 11.1],
        [131.5, 10.1],
        [123.9, 9.1],
        [115.6, 8.1],
        [106.6, 7.1],
        [96.5, 6.1],
        [85.0, 5.1],
        [71.7, 4.1],
        [55.6, 3.1],
        [34.8, 2.1],
        [4.1, 1.1],
        [0.0, 1.0024]
      ]
    }
  },
  computed: {
    ...mapState('wsdata', ['pressureTemperatureChartData']),
    lastSymbolData() {
      if (this.pressureTemperatureChartData.length > 0) {
        return [
          ...this.pressureTemperatureChartData.slice(0, this.pressureTemperatureChartData.length - 1),
          { value: this.pressureTemperatureChartData[this.pressureTemperatureChartData.length - 1], symbol: 'circle' }
        ]
      } else {
        return []
      }
    }
  },
  watch: {
    pressureTemperatureChartData: {
      deep: true,
      handler() {
        this.updatePressureTemperatureChart()
      }
      // immediate: true
    }
  },
  mounted() {
    // console.log('p t mounted')
    this.$nextTick(() => {
      this.initPressureTemperatureChart()
      this.updatePressureTemperatureChart()
    })
  },
  beforeDestroy() {
    if (!this.pressureTemperatureChart) {
      return
    }
    this.pressureTemperatureChart.dispose()
    this.pressureTemperatureChart = null
  },
  methods: {
    initPressureTemperatureChart() {
      this.pressureTemperatureChart = this.$echarts.init(document.getElementById(this.id))
      this.pressureTemperatureChart.showLoading()
    },
    updatePressureTemperatureChart() {
      if (this.pressureTemperatureChartData === undefined || this.pressureTemperatureChart === null) {
        return
      }
      this.pressureTemperatureChart.hideLoading()
      this.pressureTemperatureChart.setOption({
        // backgroundColor: '#344b58',
        backgroundColor: '#eff7fb',
        // title: {
        //   text: 'analysis',
        //   x: '20',
        //   top: '10',
        //   textStyle: {
        //     // color: '#fff',
        //     fontSize: '20'
        //   },
        //   subtextStyle: {
        //     // color: '#90979c',
        //     fontSize: '16'
        //   }
        // },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            textStyle: {
              // color: '#fff'
            }
          }
        },
        grid: {
          left: '9%',
          right: '5%',
          borderWidth: 0,
          top: '12%',
          bottom: '16%',
          textStyle: {
            // color: '#fff'
          }
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        },
        legend: {
          x: '5%',
          top: '2%',
          textStyle: {
            // color: '#90979c'
          },
          data: ['P-T']
        },
        calculable: true,
        xAxis: [{
          name: 'T(℃)',
          // min: 0,
          // max: 400,
          axisLine: {
            lineStyle: {
              // color: '#90979c'
            }
          },
          splitLine: {
            show: true
          },
          axisTick: {
            show: false
            // length: 6,
            // lineStyle: {
            //   type: 'dashed'
            //   // ...
            // }
          },
          splitArea: {
            show: true
          },
          axisLabel: {
            interval: 0
          }
        }],
        yAxis: [{
          name: 'P(MW)',
          // min: 0,
          // max: 20,
          // boundaryGap: ['1', '1'],
          splitLine: {
            show: true
          },
          axisLine: {
            lineStyle: {
              // color: '#90979c'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            interval: 0
          },
          splitArea: {
            show: true
          }
        }],
        dataZoom: [{
          // type: 'slider',
          show: true,
          // height: '65%',
          // width: '2%',
          yAxisIndex: [
            0
          ],
          // top: '15%',
          left: '2%',
          start: 0,
          end: 100,
          handleIcon: 'path://M306.1,413c0,2.2-1.8,4-4,4h-59.8c-2.2,0-4-1.8-4-4V200.8c0-2.2,1.8-4,4-4h59.8c2.2,0,4,1.8,4,4V413z',
          handleSize: '110%',
          handleStyle: {
            // color: '#d3dee5'
          },
          textStyle: {
            // color: '#fff'
          },
          borderColor: '#90979c'
        }, {
          show: true,
          // height: '5%',
          xAxisIndex: [
            0
          ],
          // bottom: '5%',
          start: 0,
          end: 100,
          handleIcon: 'path://M306.1,413c0,2.2-1.8,4-4,4h-59.8c-2.2,0-4-1.8-4-4V200.8c0-2.2,1.8-4,4-4h59.8c2.2,0,4,1.8,4,4V413z',
          handleSize: '110%',
          handleStyle: {
            // color: '#d3dee5'
          },
          textStyle: {
            // color: '#fff'
          },
          borderColor: '#90979c'
        }],
        series: [{
          name: 'P-T',
          type: 'line',
          color: ['green'],
          // stack: 'total',
          symbolSize: 10,
          symbol: 'none',
          data: this.lastSymbolData
        }
        // {
        //   name: '水-汽饱和曲线',
        //   type: 'line',
        //   color: ['#FF000033'],
        //   // stack: 'total',
        //   symbolSize: 10,
        //   symbol: 'none',
        //   data: this.line1
        // },
        // {
        //   name: 'AC恢复限制线',
        //   type: 'line',
        //   color: ['#ffa50033'],
        //   // stack: 'total',
        //   symbolSize: 10,
        //   symbol: 'none',
        //   data: this.line2
        // },
        // {
        //   name: '运行下限限制线',
        //   type: 'line',
        //   color: ['#FFFF0033'],
        //   // stack: 'total',
        //   symbolSize: 10,
        //   symbol: 'none',
        //   data: this.line3
        // },
        // {
        //   name: '运行上限限制线',
        //   type: 'line',
        //   color: ['#0000FF33'],
        //   // stack: 'total',
        //   symbolSize: 10,
        //   symbol: 'none',
        //   data: this.line4
        // },
        // {
        //   name: 'ΔTsat=180℃',
        //   type: 'line',
        //   color: ['#80008033'],
        //   // stack: 'total',
        //   symbolSize: 10,
        //   symbol: 'none',
        //   data: this.line5
        // }
        ]
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.pressure-temperature-chart {
  &-container {
    background-color: #eff7fb;
    position:absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);//将元素沿x轴反方向移动本元素的一半width,沿y轴反方向移动本元素的一半height
    // padding: 32px;
    // margin: -15px;
  }
}
</style>
