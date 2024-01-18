<template>
  <div class="core-param-table-container shadow core-param-table-bg-color">
    <el-row>
      <el-col :span="10" :offset="7"><div class="component-title">堆芯参数</div></el-col>
    </el-row>
    <el-table
      :data="coreParamTableData"
      border
      stripe
      fit
      highlight-current-row
      max-height="480px"
      class="core-param-table-table"
    >
      <!-- <el-table-column align="center" label="变量名" width="180">
        <template slot-scope="{row}">
          <span>{{ row.codeName }}</span>
        </template>
      </el-table-column> -->

      <el-table-column align="center" label="含义" min-width="50%">
        <template slot-scope="{row}">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="变量值" min-width="50%">
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
  name: 'CoreParamTable',
  data() {
    return {
    }
  },
  computed: {
    ...mapState('wsdata', ['coreParamTableData']),
    tableDataLoading() {
      return this.coreParamTableData === undefined
    }
  },
  methods: {
  }
}
</script>

<style lang="scss">
.core-param-table {
  &-container {
    height: 100%;
    width: 100%;
    /* border: solid 3px rgb(182, 184, 182); */
    padding: 10px;
    font: bold 15px 'Microsoft YaHei';
    border-radius: 4px;
  }
  &-table {
    // padding-left: 25px;
    margin-top: 30px;
  }
  &-bg-color {
    background: #f2fbf8;
  }
  &-courier-new-font {
    font: bold 20px 'Courier New';
  }
}

</style>
