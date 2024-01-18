<template>
  <div
    class="action-history-table-container action-history-table-bg-color"
    :class="shadowClass"
  >
    <el-row :gutter="0">
      <el-col :span="24">

        <el-select
          v-model="sortMode"
          placeholder="请选择"
          style="width: 60%;"
        >
          <el-option
            v-for="item in options"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <el-button
          style="margin-left: 5%;"
          type="primary"
          @click="handleClearActionButtonClick"
        >
          清空
        </el-button>
      </el-col>

    </el-row>

    <div class="action-history-table-timeline">
      <el-scrollbar ref="actionHistoryTableScrollbar" style="height: 100%" wrap-style="overflow-x:hidden;">
        <el-timeline>
          <el-timeline-item
            v-for="(item, index) in tableData"
            :key="index"
            :icon="item.icon"
            :color="item.color"
            :size="item.size"
            :timestamp="item.time"
            placement="top"
          >
            <el-card
              class="action-history-table-card"
            >
              <h4>序号：{{ item.step }}</h4>
              <h4 v-if="operatingMode==='expert'">建议动作：{{ item.suggested_action_num }}</h4>
              <h4 v-if="operatingMode==='expert'">建议动作意义：{{ item.suggested_action }}</h4>
              <h4>当前动作：{{ item.action_num }}</h4>
              <h4>动作意义：{{ item.action }}</h4>
              <h4>动作得分：{{ item.reward }}</h4>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-scrollbar>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
  name: 'ActionHistoryTable',
  props: {
    hasShadow: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      sortMode: 'timeDescend',
      options: [
        { value: 'timeDescend', label: '时间降序' },
        { value: 'rewardAscend', label: '得分升序' },
        { value: 'rewardDescend', label: '得分降序' }
      ]
    }
  },
  computed: {
    ...mapState('wsdata', ['actionHistoryTableData', 'operatingMode']),
    tableData() {
      if (this.actionHistoryTableData === undefined) {
        return undefined
      }
      var tableDataBox = []
      for (let i = 0; i < this.actionHistoryTableData.length; i++) {
        tableDataBox.push(this.actionHistoryTableData[i])
      }
      const compareAscending = p => (m, n) => m[p] - n[p]
      const comparedescending = p => (m, n) => n[p] - m[p]
      if (this.sortMode === 'timeAscend') {
        // 升序，默认
        // 无需处理
      } else if (this.sortMode === 'timeDescend') {
        // 降序
        tableDataBox.reverse()
      } else if (this.sortMode === 'rewardDescend') {
        // reward降序
        tableDataBox.sort(comparedescending('reward'))
      } else if (this.sortMode === 'rewardAscend') {
        // reward升序
        tableDataBox.sort(compareAscending('reward'))
      }
      return tableDataBox
    },
    scrollLength() {
      if (this.actionHistoryTableData === undefined) {
        return 0
      } else {
        return this.actionHistoryTableData.length
      }
    },
    shadowClass() {
      if (this.hasShadow === true) {
        return 'shadow'
      } else {
        return ''
      }
    }
  },
  updated() {
    // this.$refs['actionHistoryTableScrollbar'].wrap.scrollTop = this.$refs['actionHistoryTableScrollbar'].wrap.scrollHeight
  },
  methods: {
    handleClearActionButtonClick() {
      this.$store.commit('wsdata/clearActionHistoryTableData')
    }
  }
}
</script>

<style lang="scss">
.action-history-table {
    &-container {
    height: 480px;
    width: 100%;
    // border: solid 3px rgb(93, 90, 90);
    padding: 20px;
    font: bold 20px 'Courier New';
    border-radius: 4px;
    // margin: -15px;
  }
  &-bg-color {
    background: #eff7fb;
  }
  &-timeline {
    height: 350px;
    width: 100%;
    padding-top: 20px;
    margin-left: -30px;
  }
  &-card {
    font: bold 10px 'Microsoft YaHei';
  }
}

</style>
