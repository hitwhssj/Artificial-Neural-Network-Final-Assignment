<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      path: 'ws://localhost:5000/'
    }
  },
  mounted() {
    this.initWebSocket()
  },
  destroyed() {
    this.closeWebSocket()
  },
  methods: {
    initWebSocket() {
      this.$store.commit('wsdata/initWebsocket', this.path)
    },
    closeWebSocket() {
      this.$store.commit('wsdata/closeWebSocket', this.path)
    }
  }
}
</script>
