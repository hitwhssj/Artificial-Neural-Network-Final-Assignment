from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from threading import Lock
import os
import random
import time
import matplotlib
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import pandas as pd
from itertools import count
from decimal import Decimal

from nuclear import Nuclear

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources=r'/*')
socketio = SocketIO(app, cors_allowed_origins='*')

thread = None
lock = Lock()
state = None
constraints = {
    'start': False,
    'continue': False,
    'pause': False,
    'stop': False,
    'end': False,
}
model_file_path = './models/policy_net'

expert_action_flag = '等待专家动作'
expert_action_data = {
    'index': 0,
    'value': '0.不动作'
}
start_accident = False
accident_list = [0, 0, 0, 0, 0]
accident = -1


@app.route("/get-model-file-name")
def get_model_file_name():
    model_file_list = os.listdir(model_file_path)
    model_file_list.reverse()
    return model_file_list


@socketio.on('connect')
def connect():
    print('Client connected\n')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected\n')


@socketio.on('expert_action')
def update_expert_action(message):
    global expert_action_data, expert_action_flag
    expert_action_data = message
    expert_action_flag = '收到专家动作'
    print('\n收到了专家数据：' + str(expert_action_data) + '\n')


@socketio.on('start_accident')
def update_accident_list(message):
    global accident_list, accident
    accident = message
    print('\n收到了accident数据：' + str(accident) + '\n')


@socketio.on('control_message')
def receive_msg(message):
    global thread, state, constraints
    with lock:
        if message['control_signal'] == 'start':
            if thread is None:
                print('\n开始\n')
                state = 'start'
                constraints['start'] = True
                if message['run_mode'] == 'train':
                    thread = socketio.start_background_task(background_thread_automatic,
                                                            {'run_mode': 'train',
                                                             'algorithm': message['algorithm'],
                                                             'init_power': message['init_power'],
                                                             'automatic_save': message['automatic_save'],
                                                             'operating_mode': message['operating_mode']})
                elif message['run_mode'] == 'test':
                    thread = socketio.start_background_task(background_thread_automatic,
                                                            {'run_mode': 'test',
                                                             'algorithm': message['algorithm'],
                                                             'init_power': message['init_power'],
                                                             'load_model_file_name': message['load_model_file_name'],
                                                             'operating_mode': message['operating_mode']})
            else:
                print('\n继续\n')
                state = 'continue'
                constraints['continue'] = True
        elif message['control_signal'] == 'pause':
            print('\n暂停\n')
            state = 'pause'
            constraints['pause'] = True
        elif message['control_signal'] == 'stop':
            print('\n结束\n')
            state = 'stop'
            constraints['stop'] = True
        else:
            print("\n错误：收到非法信号\n")


