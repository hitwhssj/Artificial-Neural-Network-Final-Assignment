import { io } from 'socket.io-client'
export default {
  namespaced: true,
  state: {
    // 自动模式表单数据
    runMode: 'train',
    initPower: 1.0,
    algorithm: 'DQN',
    automaticSave: false,
    loadModelFileName: '',
    statusParamTableData: undefined,
    keyParamTableData: undefined,
    coreParamTableData: undefined,
    actionHistoryTableData: [],
    keyDeviceTableData: undefined,
    pressureTemperatureChartData: [
    ],
    paramChartData: {
    },
    socket: {},
    syncSignal: '',
    expertActionData: { 'index': 0, 'value': '0.不动作' },
    operatingMode: 'automatic',
    simulationTime: [],
    accidentList: [0, 0, 0, 0, 0],
    stateBoard: { info: '无' }
  },
  mutations: {
    initWebsocket(state, path) {
      this.socket = io.connect(path)
      this.socket.on('connect', () => {
        console.log('connect :' + this.socket.connected)
      })
      this.socket.on('disconnect', (reason) => {
        console.log('disconnect :' + this.socket.connected)
        console.log(reason)
      })
      this.socket.on('data_message', (res) => {
        state.envStateTableData = res.env_state_table_data
        state.envStateTableLabel = res.env_state_table_label
        // imageRenderData
        state.imageRenderData = res.image_render_data

        // keyParamTableData
        state.keyParamTableData = res.key_param_table_data
        state.coreParamTableData = res.core_param_table_data

        // actionHistoryTableData
        state.actionHistoryTableData = res.action_history_table_data

        // statusParamTableData
        state.statusParamTableData = res.status_param_table_data

        // key device
        state.keyDeviceTableData = res.key_device_table_data

        // pt chart
        state.pressureTemperatureChartData = res.pressure_temperature_chart_data
        state.paramChartData = res.param_chart_data
        state.simulationTime = res.simulation_time
        // console.log(state.mixChartData)
      })
      this.socket.on('remove_constraints', (res) => {
        state.syncSignal = res.sync_signal
        console.log('收到同步信号' + state.syncSignal)
      })
      this.socket.on('remove_expert_action', (res) => {
        state.expertActionData = res.expert_action_data
        console.log('专家动作清空')
      })
      this.socket.on('episode_end', (res) => {
        state.stateBoard = res.state_board
      })
    },
    sendControlSignal(state, controlSignal) {
      state.syncSignal = 'wait'
      // 发送成后端规范的命名
      this.socket.emit('control_message', { control_signal: controlSignal, run_mode: state.runMode, algorithm: state.algorithm, init_power: state.initPower, automatic_save: state.automaticSave, load_model_file_name: state.loadModelFileName, operating_mode: state.operatingMode })
      // console.log({ control_signal: controlSignal, run_mode: state.runMode })
      // console.log(value.runMode)
    },
    updateRunMode(state, runMode) {
      state.runMode = runMode
      // console.log('wsdata收到train or test = ' + value)
    },
    updateAutomaticSave(state, automaticSave) {
      state.automaticSave = automaticSave
    },
    clearActionHistoryTableData(state) {
      if (state.actionHistoryTableData !== undefined) {
        state.actionHistoryTableData = []
        console.log('action 已经清理')
      }
    },
    updateLoadModelFileName(state, loadModelFileName) {
      state.loadModelFileName = loadModelFileName
    },
    updateExpertActionData(state, obj) {
      state.expertActionData = obj
      this.socket.emit('expert_action', state.expertActionData)
      // console.log(obj)
    },
    updateOperatingMode(state, newOperatingMode) {
      state.operatingMode = newOperatingMode
      // console.log(state.operatingMode)
    },
    closeWebSocket(state) {
      this.socket.disconnect()
    },
    updateAccident(state, num) {
      state.accidentList[num] = 1
      this.socket.emit('start_accident', num)
    },
    clearAccident(state) {
      state.accidentList = [0, 0, 0, 0, 0]
    },
    updateInitPower(state, newInitPower) {
      state.initPower = newInitPower
    },
    updateAlgorithm(state, newAlgorithm) {
      state.algorithm = newAlgorithm
    }
  },
  actions: {},
  getters: {}
}
