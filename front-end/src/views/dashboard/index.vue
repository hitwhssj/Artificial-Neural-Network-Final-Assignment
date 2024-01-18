<template>
  <div class="dashboard-container">
    <p class="dashboard-text">
      人工神经网络期末作业：基于核电仿真环境的监控与决策系统（2 工程应用类型）
      <br>
      孙圣杰 2023214331
    </p>
    <!-- <div class="dashboard-image-select">
      <el-image
        :src="imgSrcLast"
        alt=""
        fit="fill"
        :preview-src-list="srcList"
      />
    </div> -->
    <el-image
      class="dashboard-image-background"
      :src="imgBackground"
      alt="运行实况"
      fit="fill"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Dashboard',
  components: {
  },
  data() {
    return {
      imgBackground: require('@/assets/school.jpg')
    }
  },
  computed: {
    ...mapGetters([
      'name'
    ])
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    // margin: 30px;
    width: 100%;
    height: 110%;
    position: absolute;
  }
  &-text {
    line-height: 46px;
    text-align: center;
    margin: 0px;
    font: bold 35px 'Microsoft YaHei';
    // background-color: #a3c5e5;
  }
  &-image-select {
    margin-left: 2%;
    width: 8%;
    height: 8%;
    margin-top: -5%;
    opacity: 1;
  }
  &-image-background {
    width: 100%;
    height: 100%;
    // opacity: 0.8;
    // margin-top: -10%;
    // z-index: -1;
  }
}
</style>
