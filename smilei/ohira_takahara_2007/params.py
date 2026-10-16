# 仮ぎめ込み。2007年図1の正本ではない。
# 2π v_d / ω_pe は箱の長さに使わない。
# 論文は Poisson で電磁波を解かない。Smilei は Maxwell である。

import math
import os

# Smilei 単位: c = 1、ω_pe = 1、基準密度 n_e = 1、m_e = 1、e = 1。

mass_ratio = 1836

# 温度は各種 7 eV。Smilei の temperature は m_e c^2 単位。陽子も同じエネルギー温度。
temperature = 7.0 / 511000.0

n_electrons = 1.0
n_upstream_protons = 0.8
n_reflected_protons = 0.2

# 電流を消す電子ドリフトは足さない。上流電子と上流陽子の平均速度は 0。
v_electron = [0.0, 0.0, 0.0]
v_upstream_proton = [0.0, 0.0, 0.0]
v_reflected_proton = [-0.04, 0.0, 0.0]

# 背景磁場は z 方向。ω_ce / ω_pe = 0.03。格子の初期値 Bz と Bz_m。
B0 = 0.03

# セル幅のデバイ長は sqrt(2*7/511000)。論文の「デバイ長の3倍」に合わせる。
# temperature は kT のまま。分散は kT/m_e。
debye_length = math.sqrt(2.0 * 7.0 / 511000.0)
dx = 3.0 * debye_length
n_cells = 256
# この長さは、論文が 16 λ_Bun と呼ぶ箱である。
Lx = dx * n_cells
Ly = Lx

ppc_electrons_1d = 10240
ppc_electrons_2d = 80
ppc_protons_1d = 200
ppc_protons_2d = 50

# 2次元の regular は ppc が平方数でない。regular_number の積をその ppc にする。個数は変えない。
regular_number_electrons_2d = [8, 10]
regular_number_protons_2d = [5, 10]

dt_1d = 0.01
# 2次元は Maxwell の CFL を見る。0.01 が不安定なら dt_2d = 0.9 * dx / sqrt(2)。その値は頁の 0.01 ではない。1次元の dt は 0.01 のまま。
_cfl_dt_2d = dx / math.sqrt(2.0)
if 0.01 >= _cfl_dt_2d:
    dt_2d = 0.9 * dx / math.sqrt(2.0)
else:
    dt_2d = 0.01

# 頁に無い。Smilei の初期速度に要るので 0。
random_seed = 0

# 本計算の simulation_time。OHIRA_SMOKE=1 のときは各入力が 10*dt にする。
simulation_time = 1000


def smoked():
    return os.environ.get("OHIRA_SMOKE") == "1"
