# -*- coding: utf-8 -*-

import numpy as np


# Initialization
class para_init(object):
    def __init__(self):
        # 缓发中子份额β1-β6，用于计算点堆方程公式2-7，数值来自经典压水堆参数设定
        self.beta_list = [0.00017, 0.00106, 0.00118, 0.00321, 0.00111, 0.00035]
        # 缓发中子份额求和
        self.beta_sum = sum(self.beta_list)
        # 缓发中子先驱核衰变常数λi，用于计算点堆方程公式2-7，数值来自经典压水堆参数设定
        self.lambda_list = [0.01249, 0.03156, 0.11063, 0.32256, 1.34188, 9.00518]
        # 中子代时间Λ，用于计算点堆方程公式2-7，数值来自表2.3
        self.Lambda = 2e-5

        # 反应堆初始功率，用于计算反应性温度反馈2-13，来自表2.1，数值无来源
        self.p0 = 2500  # MW
        # 初始中子数，用于归一化，计算通量Φ时要×n0，数值来自表2.3
        self.n0 = 5e8  # n·cm^-3

        # 燃料功率份额ff，原用于计算冷却剂和燃料的反馈2-13，然而delta p式子中没有该参数
        self.f_prop = 0.92  # Fuel rod deposit heat
        # 中子速度v，用于计算反应堆时空动力学方程2-3和通量Φ，然而点堆方程2-7中没有
        self.v_neutron = 2.2e5  # cm/s

        # 反应堆入口冷却剂初始温度，Te0。用于计算冷却剂和燃料的反馈2-13，因为delta p式子忽略Te的变化，故设计为常数，Tl，Tf时刻改变
        self.temp_in = 290  # Entrance temperature

        # 宏观吸收截面Σf，用于计算氙Xe和钐Sm贡献的副反应性2-10，数值来自表2.3
        self.Sigma_f = 0.3358  # cm-1

        # Σa，用于计算毒物贡献的Δp，2-12
        self.Sigma_a = 1.523  # cm-1

        # 微观吸收截面σxe，σsm，用于计算氙Xe和钐Sm贡献的副反应性2-8，2-9
        self.sigma_Xe = 2.36e-18  # cm2
        self.sigma_Sm = 40800 * 1e-24  # cm2

        # 吸收截面？λpm,λi,λxe, 用于计算毒物贡献的副反应性，然而用平衡态做初始态的毒物化简后只出现了lambda Xe
        self.lambda_Pm = 3.6e-6  # s-1
        self.lambda_I = 2.9e-5  # s-1
        self.lambda_Xe = 2.1e-5  # s-1

        # 裂变产额γpm,γi,γxe，用于计算毒物贡献的副反应性，三个元素均出现
        self.gamma_Pm = 1.08e-2
        self.gamma_I = 0.0639
        self.gamma_Xe = 0.00228

        # 冷却剂质量流量与冷却剂热容量之积，以下参数均用于计算燃料负反馈，但是delta p中没有出现，而且不是按照f(n0)的函数
        self.M = 102.  # MW/C
        # 燃料热容量
        self.mu_f = 26.3  # MW*s/C
        # 冷却剂热容量
        self.mu_c = 71.8  # MW*s/C
        # 燃料与冷却剂传热系数
        self.omega = 6.6  # MW/C

    # tempearture coefficients with change in reactivity
    # fuel

    # 燃料反应性温度系数，冷却剂反应性温度系数，不是按照f(n0)给出
    def alpha_f(self):
        return -3.24e-5

    # coolant
    def alpha_c(self):
        return -2.13e-4

    def section_absorb(self):
        return self.Sigma_a

    def section_Xe(self):
        return self.sigma_Xe


