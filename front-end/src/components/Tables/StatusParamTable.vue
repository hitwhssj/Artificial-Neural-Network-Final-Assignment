<template>
  <div class="status-param-table-container shadow status-param-table-bg-color">
    <el-row>
      <el-col :span="16" :offset="4"><div class="component-title">任务触发</div></el-col>
    </el-row>
    <el-table
      :data="statusParamTableData"
      border
      fit
      highlight-current-row
      :cell-class-name="tableCellClassName"
      class="status-param-table-table"
    >

      <el-table-column align="center" label="含义" min-width="100%">
        <template slot-scope="{row}">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="变量值" min-width="100%">
        <template slot-scope="{row}">
          <span>{{ row.value }}</span>
        </template>
      </el-table-column>

    </el-table>
  </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
  name: 'StatusParamTable',
  data() {
    return {
    }
  },
  computed: {
    ...mapState('wsdata', ['statusParamTableData']),
    tableDataLoading() {
      return this.statusParamTableData === undefined
    }
  },
  methods: {
    tableCellClassName({ row, column, rowIndex, columnIndex }) {
      if (columnIndex === 0) {
        return ''
      }
      if (row.value === '触发') {
        return 'status-param-table-accident-row'
      } else if (row.value === '未触发') {
        return 'status-param-table-not-accident-row'
      }
      return ''
    }
  }
}
</script>

<style lang="scss">
.status-param-table {
  &-container {
    height: 480px;
    width: 100%;
    /* border: solid 3px rgb(182, 184, 182); */
    padding: 10px;
    font: bold 15px 'Microsoft YaHei';
    border-radius: 4px;
  }
  &-table {
    // padding-left: 25px;
    margin-top: 30px;

    // position:absolute;
    // left: 50%;
    // transform: translate(-50%, 0%);//将元素沿x轴反方向移动本元素的一半width,沿y轴反方向移动本元素的一半height
    // width: 90%
  }
  &-bg-color {
    background: #f2fbf8;
  }
  &-courier-new-font {
    font: bold 20px 'Courier New';
  }
  &-not-accident-row {
    background: rgb(162, 243, 162);
  }
  &-accident-row {
    background: rgb(250, 156, 156);
  }
}

</style>
