<template>
  <div
    class="action-operation-table-container action-operation-table-bg-color"
    :class="shadowClass"
  >
    <p class="action-operation-table-next-action-text">下一个动作：{{ expertActionData.value }}</p>
    <el-table
      v-loading="tableDataLoading"
      :data="actionOperationData"
      border
      stripe
      fit
      highlight-current-row
      max-height="380px"
      class="action-operation-table-table"
    >

      <el-table-column align="center" label="动作" min-width="100%">
        <template slot-scope="{row}">
          <el-button
            type="primary"
            @click="handleActionOperationButtonClick(row)"
          >
            {{ row.value }}
          </el-button>
        </template>
      </el-table-column>

    </el-table>
  </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
  name: 'ActionOperationTable',
  props: {
    hasShadow: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      actionOperationData: [
        { index: 1, value: '1.控制棒1号高度减小3档' },
        { index: 2, value: '2.控制棒1号高度减小2档' },
        { index: 3, value: '3.控制棒1号高度减小1档' },
        { index: 4, value: '4.控制棒1号高度增加1档' },
        { index: 5, value: '5.控制棒1号高度增加2档' },
        { index: 6, value: '6.控制棒1号高度增加3档' },

        { index: 7, value: '7.控制棒2号高度减小3档' },
        { index: 8, value: '8.控制棒2号高度减小2档' },
        { index: 9, value: '9.控制棒2号高度减小1档' },
        { index: 10, value: '10.控制棒2号高度增加1档' },
        { index: 11, value: '11.控制棒2号高度增加2档' },
        { index: 12, value: '12.控制棒2号高度增加3档' }
      ],
      tableDataLoading: false
    }
  },
  computed: {
    ...mapState('wsdata', ['expertActionData']),
    shadowClass() {
      if (this.hasShadow === true) {
        return 'shadow'
      } else {
        return ''
      }
    }
  },
  updated() {
    // this.$refs['actionOperationTableScrollbar'].wrap.scrollTop = this.$refs['actionOperationTableScrollbar'].wrap.scrollHeight
  },
  methods: {
    handleActionOperationButtonClick(row) {
      // console.log(row)
      this.$store.commit('wsdata/updateExpertActionData', { 'index': row.index, 'value': row.value })
    }
  }
}
</script>

<style lang="scss">
.action-operation-table {
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
  &-table {
    // padding-left: 25px;
    margin-top: 0px;
  }
  &-next-action-text {
    font: bold 15px 'Microsoft YaHei';
  }
}

</style>
