# Smilei GPU で背景磁場が消える件

Ohira & Takahara (2007) の 1 次元 Buneman を Smilei の GPU 版で回すと、`PrescribedField` で入れた一様な `Bz_m = 0.03` が時刻 0 だけ残り、時刻 50 には 0 になる。CPU では 0.03 のままである。報告は [SmileiPIC/Smilei#912](https://github.com/SmileiPIC/Smilei/issues/912)。

## 起きたこと

`PrescribedField` は、粒子を押すが Maxwell には参加しない場である。各ステップで格子から外し、粒子推進の前にホストの配列へ足す。

GPU では磁場のセンタリングがデバイス上で `Bz_m = (Bz + Bz_m) / 2` をする。Faraday が更新する `Bz` にはこの背景磁場が入っていないのでほぼ 0 である。デバイス上の `Bz_m` は毎ステップ半分になり、数十ステップで消える。ホストへの足し戻しはデバイスにコピーされない。診断はデバイスの値を書くので、保存された `Bz_m` は 0 になる。

短い箱（`buneman_1d_fields_gpu`）でも長い箱（`buneman_1d_ldebye2_t200`）でも同じである。電子の `py` は CPU では時刻 50 に約 `+5.3e-3` まで動くが、GPU では約 0 のままである。平均 `Ex` の符号の進みも CPU と分かれる。

WarpX の GPU は `warpx.B_external_grid` を初期化のときだけデバイス上の格子磁場へ足し、その後は同じ配列を Faraday で更新する。一様成分は回転がゼロなので残る。長い箱の HIP ランでも `B` は時刻 200 まで `-0.030` であった。

## 方法

Smilei の `ExternalField` は初期だけの格子磁場である。`Bz` と `Bz_m` の両方に `constant(0.03)` を入れる。初期化のデバイスへのコピーは、この適用の後にある。以降はホストへ書き戻さない。一様な `Bz` は Faraday で保持され、センタリングの平均も `0.03` のままである。

`smilei/ohira_takahara_2007/buneman_1d.py` はこの形にした。`PrescribedField` は外した。

## テスト

GPU、アンテナなし、時刻 200。出力は `runs/ohira_takahara_2007/buneman_1d_gpu_bgrid_t200/`。終了コード 0、壁時計 833 秒。

`Bz` と `Bz_m` の平均は時刻 0, 50, 100, 150, 200 とも `0.030`。電子の `py` は時刻 50 で `+5.27e-3`。平均 `Ex` は時刻 50 で `-1.60e-3`、時刻 200 で `+6.54e-3`。アンテナなしの CPU（`buneman_1d_cpu_t200`）および WarpX の長い箱と同じ並びである。成長率の最大はモード 20（`k|V_d|/ω_pe = 1.25`、0.027）で、電力の最大がモード 21 なのは初期振幅のためである。
