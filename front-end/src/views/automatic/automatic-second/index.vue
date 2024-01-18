<template>
  <div class="automatic-env-container">

    <el-row :gutter="20">
      <el-col :span="8"><div class="automatic-env-key-param-table"><KeyParamTable /></div></el-col>
      <el-col :span="8"><div class="automatic-env-key-param-table"><CoreParamTable /></div></el-col>
      <el-col :span="8"><div class="automatic-env-key-device-table"><KeyDeviceTable /></div></el-col>
    </el-row>
  </div>
</template>

<script>
import KeyParamTable from '@/components/Tables/KeyParamTable.vue'
import KeyDeviceTable from '@/components/Tables/KeyDeviceTable.vue'
import CoreParamTable from '@/components/Tables/CoreParamTable.vue'
export default {
  // name: 'AutomaticEnv',
  components: {
    KeyParamTable,
    KeyDeviceTable,
    CoreParamTable
  },
  data() {
    return {
      // 与css相同
      mixChartHeight: '630px',
      mixChartWidth: '1240px'
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
.automatic-env {
  &-container {
    background-color: rgb(240, 242, 245);
    padding: 32px;
    padding-top: 0px;
  }
  &-key-param-table {
    border-radius: 4px;
    background-color: white;
    position: relative;
    width: 100%;
    height: 100%;
    // float: left;
  }
  &-key-device-table {
    border-radius: 4px;
    background-color: white;
    position: relative;
    width: 100%;
    height: 100%;
    // float: right;
  }
}
</style>