def background_thread_automatic(param):
    global thread, constraints, expert_action_data, expert_action_flag, accident_list, accident
    accident = -1

    # 获取参数
    run_mode = param['run_mode']
    init_power = param['init_power']
    algorithm = param['algorithm']
    automatic_save = None
    load_model_file_name = None
    operating_mode = param['operating_mode']
    # train only
    if run_mode == 'train':
        automatic_save = param['automatic_save']
        print('\n*******自动保存变量（%s, %s）*******\n' % (run_mode, operating_mode))
        print(automatic_save)
    # test only
    elif run_mode == 'test':
        load_model_file_name = param['load_model_file_name']
        print('\n*******要加载的模型（%s, %s）*******\n' % (run_mode, operating_mode))
        print('模型是：' + load_model_file_name)

    # 定义模型
    print('\n*******算法（%s, %s）*******\n' % (run_mode, operating_mode))
    print('算法是：' + algorithm)
    model = Nuclear(run_mode=run_mode, operating_mode=operating_mode, algorithm=algorithm, init_power=init_power)

    # # 未触发accident
    # while not start_accident:
    #     model.run_one_step(out_action=torch.tensor([[0]], device=model.device, dtype=torch.long))
    #     data = model.pack_step_data()
    #     socketio.emit('data_message', data)
    #     print(data['action_history_table_data'])
    #     socketio.sleep(0.8)

    model.reset_env()
    if run_mode == "test" and load_model_file_name is not None and load_model_file_name != "":
        model.load_model(load_model_file_name)
        print('\n*******模型加载完成（%s, %s）*******\n' % (run_mode, operating_mode))

    if init_power == 0.5:
        model.env.half_power()
        # for i in range(80):
        #     model.run_one_step()

    # accident = 2

    # 发送reset数据
    # data = model.pack_step_data()
    # socketio.emit('data_message', data)
    for t in count():
        # 判断线程状态
        if state == 'start':
            print('\n*******模型运行中（%s, %s）*******\n' % (run_mode, operating_mode))
            if constraints['start']:
                # 通知前端解锁按钮
                socketio.emit('remove_constraints', {'sync_signal': 'start_over'})
                constraints['start'] = False
            if operating_mode == 'automatic':
                socketio.sleep(0.3)
                pass
            else:
                socketio.sleep(2)
        elif state == 'continue':
            print('\n*******模型运行中（%s, %s）*******\n' % (run_mode, operating_mode))
            if constraints['continue']:
                socketio.emit('remove_constraints', {'sync_signal': 'continue_over'})
                constraints['continue'] = False
            if operating_mode == 'automatic':
                socketio.sleep(0.3)
                pass
            else:
                socketio.sleep(2)
        elif state == 'pause':
            print('\n*******模型已暂停（%s, %s）*******\n' % (run_mode, operating_mode))
            if constraints['pause']:
                socketio.emit('remove_constraints', {'sync_signal': 'pause_over'})
                constraints['pause'] = False
            socketio.sleep(2)
            continue
        elif state == 'stop':
            # 具体终止逻辑在下方
            break

        # 正式开始运行
        if expert_action_flag == '收到专家动作':
            expert_action_flag = '执行专家动作'

        if accident != -1:
            model.env.start_accident(accident)
            accident = -1
        # model.env.accident_list = accident_list
        if operating_mode == 'automatic':
            model.run_one_step()
            # if model.env.accident_list.count(1) > 0:
            #     model.run_one_step()
            # else:
            #     model.run_one_step(expert_action=torch.tensor([[0]], device=model.device, dtype=torch.long))
        elif operating_mode == 'expert':
            model.run_one_step(expert_action=torch.tensor(
                [[expert_action_data['index']]], device=model.device, dtype=torch.long))

        if expert_action_flag == '执行专家动作':
            expert_action_data = {
                'index': 0,
                'value': '0.不动作'
            }
            expert_action_flag = '等待专家动作'
            socketio.emit('remove_expert_action', {'expert_action_data': expert_action_data})

        # 拼接后发送前端
        data = model.pack_step_data()
        socketio.emit('data_message', data)
        if model.done:
            state_board = {'info': model.info}
            socketio.emit('episode_end', {'state_board': state_board})
            # socketio.sleep(2)
            # if model.info != 'success' or model.env.accident_list[3] == 1 or model.env.accident_list[4] == 1:
            #     break
            # else:
            #     model.env.accident_list = [0, 0, 0, 0, 0]
            break

    if run_mode == "train" and automatic_save:
        model.save_model()
        print('\n*******模型存储完成（%s, %s）*******\n' % (run_mode, operating_mode))

    # always
    model.save_data()
    print('\n*******数据存储完成（%s, %s）*******\n' % (run_mode, operating_mode))

    if state == 'stop':
        print('\n*******手动终止！（%s, %s）*******\n' % (run_mode, operating_mode))
        if constraints['stop']:
            socketio.emit('remove_constraints', {'sync_signal': 'stop_over'})
            constraints['stop'] = False
    else:
        # 此次正常执行结束
        print('\n*******模型正常运行结束！（%s, %s）*******\n' % (run_mode, operating_mode))
        socketio.emit('remove_constraints', {'sync_signal': 'end_over'})

    thread = None

