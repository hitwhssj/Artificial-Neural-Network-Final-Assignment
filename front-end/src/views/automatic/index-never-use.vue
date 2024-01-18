<template>
  <div>
    <div class="automatic-text">{{ name }}</div>
    <ControlButton />
    <router-view />
    <Layout />
  </div>
</template>

<script>
import ControlButton from '@/components/ControlButton/index.vue'
import Layout from '@/layout/index.vue'
export default {
  // name: 'index',
  components: {
    ControlButton,
    Layout
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
.automatic {
  &-container {
    margin: 30px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
}
</style>
