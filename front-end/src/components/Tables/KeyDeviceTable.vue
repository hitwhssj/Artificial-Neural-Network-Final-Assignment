<template>
  <div class="key-device-table-container shadow key-device-table-bg-color">
    <el-row>
      <el-col :span="10" :offset="7"><div class="component-title">重要设备</div></el-col>
    </el-row>
    <el-table
      :data="keyDeviceTableData"
      border
      stripe
      fit
      highlight-current-row
      max-height="480px"
      class="key-device-table-table"
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
  name: 'KeyDeviceTable',
  data() {
    return {
    }
  },
  computed: {
    ...mapState('wsdata', ['keyDeviceTableData']),
    tableDataLoading() {
      return this.keyDeviceTableData === undefined
    }
  },
  methods: {
  }
}
</script>

<style lang="scss">
.key-device-table {
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
