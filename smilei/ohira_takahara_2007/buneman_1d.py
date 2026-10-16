# 仮ぎめ込み。2007年図1の正本ではない。

import math
import os
import sys

_pic_root = os.environ.get("PIC_ROOT")
if _pic_root:
    _here = os.path.join(_pic_root, "smilei", "ohira_takahara_2007")
else:
    try:
        _here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        _here = os.getcwd()
if _here not in sys.path:
    sys.path.insert(0, _here)

from params import *

timestep = dt_1d
if smoked():
    simulation_time = 10.0 * timestep
elif os.environ.get("OHIRA_FIELDS") == "1":
    _span = os.environ.get("OHIRA_FIELDS_TIME")
    if _span:
        simulation_time = float(_span)
    else:
        # 頁の終了は 1000。50間隔の出力ステップが n_time より先に出ないよう、そのステップの次まで進める。params の simulation_time は 1000 のまま。
        _every = max(1, int(round(50.0 / timestep)))
        _k = math.ceil(1000.0 / (_every * timestep) - 1e-12)
        _step = _every * _k
        simulation_time = (_step + 1) * timestep

_nsteps = int(simulation_time / timestep)

_use_gpu = os.environ.get("SMILEI_GPU") == "1"
_n_patches = [1] if _use_gpu else [4]

Main(
    geometry="1Dcartesian",
    interpolation_order=2,
    cell_length=[dx],
    number_of_cells=[n_cells],
    number_of_patches=_n_patches,
    timestep=timestep,
    simulation_time=simulation_time,
    EM_boundary_conditions=[["periodic"]],
    random_seed=random_seed,
    print_every=max(1, _nsteps // 10),
    gpu_computing=_use_gpu,
)


# 背景磁場は格子の初期値。一様成分は Faraday が保持する。B_m は t=0、B は t=0.5 dt。
ExternalField(
    field="Bz",
    profile=constant(B0),
)
ExternalField(
    field="Bz_m",
    profile=constant(B0),
)

Species(
    name="electrons",
    position_initialization="regular",
    momentum_initialization="maxwell-juettner",
    particles_per_cell=ppc_electrons_1d,
    mass=1.0,
    charge=-1.0,
    number_density=n_electrons,
    mean_velocity=v_electron,
    temperature=[temperature],
    boundary_conditions=[["periodic", "periodic"]],
)

Species(
    name="upstream_protons",
    position_initialization="regular",
    momentum_initialization="maxwell-juettner",
    particles_per_cell=ppc_protons_1d,
    mass=mass_ratio,
    charge=1.0,
    number_density=n_upstream_protons,
    mean_velocity=v_upstream_proton,
    temperature=[temperature],
    boundary_conditions=[["periodic", "periodic"]],
)

Species(
    name="reflected_protons",
    position_initialization="regular",
    momentum_initialization="maxwell-juettner",
    particles_per_cell=ppc_protons_1d,
    mass=mass_ratio,
    charge=1.0,
    number_density=n_reflected_protons,
    mean_velocity=v_reflected_proton,
    temperature=[temperature],
    boundary_conditions=[["periodic", "periodic"]],
)

# 反射陽子の電流 n_r*V_d を消す。論文は Poisson でこの一様電流が電場を作らない。
# OHIRA_ANTENNA=0 のときは足さない。
if os.environ.get("OHIRA_ANTENNA") != "0":
    Antenna(
        field="Jx",
        space_profile=-n_reflected_protons * v_reflected_proton[0],
        time_profile=1.0,
    )

DiagScalar(every=1 if smoked() else max(1, int(round(1.0 / timestep))), precision=10)

if os.environ.get("OHIRA_FIELDS") == "1":
    _every_snapshot = max(1, int(round(50.0 / timestep)))
    DiagFields(
        every=_every_snapshot,
        fields=["Ex", "Ey", "Ez", "Bx", "By", "Bz", "Bx_m", "By_m", "Bz_m"],
    )
    for _species in ("electrons", "upstream_protons", "reflected_protons"):
        DiagTrackParticles(
            species=_species,
            every=_every_snapshot,
            flush_every=_every_snapshot,
            attributes=["x", "y", "z", "px", "py", "pz"],
        )
