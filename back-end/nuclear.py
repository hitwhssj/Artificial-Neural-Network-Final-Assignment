import time
import os
import gym
import math
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from decimal import Decimal

from env import NuclearEnv


class ReplayMemory(object):

    def __init__(self, capacity, Transition):
        self.memory = deque([], maxlen=capacity)
        self.transition = Transition

    def push(self, *args):
        """Save a transition"""
        self.memory.append(self.transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DQN(nn.Module):

    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)


class VAnet(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(VAnet, self).__init__()
        self.fc1 = nn.Linear(n_observations, 128)  # 共享网络部分
        self.fc_A = nn.Linear(128, n_actions)
        self.fc_V = nn.Linear(128, 1)

    def forward(self, x):
        A = self.fc_A(F.relu(self.fc1(x)))
        V = self.fc_V(F.relu(self.fc1(x)))
        Q = V + A - A.mean(1).view(-1, 1)  # Q值由V值和A值计算得到
        return Q


class Nuclear:
    def __init__(self, run_mode, operating_mode, algorithm='DQN', init_power=1.0):
        # 初始化环境
        self.env = None
        if gym.__version__[:4] == '0.26':
            self.env = NuclearEnv('dopri5', rod_num=2)
        elif gym.__version__[:4] == '0.25':
            self.env = NuclearEnv('dopri5', rod_num=2)
        else:
            raise ImportError(f"Requires gym v25 or v26, actual version: {gym.__version__}")

        # 选择cpu模式还是gpu模式
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # self.device = torch.device("cpu")
        self.algorithm = algorithm
        self.init_power = init_power

        # 定义工具类
        self.Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

        # 常量：用于optimize_model函数，train专用
        self.BATCH_SIZE = 128
        self.GAMMA = 0.99
        self.TAU = 0.005

        # 常量：用于select_action，train，test公用
        self.EPS_START = 0.9
        self.EPS_END = 0.05
        self.EPS_DECAY = 1000

        # 定义空白模型
        if gym.__version__[:4] == '0.26':
            self.state, _ = self.env.reset()
        elif gym.__version__[:4] == '0.25':
            self.state, _ = self.env.reset()
        self.n_observations = len(self.state)
        self.n_actions = self.env.action_dim
        if self.algorithm == 'Dueling DQN':
            self.policy_net = VAnet(self.n_observations, self.n_actions).to(self.device)
            self.target_net = VAnet(self.n_observations, self.n_actions).to(self.device)
        else:
            self.policy_net = DQN(self.n_observations, self.n_actions).to(self.device)
            self.target_net = DQN(self.n_observations, self.n_actions).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        # 变量：用于optimizer_model，train专用
        self.LR = 1e-4
        self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=self.LR, amsgrad=True)
        self.memory = ReplayMemory(10000, self.Transition)

        # 变量：用于seletc_action，train和test公用
        self.steps_done = 0
        self.step = 0

        # 记录数据的变量，train和test公用，提供给flask_app查看
        self.run_mode = run_mode
        self.operation_mode = operating_mode

        self.action = None
        self.advice_action = None
        self.observation = None
        self.reward = None
        self.done = None
        self.next_state = None
        self.image = None
        self.info = 'reset'
        # 模型文件路径
        self.policy_net_model_file_path = './models/policy_net'
        self.target_net_model_file_path = './models/target_net'

        # 对以上信息的进一步封装，直接提供给后端发送给前端
        self.suggested_action = None
        self.current_time = time.localtime()
        self.simulation_time = []
        self.step_status_data = []
        self.status_data = []
        self.step_param_data = []
        self.param_data = []
        self.step_core_param_data = []
        self.core_param_data = []
        self.step_device_data = []
        self.device_data = []
        self.step_action_data = []
        self.action_data = []
        self.real_action_data = []
        self.p_t_data = []
        self.param_chart_data = {
            'rod_1': {'name': '1号控制棒距底部的高度', 'code_name': 'rod_1', 'index': 0, 'unit': '', 'data': []},
            'rod_2': {'name': '2号控制棒距底部的高度', 'code_name': 'rod_2', 'index': 0, 'unit': '', 'data': []},
            'Q1': {'name': '一回路入口流量', 'code_name': 'Q1', 'index': 0, 'unit': ' m³/h', 'data': []},
            'Q2': {'name': '二回路流量', 'code_name': 'Q2', 'index': 0, 'unit': ' m³/h', 'data': []},
            'T4': {'name': '二回路输入温度', 'code_name': 'T4', 'index': 0, 'unit': ' ℃', 'data': []},
            'Q3': {'name': '安全注入补给流量', 'code_name': 'Q3', 'index': 0, 'unit': ' m³/h', 'data': []},
            'T1': {'name': '反应堆入口冷却剂温度', 'code_name': 'T1', 'index': 0, 'unit': ' ℃', 'data': []},
            'T2': {'name': '反应堆出口冷却剂温度', 'code_name': 'T2', 'index': 0, 'unit': ' ℃', 'data': []},
            'T3': {'name': '一回路热交换输出温度', 'code_name': 'T3', 'index': 0, 'unit': ' ℃', 'data': []},
            'T5': {'name': '二回路输出温度', 'code_name': 'T5', 'index': 0, 'unit': ' ℃', 'data': []},
            'Q1_real': {'name': '一回路实际流量', 'code_name': 'Q1_real', 'index': 0, 'unit': ' ℃', 'data': []},
            'power': {'name': '功率', 'code_name': 'power', 'unit': ' MW', 'data': []},
            'n': {'name': '归一化后的中子数', 'code_name': 'n', 'unit': ' ', 'data': []},
            'Cr1': {'name': '缓发中子先驱核浓度1', 'code_name': 'Cr1', 'unit': ' ', 'data': []},
            'Cr2': {'name': '缓发中子先驱核浓度2', 'code_name': 'Cr2', 'unit': ' ', 'data': []},
            'Cr3': {'name': '缓发中子先驱核浓度3', 'code_name': 'Cr3', 'unit': ' ', 'data': []},
            'Cr4': {'name': '缓发中子先驱核浓度4', 'code_name': 'Cr4', 'unit': ' ', 'data': []},
            'Cr5': {'name': '缓发中子先驱核浓度5', 'code_name': 'Cr5', 'unit': ' ', 'data': []},
            'Cr6': {'name': '缓发中子先驱核浓度6', 'code_name': 'Cr6', 'unit': ' ', 'data': []},
            'rho': {'name': '反应性', 'code_name': 'rho', 'unit': ' ', 'data': []},
            'source': {'name': '源项', 'code_name': 'source', 'unit': ' ', 'data': []},
            'Tf': {'name': '燃料平均温度', 'code_name': 'Tf', 'unit': ' ℃', 'data': []},
            'T22': {'name': '堆芯出口温度', 'code_name': 'T22', 'unit': ' ℃', 'data': []},
            'I': {'name': '碘I', 'code_name': 'I', 'unit': ' ', 'data': []},
            'Xe': {'name': '氙Xe', 'code_name': 'Xe', 'unit': ' ', 'data': []},
            'Pm': {'name': '钷Pm', 'code_name': 'Pm', 'unit': ' ', 'data': []},
            'Sm': {'name': '钐Sm', 'code_name': 'Sm', 'unit': ' ', 'data': []},
            'reward': {'name': '奖励值', 'code_name': 'reward', 'unit': ' ', 'data': []},
            'action': {'name': '动作', 'code_name': 'action', 'unit': ' ', 'data': []},
            'advice_action': {'name': '建议动作', 'code_name': 'advice_action', 'unit': ' ', 'data': []}
        }
        self.statuses = [
            # status data
            {'name': '100%功率模式', 'code_name': None, 'index': None},
            {'name': '75%功率模式', 'code_name': None, 'index': None},
            {'name': '50%功率模式', 'code_name': None, 'index': None},
            # {'name': '一回路冷却液泄露事故', 'code_name': None, 'index': None},
            # {'name': '控制棒失控抽出事故', 'code_name': None, 'index': None},
        ]
        self.circuit_params = [
            {'name': '1号控制棒高度', 'code_name': 'rod_1', 'index': 0, 'unit': ' '},
            {'name': '2号控制棒高度', 'code_name': 'rod_2', 'index': 0, 'unit': ' '},
            {'name': '一回路流量', 'code_name': 'Q1', 'index': 0, 'unit': ' m³/h'},
            {'name': '二回路流量', 'code_name': 'Q2', 'index': 0, 'unit': ' m³/h'},
            {'name': '二回路输入温度', 'code_name': 'T4', 'index': 0, 'unit': ' ℃'},
            {'name': '安全注入补给流量', 'code_name': 'Q3', 'index': 0, 'unit': ' m³/h'},
            {'name': '反应堆入口冷却剂温度', 'code_name': 'T1', 'index': 0, 'unit': ' ℃'},
            {'name': '反应堆出口冷却剂温度', 'code_name': 'T2', 'index': 0, 'unit': ' ℃'},
            {'name': '一回路热交换输出温度', 'code_name': 'T3', 'index': 0, 'unit': ' ℃'},
            {'name': '二回路输出温度', 'code_name': 'T5', 'index': 0, 'unit': ' ℃'},
            {'name': '一回路实际流量', 'code_name': 'Q1_real', 'index': 0, 'unit': ' m³/h'}
        ]
        self.core_params = [
            # {'name': '功率', 'code_name': 'power', 'unit': ' MW'},
            {'name': '归一化后的中子数', 'code_name': 'n', 'unit': ' '},
            {'name': '缓发中子先驱核浓度1', 'code_name': 'Cr1', 'unit': ' '},
            {'name': '缓发中子先驱核浓度2', 'code_name': 'Cr2', 'unit': ' '},
            {'name': '缓发中子先驱核浓度3', 'code_name': 'Cr3', 'unit': ' '},
            {'name': '缓发中子先驱核浓度4', 'code_name': 'Cr4', 'unit': ' '},
            {'name': '缓发中子先驱核浓度5', 'code_name': 'Cr5', 'unit': ' '},
            {'name': '缓发中子先驱核浓度6', 'code_name': 'Cr6', 'unit': ' '},
            {'name': '反应性', 'code_name': 'rho', 'unit': ' '},
            {'name': '外源项', 'code_name': 'source', 'unit': ' '},
            {'name': '燃料平均温度', 'code_name': 'source', 'unit': ' ℃'},
            {'name': '堆芯出口温度', 'code_name': 'T2', 'unit': ' ℃'},
            {'name': '碘I', 'code_name': 'I', 'unit': ' '},
            {'name': '氙Xe', 'code_name': 'Xe', 'unit': ' '},
            {'name': '钷Pm', 'code_name': 'Pm', 'unit': ' '},
            {'name': '钐Sm', 'code_name': 'Sm', 'unit': ' '},
        ]
        self.devices = [
            # A B合一
            {'name': '1号控制棒', 'code_name': 'rod_1', 'index': 27, 'unit': None},
            {'name': '2号控制棒', 'code_name': 'rod_2', 'index': 27, 'unit': None},
            {'name': '一回路主泵', 'code_name': 'main_pump', 'index': 27, 'unit': None},
            {'name': '蒸汽发生器泵', 'code_name': 'ARE_pump', 'index': 27, 'unit': None},
            {'name': '蒸汽发生器水温', 'code_name': 'ARE_water_temperature', 'index': 27, 'unit': None},
            {'name': '安全注入箱', 'code_name': 'security_injection', 'index': 27, 'unit': None}
        ]

    def select_action(self):
        sample = random.random()
        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
                        math.exp(-1. * self.steps_done / self.EPS_DECAY)
        if self.env.accident_list.count(1) != 0:
            self.steps_done += 1
        if sample > eps_threshold or self.run_mode == 'test':
            with torch.no_grad():
                return self.policy_net(self.state).max(1)[1].view(1, 1)
        else:
            return torch.tensor([[self.env.sample_action()]], device=self.device, dtype=torch.long)

    def optimize_model(self):
        if len(self.memory) < self.BATCH_SIZE:
            return
        transitions = self.memory.sample(self.BATCH_SIZE)
        batch = self.Transition(*zip(*transitions))

        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), device=self.device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                           if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        next_state_values = torch.zeros(self.BATCH_SIZE, device=self.device)
        with torch.no_grad():
            if self.algorithm == 'Double DQN':
                # print(self.algorithm + '更新')
                max_action = self.policy_net(non_final_next_states).max(1)[1].view(-1, 1)
                # print(max_action.shape)
                # print(action_batch.shape)
                # print(self.target_net(non_final_next_states).shape)
                # print(self.target_net(non_final_next_states).max(1)[0].shape)
                # print('start')
                # print(self.target_net(non_final_next_states).gather(1, max_action).shape)
                next_state_values[non_final_mask] = self.target_net(non_final_next_states).gather(1, max_action).view(-1)
            else:
                # print(self.algorithm + '更新')
                next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0]
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.GAMMA) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        # In-place gradient clipping
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()

    def reset_env(self):
        self.suggested_action = None
        self.current_time = time.localtime()
        self.simulation_time = []
        self.step_status_data = []
        self.status_data = []
        self.step_param_data = []
        self.param_data = []
        self.step_core_param_data = []
        self.core_param_data = []
        self.step_device_data = []
        self.device_data = []
        self.step_action_data = []
        self.action_data = []
        self.real_action_data = []
        self.p_t_data = []
        self.done = False
        for key in self.param_chart_data:
            self.param_chart_data[key]['data'] = []
        # self.steps_done = 0
        # self.step = 1
        if gym.__version__[:4] == '0.26':
            self.state, _ = self.env.reset()
        elif gym.__version__[:4] == '0.25':
            self.state, _ = self.env.reset()
        self.state = torch.tensor(self.state, dtype=torch.float32, device=self.device).unsqueeze(0)

    def run_one_step(self, expert_action=None, real_step=0):
        if self.operation_mode == 'expert':
            self.action = expert_action
            self.advice_action = self.select_action()
            if self.advice_action.item() > self.env.rod_action_dim * self.env.rod_num \
                    and self.env.accident_list.count(1) != 0 and self.env.accident_list.index(1) <= 2 \
                    or self.env.accident_list.count(1) == 0:
                self.advice_action = torch.tensor([[0]], device=self.device, dtype=torch.long)
        else:
            self.action = self.select_action()
            if self.action.item() > self.env.rod_action_dim * self.env.rod_num \
                    and self.env.accident_list.count(1) != 0 and self.env.accident_list.index(1) <= 2 \
                    or self.env.accident_list.count(1) == 0:
                self.action = torch.tensor([[0]], device=self.device, dtype=torch.long)
            self.advice_action = self.action
        self.observation, self.reward, self.done, self.info = self.env.step(self.action.item(), real_step)
        self.reward = torch.tensor([self.reward], device=self.device)

        if self.done:
            # self.next_state = None
            self.next_state = torch.tensor(self.observation, dtype=torch.float32, device=self.device).unsqueeze(0)
        else:
            self.next_state = torch.tensor(self.observation, dtype=torch.float32, device=self.device).unsqueeze(0)

        if self.run_mode == 'train' and self.env.accident_list.count(1) != 0:
            # Store the transition in memory
            # print('更新模型')
            self.memory.push(self.state, self.action, self.next_state, self.reward)

        # Move to the next state
        self.state = self.next_state

        if self.run_mode == 'train' and self.env.accident_list.count(1) != 0:
            # Perform one step of the optimization (on the policy network)
            # print('更新模型')
            self.optimize_model()

            # Soft update of the target network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            target_net_state_dict = self.target_net.state_dict()
            policy_net_state_dict = self.policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key] * self.TAU + target_net_state_dict[key] * (
                        1 - self.TAU)
            self.target_net.load_state_dict(target_net_state_dict)
        self.step += 1
        self.current_time = time.localtime()

    def save_model(self):
        current_time = self.current_time
        current_time = time.strftime("%Y-%m-%d_%H_%M_%S", current_time)
        mission = ''
        for i in range(len(self.env.accident_list)):
            if self.env.accident_list[i] == 1:
                mission += self.env.accident_name[i] + '_'
        mission = str(self.algorithm) + '_' + str(self.init_power) + '_' + mission
        name = 'model_' + mission + current_time + '.pt'
        policy_net_path = os.path.join('./models/policy_net', name)
        target_net_path = os.path.join('./models/target_net', name)

        torch.save(self.policy_net.state_dict(), policy_net_path)
        torch.save(self.target_net.state_dict(), target_net_path)

    def load_model(self, name):
        policy_net_path = os.path.join('./models/policy_net', name)
        target_net_path = os.path.join('./models/target_net', name)
        self.policy_net.load_state_dict(torch.load(policy_net_path))
        self.target_net.load_state_dict(torch.load(target_net_path))

    def save_data(self):
        file_path = './data'
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)

        current_time = self.current_time
        current_time = time.strftime("%Y-%m-%d-%H-%M-%S", current_time)

        # status
        # name = 'status-' + current_time + '.xlsx'
        name = 'status.xlsx'
        status_file_name = os.path.join(file_path, name)
        status_data = pd.DataFrame(self.status_data)
        status_data.to_excel(status_file_name, engine='openpyxl')

        # param
        # name = 'param-' + current_time + '.xlsx'
        name = 'param.xlsx'
        param_file_name = os.path.join(file_path, name)
        param_data = pd.DataFrame(self.param_data)
        param_data.to_excel(param_file_name, engine='openpyxl')

        name = 'core_param.xlsx'
        core_param_file_name = os.path.join(file_path, name)
        core_param_data = pd.DataFrame(self.core_param_data)
        core_param_data.to_excel(core_param_file_name, engine='openpyxl')

        # device
        # name = 'device-' + current_time + '.xlsx'
        name = 'device.xlsx'
        device_file_name = os.path.join(file_path, name)
        device_data = pd.DataFrame(self.device_data)
        device_data.to_excel(device_file_name, engine='openpyxl')

        # action
        name = 'action.xlsx'
        action_file_name = os.path.join(file_path, name)
        action_data = pd.DataFrame(self.action_data)
        action_data.to_excel(action_file_name, engine='openpyxl')
        # if self.mode == 'automatic':
        #     action_data.to_excel(action_file_name, columns=['step', 'action_num', 'action', 'time', 'reward'])
        # elif self.mode == 'expert':
        #     action_data.to_excel(action_file_name, columns=['step', 'action_num', 'action', 'suggested_action_num',
        #                                                     'suggested_action', 'time', 'reward'])

    def close(self):
        # self.env.close()
        pass

    def pack_step_data(self):
        self.current_time = time.localtime()
        self.simulation_time.append(self.step)

        # state = self.observation.tolist()
        circuit_param = self.env.circuit_param_list.tolist()
        core_param = self.env.last_core_state
        status = self.env.accident_list
        device_env = self.env.device_proportion
        action = self.action.item() if self.action is not None else None
        advice_action = self.advice_action.item() if self.advice_action is not None else None
        reward = self.reward.item() if self.reward is not None else None

        # status_param_table_data
        self.step_status_data = []
        for i in range(len(self.statuses)):
            self.step_status_data.append(
                {'name': self.statuses[i]['name'], 'value': '触发' if status[i] else '未触发'}
            )
        self.status_data.append({
            self.statuses[i]['name']: '触发' if status[i] else '未触发' for i in range(len(self.statuses))
        })

        # key_param_table
        self.step_param_data = []
        for i in range(len(self.circuit_params)):
            self.step_param_data.append(
                {'name': self.circuit_params[i]['name'],
                 'value': str(round(circuit_param[i], 2)) + self.circuit_params[i]['unit']}
            )
        self.param_data.append({
            self.circuit_params[i]['name'] + self.circuit_params[i]['unit']:
                round(circuit_param[i], 2) for i in range(len(self.circuit_params))
        })
        # self.step_core_param_data = [self.env.power]
        self.step_core_param_data = [{
            'name': '功率',
            'value': str(round(self.env.power, 4)) + 'MW'
        }]
        for i in range(len(self.core_params)):
            self.step_core_param_data.append(
                {'name': self.core_params[i]['name'],
                 'value': str(round(core_param[i], 2)) + self.core_params[i]['unit']}
                if i > 0 else {'name': self.core_params[i]['name'],
                 'value': str(round(core_param[i], 6)) + self.core_params[i]['unit']}
            )
        self.core_param_data.append({
            self.core_params[i]['name'] + self.core_params[i]['unit']:
                round(core_param[i], 2) for i in range(len(self.core_params))
        })

        # key_device_table
        self.step_device_data = []
        for i in range(len(self.devices)):
            self.step_device_data.append(
                {'name': self.devices[i]['name'], 'value': str(round(device_env[i], 1)) + ' %'}
            )

        self.device_data.append({
            self.devices[i]['name']: round(device_env[i], 1) for i in range(len(self.devices))
        })

        # action_history_table
        self.step_action_data.append({
            'step': self.step,
            'action_num': action if action is not None else '执行reset：无action',
            'action': self.env.action_name[action] if action is not None else '执行reset：无action',
            'suggested_action_num': advice_action if advice_action is not None else '执行reset：无action',
            'suggested_action': self.env.action_name[advice_action] if advice_action is not None else '执行reset：无action',
            'time': 'time: ' + str(self.simulation_time[-1]),
            'reward': round(reward, 2) if self.reward is not None else '无reward',
            'color': '#0bbd87'
        })
        self.action_data.append({
            'step': self.step,
            'action_num': action if action is not None else '执行reset：无action',
            'action': self.env.action_name[action] if action is not None else '执行reset：无action',
            'suggested_action_num': advice_action if advice_action is not None else '执行reset：无action',
            'suggested_action': self.env.action_name[advice_action] if advice_action is not None else '执行reset：无action',
            'time': 'time: ' + str(self.simulation_time[-1]),
            'reward': round(reward, 2) if self.reward is not None else '无reward',
            'color': '#0bbd87'
        })

        # P_T_chart
        self.p_t_data.append([circuit_param[7], self.env.power])

        # chart_data
        temp = list(core_param)
        chart_param = circuit_param + [self.env.power] + temp[0:-1] + [reward, action, advice_action]
        for i, key in enumerate(self.param_chart_data.keys()):
            self.param_chart_data[key]['data'].append(chart_param[i])

        data = {
            # 后端只记录最新的status_param_table_data
            'status_param_table_data': self.step_status_data,
            # 后端只记录最新的key_param_table_data
            'key_param_table_data': self.step_param_data,
            'core_param_table_data': self.step_core_param_data,
            'key_device_table_data': self.step_device_data,
            'action_history_table_data': self.step_action_data,
            # charts
            'pressure_temperature_chart_data': self.p_t_data,
            'param_chart_data': self.param_chart_data,
            'simulation_time': self.simulation_time
        }
        return data


if __name__ == '__main__':
    model = Nuclear(run_mode='train', operating_mode='automatic', algorithm='Double DQN')
    n = 1
    for i in range(n):
        # train n Episode
        model.reset_env()
        model.pack_step_data()

        # model.load_model('model_2023-04-29_10_35_08.pt')
        model.env.start_accident(0)
        for t in count():
            model.run_one_step()
            model.env.show()
            model.pack_step_data()
            print(model.info)

            if model.done:
                # model.episode_duration_list.append(t + 1)
                print('over')
                model.save_model()
                model.save_data()
                break

