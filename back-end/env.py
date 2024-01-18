# -*- coding: utf-8 -*-
import random
from tqdm import tqdm
import numpy as np
from matplotlib import pyplot as plt

import env_core as Nu


class NuclearEnv(object):
    # 300 corresponds with nr_init = 1.0 with indicates full power
    scale = 100
    dt = 1.  # time step
    drho = 0.0005

    episode_step_max = 1500
    rod_pos_max = 512
    rod_pos_min = 0

    def __init__(self, integrator, rod_num=2):
        # 1. 设备(动作仅修改设备的百分比)
        # 控制棒, 主泵Q1，泵Q2，温度T4，安注箱Q3
        self.episodic_step = 1
        self.rod_num = rod_num
        self.device_name = []
        self.device_proportion = []
        self.device_range = []
        for i in range(rod_num):
            self.device_name.append('rod' + str(i))
            self.device_proportion.append(50.)
            self.device_range.append((0., 512.))
        self.device_name.extend(['main_pump', 'ARE_pump', 'ARE_water_temperature', 'security_injection'])
        self.device_proportion.extend([100., 100., 80., 0.])
        self.device_range.extend([(0., 25600.), (20., 20000.), (20., 270.), (0., 5000.)])

        # 2. 非堆芯参数,回路参数(T1,T2指定,Q1,Q2,Q3,T4输入值由开度*范围,T3,T5计算得来)
        # 2.1 常量
        self.k = 2000
        # 2.2 变量
        self.power = None

        self.circuit_param_name = []
        for i in range(self.rod_num):
            self.circuit_param_name.append('rod' + str(i) + '_pos')
        self.circuit_param_name.extend(['Q1', 'Q2', 'T4', 'Q3', 'T1', 'T2', 'T3', 'T5', 'real_Q1'])
        self.circuit_param_list = []
        for i in range(self.rod_num):
            self.circuit_param_list.append(0.)
        self.circuit_param_list.extend([0., 0., 0., 0., 0., 0., 0., 0., 0.])
        self.circuit_param_list = np.array(self.circuit_param_list, dtype=np.float64)

        self.core_state = None
        self.last_core_state = None
        self.state = None
        self.reactor = None
        self.integrator = integrator
        # 2. 动作
        self.action_mapping_table = [0]
        self.action_name = ['不动作']
        # 控制棒
        self.rod_action_dim = 4
        for i in range(self.rod_num):
            self.action_mapping_table.extend([-0.6, -0.4, -0.2, 0.2, 0.4, 0.6])
            # self.action_mapping_table.extend([-0.4, -0.2, 0.2, 0.4])
            self.action_name.append('控制棒' + str(i + 1) + '号高度减小3档')
            self.action_name.append('控制棒' + str(i + 1) + '号高度减小2档')
            self.action_name.append('控制棒' + str(i + 1) + '号高度减小1档')
            self.action_name.append('控制棒' + str(i + 1) + '号高度增加1档')
            self.action_name.append('控制棒' + str(i + 1) + '号高度增加2档')
            self.action_name.append('控制棒' + str(i + 1) + '号高度增加3档')
        # # Q1
        # self.action_mapping_table.extend([-5, 5])
        # self.action_name.append('主泵开度减小5%')
        # self.action_name.append('主泵开度增加5%')
        # # Q2
        # self.action_mapping_table.extend([-5, 5])
        # self.action_name.append('蒸汽发生器泵开度减小5%')
        # self.action_name.append('蒸汽发生器泵开度增加5%')
        # # T4
        # self.action_mapping_table.extend([-1, 1])
        # self.action_name.append('蒸汽发生器水温加热减小1%')
        # self.action_name.append('蒸汽发生器水温加热增加1%')
        # # 安注
        # self.action_mapping_table.extend([-5, 5])
        # self.action_name.append('安全注入箱开度减小5%')
        # self.action_name.append('安全注入箱开度增加5%')

        self.action_space = np.array(self.action_mapping_table, dtype=np.float32)
        self.action_dim = len(self.action_space)

        self.init_power = 1.0
        self.target_power = 240
        self.start_power = 300
        self.is_half_power = False

        # accident
        self.accident_name = ['100', '75', '50', 'lost of coolant accident', 'rod abnormal extraction']
        self.accident_list = [0, 0, 0, 0, 0]
        self.coolant_lost = 0
        self.rod_extraction = 15
        self.n_lost = 0
        self.real_Q1 = 0
        self.find_accident = 0

    def reset(self):
        # 清空参数
        self.device_proportion = []
        for i in range(self.rod_num):
            self.device_proportion.append(50.)
        self.device_proportion.extend([100., 100., 80., 0.])

        self.accident_list = [0, 0, 0, 0, 0]
        self.coolant_lost = 0
        self.rod_extraction = 15
        self.n_lost = 0
        self.real_Q1 = 0
        self.find_accident = random.uniform(6, 10)

        # 需要传入归一化后的中子数作为nr0，用功率替代，subcritical代表什么？
        self.reactor = Nu.NucBalance(subcritical=-0.1, n_init=self.init_power)
        # ！！！需要修改：传入T1

        # state0是堆芯平衡态的各项参数值，直接计算得来，属于固定数值
        self.last_core_state = self.reactor.status_vector
        self.power = self.last_core_state[0] * self.scale
        # 必须在status_vector赋值后
        self.update_circuit_param()

        # state0[0]是归一化的中子数，正是传入的n_init,pointer_h代表功率？scale是常数倍数？

        return np.concatenate((np.array([self.power], dtype=np.float64), np.array([self.device_proportion[0],
                                                                                   self.device_proportion[1]],
                                                                                  dtype=np.float64)), axis=0), {}

    def convert_proportion_to_value(self, proportion, value_range):
        ans = value_range[0] + proportion * (value_range[1] - value_range[0]) / 100
        return ans

    def update_core(self):
        self.core_state = Nu.Calculate_status(self.last_core_state, self.dt, self.integrator)

        # if self.accident_list[3] == 1:
        #     # self.core_state[0] = self.circuit_param_list[self.rod_num + 5] / 180 - random.uniform(0.25, 0.45)
        #     self.core_state[0] -= self.coolant_lost / 15000
        # if self.accident_list[4] == 1:
        #     if self.n_lost < 10000:
        #         self.n_lost += 100
        #     self.core_state[0] -= self.n_lost / 15000

        if self.accident_list[3] == 1 or self.accident_list[4] == 1:
            if self.episodic_step > self.find_accident:
                if self.n_lost == 0:
                    self.device_proportion[0] = 5
                    self.device_proportion[1] = 5
                    self.core_state[7] = -0.2 + random.uniform(-0.01, 0.01)
                if self.n_lost < 4:
                    self.n_lost += 1
                if self.n_lost == 1:
                    self.core_state[0] = 0.03 + random.uniform(-0.001, 0.005)
                elif self.n_lost == 2:
                    self.core_state[0] = 0.005 + random.uniform(-0.0001, 0.0005)
                elif self.n_lost == 3:
                    self.core_state[0] = 0.0005 + random.uniform(-0.00001, 0.00005)
                elif self.n_lost == 4:
                    self.core_state[0] = 0.0001 + random.uniform(-0.00001, 0.00005)

        self.power = self.core_state[0] * self.scale
        # parameter updating
        alpha_f = Nu.para_init().alpha_f()
        alpha_c = Nu.para_init().alpha_c()
        # Introduced reactivity
        sigma_Xe = Nu.para_init().section_Xe()
        Sigma_abs = Nu.para_init().section_absorb()
        # parameter change
        dtempf = self.core_state[9] - self.last_core_state[9]
        dtempc = self.core_state[10] - self.last_core_state[10]
        dXe = self.core_state[12] - self.last_core_state[12]
        self.last_core_state = self.core_state
        # drho
        self.drho_ = alpha_f * dtempf + alpha_c * dtempc - sigma_Xe * dXe / Sigma_abs
        self.last_core_state[7] += self.drho_

    def update_circuit_param(self):
        for i in range(len(self.device_name)):
            self.circuit_param_list[i] = self.convert_proportion_to_value(
                self.device_proportion[i], self.device_range[i])

        j = len(self.device_name)
        self.circuit_param_list[j] = self.last_core_state[15]
        self.circuit_param_list[j + 1] = self.last_core_state[10]
        # 计算T3和T5
        j = self.rod_num
        Q1 = self.circuit_param_list[j]
        Q2 = self.circuit_param_list[j + 1]
        T4 = self.circuit_param_list[j + 2]
        Q3 = self.circuit_param_list[j + 3]
        T1 = self.circuit_param_list[j + 4]
        T2 = self.circuit_param_list[j + 5]
        Q1 += Q3
        if self.accident_list[3] == 1:
            self.coolant_lost += 100
            if self.coolant_lost >= 5000:
                self.coolant_lost = 5000
            Q1 -= self.coolant_lost
        # real Q1,T2
        self.circuit_param_list[j + 8] = Q1
        # self.circuit_param_list[j + 5] += abs(Q3 - self.coolant_lost) / 100

        # T3 = T2 + (2 * T4 - 2 * self.k * Q2 * T2) / (self.k * Q2 + 2 * Q1 * Q2 + self.k * Q1)
        T3 = T2 - (2 * self.k * Q2 * T2) / (self.k * Q2 + 2 * Q1 * Q2 + self.k * Q1) + T4 - 220
        T5 = Q1 * (T2 - T3) / Q2 + T4
        if T5 >= T3:
            T5 = T3 - 5 + np.random.randint(-2, 2)

        self.circuit_param_list[j + 6] = T3
        self.circuit_param_list[j + 7] = T5

    def update_next_step(self):
        # T1 = T3
        self.last_core_state[15] = self.circuit_param_list[self.rod_num + 6]

    def start_accident(self, accident):
        self.accident_list[accident] = 1
        pos = self.accident_name.index('rod abnormal extraction')
        if accident == pos:
            self.last_core_state[7] += self.drho * self.rod_extraction * (
                    self.device_range[0][1] - self.device_range[0][0]) / 100
            self.device_proportion[0] += self.rod_extraction

    def half_power(self):
        self.last_core_state[7] -= self.drho * 2 * 20 * (
                self.device_range[0][1] - self.device_range[0][0]) / 100
        self.device_proportion[0] -= 20
        self.device_proportion[1] -= 20
        self.is_half_power = True

    # Update pointer position based on incoming action
    def step(self, action, episodic_step):
        self.episodic_step = episodic_step
        done = False
        info = '运行中'
        reward = 0.
        # Calculate next state based on action
        self.perform_action(action)
        self.update_core()
        self.update_circuit_param()
        self.state = np.concatenate((np.array([self.power], dtype=np.float64), np.array([self.device_proportion[0],
                                                                                         self.device_proportion[1]],
                                                                                        dtype=np.float64)), axis=0)
        # 更新T1=T3
        self.update_next_step()
        # reward function
        # reward = (-abs(self.power - self.target_power) + self.drho_) / 10

        # 1. 功率调整
        if self.accident_list.count(1) == 0:
            # reward = (-abs(self.last_core_state[0] - 1) * 300 + self.drho_) / 10 -\
            #          abs(50 - self.device_proportion[0]) * 10 - abs(50 - self.device_proportion[1]) * 10
            reward = (-abs(self.last_core_state[0] * self.scale - 1 * self.scale)) / 10
        elif self.accident_list[0] == 1:
            # reward = (-abs(self.last_core_state[0] - 1) * 300 + self.drho_) / 10 -\
            #          abs(50 - self.device_proportion[0]) * 10 - abs(50 - self.device_proportion[1]) * 10
            reward = (-abs(self.last_core_state[0] * self.scale - 1 * self.scale)) / 10
        elif self.accident_list[1] == 1:
            # reward = (-abs(self.last_core_state[0] - 0.75) * 300 + self.drho_) / 10 - \
            #          abs(40 - self.device_proportion[0]) * 10 - abs(40 - self.device_proportion[1]) * 10
            reward = (-abs(self.last_core_state[0] * self.scale - 0.75 * self.scale)) / 10
            # print((-abs(self.last_core_state[0] - 0.75) * 300 + self.drho_) / 10)
            # print((50 - self.device_proportion[0]) * 10)
            # print((50 - self.device_proportion[1]) * 10)
        elif self.accident_list[2] == 1:
            # reward = (-abs(self.last_core_state[0] - 0.5) * 300 + self.drho_) / 10 - \
            #          abs(20 - self.device_proportion[0]) * 10 - abs(20 - self.device_proportion[1]) * 10
            reward = (-abs(self.last_core_state[0] * self.scale - 0.5 * self.scale)) / 10

        # 2. 事故
        elif self.accident_list[3] == 1:
            reward = (180 - self.circuit_param_list[self.rod_num + 5]) / 5 - abs(
                self.circuit_param_list[self.rod_num + 8] - self.convert_proportion_to_value(
                    self.device_proportion[2], self.device_range[2])) / 500 - abs(
                self.device_proportion[self.rod_num + 3] - 100) / 10 - \
                     self.device_proportion[4] / 10
            # print(50 - self.device_proportion[self.rod_num + 2])
            # print(self.device_proportion[self.rod_num + 3] - 100)
        elif self.accident_list[4] == 1:
            reward = (180 - self.circuit_param_list[self.rod_num + 5]) / 5 - abs(
                self.circuit_param_list[self.rod_num + 8] - self.convert_proportion_to_value(
                    self.device_proportion[2], self.device_range[2])) / 500 + abs(
                self.device_proportion[self.rod_num + 3] - 100) / 10 - \
                     self.device_proportion[4] / 10

        # 事故
        if self.accident_list[3] == 1 or self.accident_list[4] == 1:
            if self.circuit_param_list[self.rod_num + 5] < 180:
                info = 'success'
                done = True
        # 功率
        # 满功率不停
        if self.accident_list[0] == 1:
            if self.last_core_state[0] - 1 >= 0.005:
                info = 'success'
                done = True
                # reward = 10000

        # 75功率停
        elif self.accident_list[1] == 1 and self.is_half_power:
            if self.last_core_state[0] - 0.75 >= 0.005:
                info = 'success'
                done = True
                # reward = 10000
        elif self.accident_list[1] == 1 and not self.is_half_power:
            if 0.75 - self.last_core_state[0] >= 0.005:
                info = 'success'
                done = True
                # reward = 10000

        # 半功率停
        elif self.accident_list[2] == 1:
            if 0.5 - self.last_core_state[0] >= 0.005:
                info = 'success'
                done = True
                # done = False
                # reward = 10000

        # T2 溢出
        if self.circuit_param_list[self.rod_num + 5] > 360 or min(self.circuit_param_list) < 0:
            info = 'T2溢出: ' + str(self.circuit_param_list[self.rod_num + 5])
            done = True

        elif self.accident_list[4] != 1 and self.last_core_state[0] > 1.15:
            info = '功率过高: ' + str(self.last_core_state[0]*self.scale)
            done = True

        elif self.accident_list[4] != 1 and self.last_core_state[0] < 0.35:
            info = '功率过低: ' + str(self.last_core_state[0]*self.scale)
            done = True

        elif self.accident_list[4] == 1 and self.last_core_state[0] > 3.8:
            info = '中子数膨胀: ' + str(self.last_core_state[0])
            done = True
        elif episodic_step > self.episode_step_max:
            done = True
            info = '超时'

        # 额外奖励
        # 满功率不停
        if self.accident_list[0] == 1:
            if abs(self.last_core_state[0] - 1) <= 0.1:
                reward += 1

            # 75功率停
        elif self.accident_list[1] == 1:
            if abs(self.last_core_state[0] - 0.75) <= 0.1:
                reward += 1

            # 半功率停
        elif self.accident_list[2] == 1:
            if abs(self.last_core_state[0] - 0.5) <= 0.1:
                reward += 1

        return self.state, reward, done, info

    def sample_action(self):
        # random action, return 0, 1, 2
        # action = np.random.randint(0, self.action_dim)
        # # 无需求
        # if action > self.rod_action_dim * self.rod_num and self.accident_list.count(1) == 0:
        #     action = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        # # 满功率
        # if self.accident_list[0] == 1:
        #     action = random.choice([3, 4, 5, 6, 6, 9, 10, 11, 12, 12])
        # # 75功率
        # if action > self.rod_action_dim * self.rod_num and self.accident_list[1] == 1:
        #     if self.is_half_power:
        #         action = random.choice([2, 3, 3, 4, 4, 6, 7, 7, 8, 8])
        #     else:
        #         action = random.choice([1, 1, 2, 3, 5, 6, 6, 7])
        # # 50功率
        # if self.accident_list[2] == 1:
        #     action = random.choice([1, 1, 2, 2, 3, 4, 7, 7, 8, 9, 10])
        # # loca
        # if self.accident_list[3] == 1:
        #     action = random.choice([0, 2, 3, 9, 10, 11, 12, 13, 13, 13, 16, 16, 16])
        # # rod accident
        # if self.accident_list[4] == 1:
        #     action = random.choice([0, 2, 3, 9, 10, 11, 12, 13, 13, 13, 15, 16])

        action = np.random.randint(0, self.action_dim)
        return action

    def update_device(self, device_index, diff):
        temp = self.device_proportion[device_index] + diff
        if 0 <= temp <= 100:
            self.device_proportion[device_index] += diff
            return True
        else:
            return False

    def perform_action(self, action):
        # action is index, real value is defined by self.action_list
        # if action > self.rod_action_dim * self.rod_num and self.accident_list.count(1) == 0:
        #     print('不作为')
        if action == 0:
            pass
            # print('0.不动作')
        elif 1 <= action <= self.rod_action_dim * self.rod_num:
            rod_index = (action - 1) // self.rod_action_dim
            self.update_device(rod_index, self.action_mapping_table[action])
            self.last_core_state[7] += self.drho * self.action_mapping_table[action] * (
                    self.device_range[rod_index][1] - self.device_range[rod_index][0]) / 100
            # print('1.控制棒%f号改变%f后成为%f' % (
            #     rod_index, self.action_mapping_table[action], self.device_proportion[rod_index]))
        elif action <= self.rod_action_dim * self.rod_num + 2:
            self.update_device(self.rod_num, self.action_mapping_table[action])
            # print('2.主泵改变%f后成为%f' % (self.action_mapping_table[action], self.device_proportion[self.rod_num]))
        elif action <= self.rod_action_dim * self.rod_num + 4:
            self.update_device(self.rod_num + 1, self.action_mapping_table[action])
            # print('3.蒸汽发生器泵改变%f后成为%f' % (
            #     self.action_mapping_table[action], self.device_proportion[self.rod_num + 1]))
        elif action <= self.rod_action_dim * self.rod_num + 6:
            self.update_device(self.rod_num + 2, self.action_mapping_table[action])
            # print('4.蒸汽发生器水温改变%f后成为%f' % (
            #     self.action_mapping_table[action], self.device_proportion[self.rod_num + 2]))
        elif action <= self.rod_action_dim * self.rod_num + 8:
            self.update_device(self.rod_num + 3, self.action_mapping_table[action])
            # print('5.安全注入改变%f后成为%f' % (
            #     self.action_mapping_table[action], self.device_proportion[self.rod_num + 3]))

    def render(self):
        pass

    def show(self):
        print('accident is: %f' % self.state[0])
        print('accident is: %f' % self.state[1])
        print('accident is: %f' % self.state[2])
        print('accident is: %f' % self.state[3])
        print('accident is: %f' % self.state[4])

        print('n is: %f' % self.state[5])
        print('Cr[0] is: %f' % self.state[6])
        print('Cr[1] is: %f' % self.state[7])
        print('Cr[2] is: %f' % self.state[8])
        print('Cr[3] is: %f' % self.state[9])
        print('Cr[4] is: %f' % self.state[10])
        print('Cr[5] is: %f' % self.state[11])
        print('subcritical is: %f' % self.state[12])
        print('source0 is: %f' % self.state[13])
        print('temp_f is: %f' % self.state[14])
        print('temp_c is: %f' % self.state[15])
        print('density_I is: %f' % self.state[16])
        print('density_Xe is: %f' % self.state[17])
        print('density_Pm is: %f' % self.state[18])
        print('density_Sm is: %f' % self.state[19])
        print('temp_in is: %f' % self.state[20])
        print('rod1 is: %f' % self.state[21])
        print('rod2 is: %f' % self.state[22])
        print('Q1 is: %f' % self.state[23])
        print('Q2 is: %f' % self.state[24])
        print('T4 is: %.10f' % self.state[25])
        print('Q3 is: %f' % self.state[26])
        print('T1 is: %.10f' % self.state[27])
        print('T2 is: %.10f' % self.state[28])
        print('T3 is: %.10f' % self.state[29])
        print('T5 is: %.10f' % self.state[30])
        print('real Q1 is: %.10f' % self.state[31])
        print('-' * 20)


if __name__ == '__main__':
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
    plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

    power_env = NuclearEnv('dopri5', rod_num=2)
    state0 = power_env.reset()

    n_list = []
    power_list = []
    t = []
    power_list.append(power_env.power)
    n_list.append(power_env.last_core_state[0])
    t.append(0)
    for i in tqdm(range(1501)):
        # input()
        state1, r, done, info = power_env.step(0, 0)
        power_list.append(power_env.power)
        n_list.append(power_env.last_core_state[0])
        t.append(i + 1)
        # print('step ' + str(i+1))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4, 6))
    y1 = n_list
    x1 = t
    ax1.plot(x1, y1)
    ax1.set_xlabel('step')
    ax1.set_ylabel('Normalized neutron density(cm$^{-3}$)')
    ax1.grid()

    y2 = power_list
    x2 = t
    ax2.plot(x2, y2)
    ax2.set_xlabel('step')
    ax2.set_ylabel('Power(MW)')
    ax2.grid()

    plt.tight_layout()
    plt.savefig("./figures/env.png", dpi=300)
    plt.show()

