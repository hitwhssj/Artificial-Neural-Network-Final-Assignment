import Vue from 'vue'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:5000'
Vue.prototype.$axios = axios
