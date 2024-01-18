<template>
  <div class="automatic-agent-container">
    <keep-alive>
      <el-tabs type="border-card" class="automatic-agent-el-tabs">
        <el-tab-pane class="automatic-agent-chart" :lazy="true">
          <span slot="label">
            <svg-icon icon-class="action-history" />
            P-T图
          </span>
          <PressureTemperatureChart :height="chartHeight" :width="chartWidth" />
        </el-tab-pane>

        <!-- <el-tab-pane class="automatic-agent-chart" :lazy="true">
          <span slot="label">
            <svg-icon icon-class="action-history" />
            Param-Time图
          </span>
          <ParamChart :height="chartHeight" :width="chartWidth" />
        </el-tab-pane> -->

        <el-tab-pane v-for="item in paramChartList" :key="item.id" class="automatic-agent-chart" :lazy="true">
          <span slot="label">
            <svg-icon icon-class="action-history" />
            {{ item.name }}
          </span>
          <ParamChart :id="item.id" :height="chartHeight" :width="chartWidth" />
        </el-tab-pane>

      </el-tabs>
    </keep-alive>
  </div>
</template>

<script>
import PressureTemperatureChart from '@/components/Charts/PressureTemperatureChart.vue'
import ParamChart from '@/components/Charts/ParamChart.vue'
export default {
  components: {
    PressureTemperatureChart,
    ParamChart
  },
  data() {
    return {
      // 与css相同
      chartHeight: '100%',
      chartWidth: '100%',
      paramChartList: [
        { name: 'Param-Time图', id: 'paramChart' }
      ]
    }
  },
  computed: {
    name() {
    //   console.log(this.$route)
      const matched = this.$route.matched
      return matched[0].meta.title + ' : ' + matched[1].meta.title
    }
  }
}
</script>

<style lang="scss" scoped>
.automatic-agent {
  &-container {
    background-color: rgb(240, 242, 245);
    padding: 32px;
    padding-top: 0px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
  &-el-tabs {
    // position: relative;
    width: 100%;
    height: 100%;
  }
  &-chart {
    height: 430px;
    width: 100%;
  }
}
</style>

