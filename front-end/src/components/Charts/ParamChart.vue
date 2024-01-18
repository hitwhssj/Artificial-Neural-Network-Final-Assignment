<template>
  <div>
    <div :id="id" :class="className" :style="{height:height,width:width}" class="param-chart-container" />
    <el-select
      v-model="selectParam"
      multiple
      collapse-tags
      placeholder="请选择"
      class="param-chart-select"
      @change="handleSelectChange"
    >
      <el-option
        v-for="item in paramChartOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value"
      />
    </el-select>
  </div>
</template>

<script>
import resize from './mixins/resize'
import { mapState } from 'vuex'

export default {
  name: 'ParamChart',
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: 'param-chart-container'
    },
    id: {
      type: String,
      default: 'paramChart'
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
      paramChart: null,
      selectParam: ['T2', 'T3'],
      chartOption: {
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
          },
          formatter: params => {
            // console.log(params)
            var str = ''
            params.forEach((item, index) => {
              if (str === '') {
                str += `time: ${item.axisValue}<br/>`
              }
              str += `${item.marker}${item.seriesName}: ${item.data}`
              var unit = ''
              Object.keys(this.paramChartData).forEach(key => {
                if (this.paramChartData[key].name === item.seriesName) {
                  unit = this.paramChartData[key].unit
                }
              })
              str += unit
              str += index === params.length - 1 ? '' : '<br/>'
            })
            return str
          }
        },
        grid: {
          left: '9%',
          right: '5%',
          borderWidth: 0,
          top: '20%',
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
          x: '32%',
          top: '2%',
          textStyle: {
            // color: '#90979c'
          },
          data: []
        },
        calculable: true,
        xAxis: [{
          name: 'time',
          // min: 0,
          // max: 400,
          type: 'category',
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
          },
          splitArea: {
            show: true
          },
          axisLabel: {
            interval: 0
          },
          data: this.simulationTime
        }],
        yAxis: [{
          name: 'value',
          // min: 0,
          // max: 400,
          type: 'value',
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
          // top: '18%',
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
        series: [
        ]
      }
    }
  },
  computed: {
    ...mapState('wsdata', ['paramChartData', 'simulationTime']),
    paramChartOptions() {
      var options = []
      Object.keys(this.paramChartData).forEach(key => {
        options.push({
          value: this.paramChartData[key].code_name,
          label: this.paramChartData[key].name
        })
      })
      return options
    }
  },
  watch: {
    paramChartData: {
      deep: true,
      handler() {
        this.updateParamChart()
      }
      // immediate: true
    },
    simulationTime: {
      deep: true,
      handler() {
        this.updateParamChart()
      }
      // immediate: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initParamChart()
      this.updateParamChart()
    })
  },
  beforeDestroy() {
    if (!this.paramChart) {
      return
    }
    this.paramChart.dispose()
    this.paramChart = null
  },
  methods: {
    initParamChart() {
      this.paramChart = this.$echarts.init(document.getElementById(this.id))
      this.paramChart.showLoading()
    },
    updateParamChart() {
      if (this.paramChartData === undefined || this.paramChart === null) {
        return
      }
      this.paramChart.hideLoading()
      this.paramChart.clear()
      this.chartOption.xAxis[0].data = this.simulationTime
      this.paramChart.setOption(this.chartOption)
      this.handleSelectChange()
      // console.log(this.paramChartData)
    },
    handleSelectChange() {
      this.chartOption.series = []
      this.chartOption.legend.data = []

      // console.log(this.chartOption.xAxis[0])
      this.paramChart.clear()
      this.chartOption.xAxis[0].data = this.simulationTime
      Object.keys(this.paramChartData).forEach(key => {
        if (this.selectParam.indexOf(key) >= 0) {
          // x Axis
          // if (this.chartOption.xAxis[0].data.length === 0) {
          //   for (var i = 0; i < this.paramChartData[key].data.length; i++) {
          //     this.chartOption.xAxis[0].data.push(i + 1)
          //   }
          // }

          this.chartOption.legend.data.push(this.paramChartData[key].name)
          this.chartOption.series.push({
            name: this.paramChartData[key].name,
            type: 'line',
            symbolSize: 3,
            symbol: 'circle',
            data: this.paramChartData[key].data,
            label: {
              show: false,
              // position: 'top',
              formatter: p => {
                // console.log(this.paramChartData[key].name)
                return p.data + this.paramChartData[key].unit
              }

            }
          })
        }
      })
      this.paramChart.setOption(this.chartOption, true)
    }
  }
}
</script>

<style lang="scss" scoped>
.param-chart {
  &-container {
    background-color: #eff7fb;
    position:absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);//将元素沿x轴反方向移动本元素的一半width,沿y轴反方向移动本元素的一半height
    // padding: 32px;
    // margin: -15px;
  }
  &-select {
    float: left;
    width: 30%;
  }
}
</style>