# calculate changing rate
def Change_rate(dt, status, parameter):
    # define an array to store data
    rate = np.zeros(shape=(16,), dtype=np.float32)
    n = status[0]  # neutron density
    # Delayed neutron precursor nuclear concentration
    Cr = status[1:7]
    rho = status[7]  # Reactivity
    source = status[8]  # starting source
    temp_f = status[9]  # fuel temperature
    temp_c = status[10]  # coolant temperature
    density_I = status[11]
    density_Xe = status[12]
    density_Pm = status[13]
    density_Sm = status[14]
    temp_in = status[15]

    # point reactor dynamics
    # Delayed neutron production rate
    Cr_total = 0
    for i in range(6):
        Cr_total += parameter.lambda_list[i] * Cr[i]
        # Neutron density change rate

    # 点堆方程：公式2-5
    dn = (rho - parameter.beta_sum) / parameter.Lambda * n + Cr_total + source
    # Change rate of precursor nuclear concentration

    # 点堆方程：公式2-6
    dCr = []
    for i in range(6):
        dCr.append(parameter.beta_list[i] / parameter.Lambda * n - parameter.lambda_list[i] * Cr[i])
    # Temperature change rate
    # 温度反应性反馈，公式2-13
    dtemp_f = (parameter.f_prop * parameter.p0 * n - parameter.omega * temp_f + \
               0.5 * parameter.omega * temp_c + 0.5 * parameter.omega * temp_in) / parameter.mu_f
    dtemp_c = ((1. - parameter.f_prop) * parameter.p0 * n + parameter.omega * temp_f - \
               0.5 * (2 * parameter.M + parameter.omega) * temp_c + 0.5 * (2 * parameter.M - \
                                                                           parameter.omega) * temp_in) / parameter.mu_c
    # Toxicant change rate
    # 反应堆毒物，2-8，2-9
    phi = n * parameter.n0 * parameter.v_neutron
    dI = -parameter.lambda_I * density_I + parameter.gamma_I * parameter.Sigma_f * phi
    dXe = (parameter.gamma_Xe * parameter.Sigma_f * phi + parameter.lambda_I * density_I) - \
          (parameter.sigma_Xe * phi + parameter.lambda_Xe) * density_Xe
    dSm = parameter.lambda_Pm * density_Pm - parameter.sigma_Sm * density_Sm * phi
    dPm = parameter.gamma_Pm * parameter.Sigma_f * phi - parameter.lambda_Pm * density_Pm

    # return value
    rate[0] = dn
    rate[1:7] = np.array(dCr, dtype=np.float32)
    rate[7] = 0
    # take outer source as constant
    rate[8] = 0
    rate[9] = dtemp_f
    rate[10] = dtemp_c
    rate[11] = dI
    rate[12] = dXe
    rate[13] = dPm
    rate[14] = dSm
    rate[15] = 0

    return rate


# upgrading status
def Calculate_status(status0, dt, integrator):
    from scipy.integrate import ode
    # solve with runge-kutta
    n = ode(Change_rate).set_integrator(integrator)  # 'dopri5'
    para = para_init()
    n.set_initial_value(status0, 0)
    n.set_f_params(para)
    n.integrate(dt)

    return n.y


class NucBalance(para_init):

    def __init__(self, subcritical=0.0, n_init=1.0):
        super().__init__()
        self.subcritical = subcritical
        self.source0 = -self.subcritical / self.Lambda  # Neutron increase due to reactivity
        self.cal_balance_status(n_init)  # calculate balance status
        # assign balanced status parameters to status_vector
        self.status_vector = self.balance_status.copy()

    def cal_balance_status(self, n_init):
        n = n_init
        # Balanced precursor nuclear concentration
        Cr = [0.] * 6
        for i in range(6):
            # 暂无公式
            Cr[i] = self.beta_list[i] / self.lambda_list[i] / self.Lambda * n
        # Poison concentration in balanced
        phi = self.n0 * n * self.v_neutron
        M = self.M
        omega = self.omega

        # 公式2-10
        density_I = self.gamma_I * self.Sigma_f * phi / self.lambda_I
        density_Xe = (self.gamma_Xe * self.Sigma_f * phi + self.lambda_I * density_I) / (self.sigma_Xe * phi \
                                                                                         + self.lambda_Xe)
        # 公式2-11
        density_Pm = self.gamma_Pm * self.Sigma_f * phi / self.lambda_Pm
        density_Sm = self.gamma_Pm * self.Sigma_f / self.sigma_Sm
        # Fuel and coolant temperature at balance
        # 暂无公式
        temp_c = (self.p0 * n + 2 * M * self.temp_in) / (2 * M)
        temp_f = temp_c + (self.f_prop * self.p0 * n) / omega
        # update return value
        y = []
        y.append(n)
        y.extend(Cr)
        y.extend([self.subcritical, self.source0, temp_f, temp_c])
        y.extend([density_I, density_Xe, density_Pm, density_Sm])
        y.append(self.temp_in)

        self.balance_status = y


def show(state1):
    print('n is: %f' % state1[0])
    print('Cr[0] is: %f' % state1[1])
    print('Cr[1] is: %f' % state1[2])
    print('Cr[2] is: %f' % state1[3])
    print('Cr[3] is: %f' % state1[4])
    print('Cr[4] is: %f' % state1[5])
    print('Cr[5] is: %f' % state1[6])
    print('subcritical is: %f' % state1[7])
    print('source0 is: %f' % state1[8])
    print('temp_f is: %f' % state1[9])
    print('temp_c is: %f' % state1[10])
    print('density_I is: %f' % state1[11])
    print('density_Xe is: %f' % state1[12])
    print('density_Pm is: %f' % state1[13])
    print('density_Sm is: %f' % state1[14])
    print('temp_in is: %f' % state1[15])
    print('-'*20)


if __name__ == '__main__':
    reactor = NucBalance(subcritical=-0.1, n_init=1.0)
    state0 = reactor.status_vector
    show(state0)
    for i in range(100):
        # input()
        state0 = Calculate_status(state0, 1, 'dopri5')
        show(state0)


