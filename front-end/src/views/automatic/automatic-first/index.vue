<template>
  <div class="automatic-interact-container">

    <el-row :gutter="50">
      <el-col :span="12"><div class="automatic-interact-status-param-table"><StatusParamTable /></div></el-col>
      <el-col :span="12"><div class="automatic-interact-action-history-table"><ActionHistoryTable :has-shadow="true" /></div></el-col>
    </el-row>
  </div>
</template>

<script>
import StatusParamTable from '@/components/Tables/StatusParamTable.vue'
import ActionHistoryTable from '@/components/Tables/ActionHistoryTable.vue'
export default {
  // name: 'AutomaticInteract',
  components: {
    StatusParamTable,
    ActionHistoryTable
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
.automatic-interact {
  &-container {
    padding: 32px;
    padding-top: 0px;
    background-color: rgb(240, 242, 245);
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
  &-status-param-table {
    border-radius: 4px;
    min-height: 36px;
    background-color: white;
    position: relative;
    width: 100%;
    height: 100%;
    float: left;
  }
  &-action-history-table {
    border-radius: 4px;
    min-height: 36px;
    background-color: white;
    position: relative;
    width: 100%;
    height: 100%;
    float: right;
  }
}
</style>

