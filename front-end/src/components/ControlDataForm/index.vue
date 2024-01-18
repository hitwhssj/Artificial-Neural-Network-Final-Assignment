<template>
  <div class="control-data-form-container shadow control-data-form-bg-color">
    <el-form ref="controlDataForm" class="control-data-form-el-form" :inline="true" :model="formData" :rules="formRules" label-width="80px" :disabled="controlDataFormConstraint">
      <!-- 运行模式单选 -->
      <el-form-item label="运行模式">
        <el-radio-group v-model="formData.runMode" @change="handleRunModeChange">
          <el-radio label="train">训练</el-radio>
          <el-radio label="test">测试</el-radio>
        </el-radio-group>
      </el-form-item>
      <!-- 初始功率单选 -->
      <el-form-item label="初始功率">
        <el-radio-group v-model="formData.initPower" @change="handleInitPowerChange">
          <el-radio label="1.0">满功率</el-radio>
          <el-radio label="0.5">半功率</el-radio>
        </el-radio-group>
      </el-form-item>
      <br>
      <!-- 选择算法 -->
      <el-form-item key="loadModelFileNameSelect" label="算法选择" prop="algorithm">
        <el-select
          v-model="formData.algorithm"
          filterable
          clearable
          placeholder="请选择算法"
          style="width: 150px;"
          @change="handleAlgorithmChange"
        >
          <el-option
            v-for="item in algorithmList"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </el-form-item>

      <!-- 选择加载的模型 -->
      <el-form-item v-if="loadModelFileNameSelectConstraint" key="loadModelFileNameSelect" label="模型选择" prop="loadModelFileName">
        <el-select
          v-model="formData.loadModelFileName"
          filterable
          remote
          clearable
          placeholder="请输入关键词"
          :loading="loadModelFileNameLoading"
          style="width: 300px;"
          @focus="handleLoadModelFileNameRemoteData"
          @change="handleLoadModelFileNameChange"
        >
          <el-option
            v-for="item in loadModelFileNameList"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </el-form-item>

      <!-- 自动保存 -->
      <el-form-item v-if="automaticSaveSliderConstraint" label="自动保存">
        <el-switch v-model="formData.automaticSave" @change="handleAutomaticSaveSliderChange" />
      </el-form-item>

      <!-- 选择Episode-->
      <!-- <el-form-item label="运行次数">
        <el-input-number v-model="formData.episodeNum" :min="1" :max="1000" label="Episode" @change="handleEpisodeNumberChange" />
      </el-form-item> -->

      <!-- 控制按钮 -->
      <el-form-item class="control-data-form-control-buttons" label="控制">
        <el-button
          :type="mainButtonType"
          :disabled="mainButtonConstraint"
          @click="clickMainButton"
        >{{ mainButtonText }}</el-button>

        <el-button
          :type="stopButtonType"
          :disabled="stopButtonConstraint"
          @click="clickStopButton"
        >{{ stopButtonText }}</el-button>
      </el-form-item>

      <!-- 事故按钮 -->
      <br>
      <el-form-item class="control-data-form-accident-buttons" label="任务:">
        <el-button
          v-for="item in accidentButtons"
          :key="item.id"
          :type="item.type"
          :disabled="accidentButtonConstraint"
          @click="handleclickAccidentButton(item.id)"
        >{{ item.text }}</el-button>

      </el-form-item>
      <el-form-item class="control-data-form-state-board">
        <el-tag>
          {{ stateBoard.info }}
        </el-tag>
      </el-form-item>
    </el-form>

  </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
  name: 'ControlDataFrom',
  data() {
    return {
      formData: {
        runMode: 'train',
        initPower: '1.0',
        automaticSave: false,
        loadModelFileName: '',
        algorithm: ''
      },
      formRules: {
        loadModelFileName: [
          { required: true, message: '请选择要加载的模型', trigger: 'change' }
        ],
        algorithm: [
          { required: true, message: '请选择算法', trigger: 'change' }
        ]
      },
      isPause: false,
      mainButtonType: 'primary',
      mainButtonText: '开始',
      mainButtonConstraint: false,
      stopButtonType: 'danger',
      stopButtonText: '结束',
      stopButtonConstraint: true,
      controlDataFormConstraint: false,
      accidentButtonConstraint: false,

      // loadModelFileName
      loadModelFileNameList: undefined,
      loadModelFileNameLoading: false,

      // check valid
      checkFormValidFlag: false,

      // accident button
      accidentButtons: [
        { id: 0, text: '100%功率', type: 'primary' },
        { id: 1, text: '75%功率', type: 'primary' },
        { id: 2, text: '50%功率', type: 'primary' }
        // { id: 3, text: '冷却液泄露', type: 'danger' },
        // { id: 4, text: '控制棒失控抽出', type: 'danger' }
      ],
      algorithmList: [
        'DQN',
        'Double DQN',
        'Dueling DQN'
      ]
    }
  },
  computed: {
    ...mapState('wsdata', ['syncSignal', 'stateBoard']),
    modelSaveButtonConstraint() {
      return this.formData.runMode === 'train'
    },
    modelLoadButtonConstraint() {
      return !(this.formData.runMode === 'train')
    },
    automaticSaveSliderConstraint() {
      return this.formData.runMode === 'train'
    },
    loadModelFileNameSelectConstraint() {
      return this.formData.runMode === 'test'
    }
  },
  watch: {
    syncSignal: {
      deep: true,
      handler() {
        if (this.syncSignal === 'start_over') {
          // 开始任务已完成
          this.mainButtonConstraint = false
          this.stopButtonConstraint = false
        } else if (this.syncSignal === 'pause_over') {
          // 暂停任务已完成
          this.mainButtonConstraint = false
          this.stopButtonConstraint = false
        } else if (this.syncSignal === 'continue_over') {
          // 继续任务已完成
          this.mainButtonConstraint = false
          this.stopButtonConstraint = false
        } else if (this.syncSignal === 'stop_over') {
          // 终止任务已完成
          this.mainButtonConstraint = false
          this.accidentButtonConstraint = false
          this.controlDataFormConstraint = false
          this.$message('手动终止！')
          this.$store.commit('wsdata/clearAccident')
        } else if (this.syncSignal === 'end_over') {
          // 正常结束，模拟触发clickStopButton
          this.mainButtonType = 'primary'
          this.mainButtonText = '开始'
          this.stopButtonConstraint = true
          this.isPause = false
          // 模仿结束任务已完成函数
          this.mainButtonConstraint = false
          this.accidentButtonConstraint = false
          this.controlDataFormConstraint = false
          this.$message('运行完成！')
          this.$store.commit('wsdata/clearAccident')
        }
      }
    }
  },
  mounted() {
  },
  methods: {
    clickMainButton(event) {
      // 验证
      if (this.isPause === false && this.checkFormValid() === false) {
        // console.log('then')
        return
      }
      // 双重验证
      if (this.formData.algorithm === '' || this.formData.algorithm === undefined || this.formData.runMode === 'test' && (this.formData.loadModelFileName === undefined || this.formData.loadModelFileName === '')) {
        this.$message('验证失败，请填写完整信息')
        return
      }
      this.mainButtonConstraint = true
      this.stopButtonConstraint = true
      this.controlDataFormConstraint = true
      if (this.isPause === false) {
        this.mainButtonType = 'warning'
        this.mainButtonText = '暂停'
        this.$store.commit('wsdata/sendControlSignal', 'start')
        this.isPause = true
      } else {
        this.mainButtonType = 'warning'
        this.mainButtonText = '继续'
        this.$store.commit('wsdata/sendControlSignal', 'pause')
        this.isPause = false
      }
    },
    clickStopButton(event) {
      this.mainButtonConstraint = true
      this.stopButtonConstraint = true
      this.mainButtonType = 'primary'
      this.mainButtonText = '开始'
      this.$store.commit('wsdata/sendControlSignal', 'stop')
      this.isPause = false
    },
    checkFormValid() {
      this.$refs['controlDataForm'].validate((valid) => {
        if (valid) {
          // alert('通过验证')
          this.$message('通过验证')
          this.checkFormValidFlag = true
          return true
        } else {
          // alert('未通过验证')
          this.$message('请填写完整信息')
          return false
        }
      })
      return this.checkFormValidFlag
    },
    // saveModel() {
    //   this.$store.commit('wsdata/sendControlSignal', 'save')
    // },
    // loadModel() {
    //   this.$store.commit('wsdata/sendControlSignal', 'load')
    // },
    handleRunModeChange(newRunMode) {
      this.$store.commit('wsdata/updateRunMode', newRunMode)
      // 进入test后清空自动保存，进入train选中自动保存
      if (newRunMode === 'test') {
        this.formData.automaticSave = false
        this.$store.commit('wsdata/updateAutomaticSave', false)
      } else if (newRunMode === 'train') {
        this.formData.automaticSave = false
        this.$store.commit('wsdata/updateAutomaticSave', false)
      }
      // console.log(newRunMode)
    },
    handleInitPowerChange(newInitPower) {
      this.$store.commit('wsdata/updateInitPower', parseFloat(newInitPower))
    },
    handleAutomaticSaveSliderChange(newAutomaticSave) {
      // console.log(newAutomaticSave)
      this.$store.commit('wsdata/updateAutomaticSave', newAutomaticSave)
    },
    handleLoadModelFileNameRemoteData() {
      this.loadModelFileNameLoading = true
      this.$axios.get('/get-model-file-name')
        .then(response => {
          // console.log(response.data)
          this.loadModelFileNameList = response.data
          this.loadModelFileNameLoading = false
        })
        .catch(function(error) {
          console.log('出错')
          console.log(error)
        })
    },
    handleLoadModelFileNameChange(newLoadModelFileName) {
      if (this.formData.algorithm === 'Dueling DQN' && newLoadModelFileName.indexOf(this.formData.algorithm) !== 0 || this.formData.algorithm !== 'Dueling DQN' && newLoadModelFileName.indexOf('Dueling DQN') === 0) {
        // this.$message('请检查模型是否匹配')
        this.$message.error('请检查模型是否匹配')
        // this.$message({
        // message: '请检查模型是否匹配',
        // type: 'warning'
        // })
      }
      this.$store.commit('wsdata/updateLoadModelFileName', newLoadModelFileName)
    },
    handleclickAccidentButton(id) {
      // console.log(id)
      this.accidentButtonConstraint = true
      this.$store.commit('wsdata/updateAccident', id)
    },
    handleAlgorithmChange(newAlgorithm) {
      this.$store.commit('wsdata/updateAlgorithm', newAlgorithm)
    }
  }
}
</script>

<style lang="scss">
.control-data-form {
  &-container {
    background-color: white;
    /* width: 500px; */
    margin-top: 10px;
    padding: 10px;
    // padding-bottom: -10px;
    /* margin-bottom: 10px; */
  }
  &-radio {
    font: bold 20px 'Courier New';
    margin: 10px;
  }
  &-control-buttons {
    /* height: 320px; */
    // margin: 10px;
    margin-left: 50px;
    font: bold 20px 'Courier New';
  }
  &-accident-buttons {
    float: left;
    font: bold 20px 'Courier New';
  }
  &-bg-color {
    background: #eff7fb;
  }
  &-el-form {
    height: 180px;
  }
  &-state-board {
    // font: bold 20px 'Microsoft YaHei';
    // background-color: #f0f2f5;
    float: right;
  }
}
</style>
