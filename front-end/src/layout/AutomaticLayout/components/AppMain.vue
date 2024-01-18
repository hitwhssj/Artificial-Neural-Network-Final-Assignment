<template>
  <div>
    <div class="automatic-layout-appmain-container">
      <!-- <div class="automatic-layout-appmain-text">{{ name }}</div> -->
      <el-row :gutter="20">
        <el-col :span="24"><div class="automatic-layout-appmain-grid-content"><ControlDataFrom /></div></el-col>
      </el-row>
    </div>

    <section class="app-main">
      <transition name="fade-transform" mode="out-in">
        <!-- <keep-alive> -->
        <router-view :key="key" />
        <!-- </keep-alive> -->
      </transition>
    </section>
  </div>

</template>

<script>
import ControlDataFrom from '@/components/ControlDataForm/index.vue'
export default {
  name: 'AppMain',
  components: {
    ControlDataFrom
  },
  computed: {
    key() {
      return this.$route.path
    },
    name() {
    //   console.log(this.$route)
      const matched = this.$route.matched
      return matched[0].meta.title + ' : ' + matched[1].meta.title
    }
  }
}
</script>

<style scoped>
.app-main {
  /*50 = navbar  */
  min-height: calc(100vh - 200px);
  width: 100%;
  position: relative;
  overflow: hidden;
}
.fixed-header+.app-main {
  padding-top: 50px;
}
</style>

<style lang="scss">
// fix css style bug in open el-dialog
.el-popup-parent--hidden {
  .fixed-header {
    padding-right: 15px;
  }
}
</style>

<style lang="scss" scoped>
.automatic-layout-appmain {
  &-container {
    padding: 32px;
    padding-top: 0px;
    background-color: rgb(240, 242, 245);
    position: relative;
    padding-bottom: 10px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
  &-grid-content {
    border-radius: 4px;
    min-height: 36px;
    background-color: white;
  }
}
</style>

