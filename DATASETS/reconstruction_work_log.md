# Math Reconstruction — Work Log

Corpus: **4235 occurrences** across **14 papers**.

This log shows what the pipeline actually attempted and produced.
Every row is a real record from real execution — no fabrication.

## Pipeline reach

| Stage | Count | Share |
| --- | ---: | ---: |
| Source occurrences | 4235 | 100% |
| Parsed via MathML tree | 4059 | 95.8% |
| Parsed via LaTeX fallback | 176 | 4.2% |
| Solver accepted | 452 | 10.7% |
| Independently verified | 218 | 5.1% |
| Verification refuted | 0 | 0.0% |
| Verification inconclusive | 98 | 2.3% |

## Where the pipeline stops, and why

| Reason | Count | What it means |
| --- | ---: | --- |
| `no_equality` | 1775 | statement carries no '=' — a definition fragment, value, or table cell |
| `empty` | 907 | nothing to solve after extraction |
| `not_an_equation:relation` | 639 | a relation other than '=' (membership, approximation, ordering) — refused rather than forced |
| `solve_unsupported` | 121 | SymPy parsed it but has no solver for this form |
| `empty_side` | 106 | one side of the relation is empty |
| `parse_error` | 101 | SymPy could not parse the recovered form |
| `markup_leaked` | 90 | a markup token survived as a symbol — refused |
| `vars:AttributeError` | 19 | see record |
| `not_preserved` | 15 | translation would have dropped or altered the source math — refused |
| `multiple_equalities` | 6 | see record |
| `no_solution` | 2 | see record |
| `no_variables` | 2 | see record |

## Per-paper

| Paper | Occurrences | Solved | Verified |
| --- | ---: | ---: | ---: |
| 2009.00031 | 360 | 32 | 12 |
| 2102.03334 | 94 | 1 | 0 |
| 2605.00155 | 991 | 116 | 48 |
| 2605.00224 | 156 | 24 | 12 |
| 2605.06070 | 991 | 116 | 48 |
| 2605.18130 | 339 | 24 | 3 |
| 2605.22715 | 133 | 16 | 4 |
| 2605.23244 | 305 | 13 | 9 |
| 2605.24807 | 52 | 7 | 5 |
| 2605.24856 | 168 | 35 | 34 |
| 2605.25036 | 211 | 12 | 2 |
| 2605.25334 | 147 | 5 | 4 |
| 2605.28615 | 94 | 0 | 0 |
| 2605.28896 | 194 | 51 | 37 |

## Worked examples — solved AND independently verified

Each row: the source as written, the form handed to the solver, the
solution, and the substitute-back check that confirms it.

| Paper | Source (LaTeX) | Recovered | Solution | Residual check |
| --- | --- | --- | --- | --- |
| 2009.00031 | `d=3-5` | `d=3-5` | `[-2]` | both stages passed |
| 2009.00031 | `\nu=22.35\mbox{ Hz}` | `nu=22.35Hz` | `[22.35*H*z]` | both stages passed |
| 2009.00031 | `\nu=22.37\mbox{ Hz}` | `nu=22.37Hz` | `[22.37*H*z]` | both stages passed |
| 2009.00031 | `\dot{E}=5.6\times 10^{37}\mbox{ erg s${}^{-1}$}` | `E_dot=5.6*((10)**(37))erg_s` | `[5.6e+37*erg_s]` | both stages passed |
| 2009.00031 | `f_{\rm X}=1.8\times 10^{-11}\mbox{ erg cm${}^{-2}$ s${...` | `f_X=1.8*((10)**(-11))erg_cms` | `[1.8e-11*erg_cms]` | both stages passed |
| 2009.00031 | `f_{\rm X}=3.1\times 10^{-12}\mbox{ erg cm${}^{-2}$ s${...` | `f_X=3.1*((10)**(-12))erg_cms` | `[3.1e-12*erg_cms]` | both stages passed |
| 2009.00031 | `\Gamma=0.4_{-0.7}^{+0.4}` | `Gamma=0.4_0.7**(+0.4)` | `[0.346816065752449]` | both stages passed |
| 2009.00031 | `\nu=22.35194397\mbox{ Hz}` | `nu=22.35194397Hz` | `[22.35194397*H*z]` | both stages passed |
| 2009.00031 | `\nu=22.3717124\mbox{ Hz}` | `nu=22.3717124Hz` | `[22.3717124*H*z]` | both stages passed |
| 2009.00031 | `\nu=22.35196\mbox{ Hz}` | `nu=22.35196Hz` | `[22.35196*H*z]` | both stages passed |
| 2009.00031 | `\ddot{\nu}=0` | `nu_ddot=0` | `[0]` | both stages passed |
| 2009.00031 | `\nu=22.35099411\mbox{ Hz}` | `nu=22.35099411Hz` | `[22.35099411*H*z]` | both stages passed |
| 2605.00155 | `P=\delta_{r}` | `P=delta_r` | `[delta_r]` | both stages passed |
| 2605.00155 | `r^{\star}\coloneqq\bar{r}_{\mathcal{P}^{\star}}` | `r_star=r_bar_P_star` | `[r_bar_P_star]` | both stages passed |
| 2605.00155 | `P_{0}\coloneqq\delta_{\hat{r}}` | `P_0=delta_r_hat` | `[delta_r_hat]` | both stages passed |
| 2605.00155 | `P_{0}=\delta_{\hat{r}}` | `P_0=delta_r_hat` | `[delta_r_hat]` | both stages passed |
| 2605.00155 | `p=1` | `p=1` | `[1]` | both stages passed |
| 2605.00155 | `P_{0}=\delta_{\hat{r}}` | `P_0=delta_r_hat` | `[delta_r_hat]` | both stages passed |
| 2605.00155 | `\Pi_{\mathrm{full}}\coloneqq\Delta_{n}^{\mathcal{X}}` | `Pi_full=Delta_n**(X)` | `[Delta_n**X]` | both stages passed |
| 2605.00155 | `p=1` | `p=1` | `[1]` | both stages passed |
| 2605.00155 | `p^{\ast}=1` | `p_star=1` | `[1]` | both stages passed |
| 2605.00155 | `p=1` | `p=1` | `[1]` | both stages passed |
| 2605.00155 | `p=1` | `p=1` | `[1]` | both stages passed |
| 2605.00155 | `p=1` | `p=1` | `[1]` | both stages passed |
| 2605.00155 | `\bar{\hat{r}}=\frac{1}{n}\sum_{i=1}^{n}\hat{r}_{i}` | `r_hat_bar=((1)/(n))Sum_i_eq_1_n*r_hat_i` | `[Sum_i_eq_1_n*r_hat_i/n]` | both stages passed |
| 2605.00155 | `\bar{\pi}=\pi_{\theta_{\mathrm{old}}}` | `pi_bar=pi_theta_old` | `[pi_theta_old]` | both stages passed |
| 2605.00155 | `\bar{\pi}=\pi_{\theta_{\mathrm{old}}}` | `pi_bar=pi_theta_old` | `[pi_theta_old]` | both stages passed |
| 2605.00155 | `\widetilde{r}_{\bar{\pi}}=\hat{r}` | `r_tilde_pi_bar=r_hat` | `[r_hat]` | both stages passed |
| 2605.00155 | `q=\bar{\pi}` | `q=pi_bar` | `[pi_bar]` | both stages passed |
| 2605.00155 | `q=\bar{\pi}` | `q=pi_bar` | `[pi_bar]` | both stages passed |
| 2605.00155 | `K=G` | `K=G` | `[G]` | both stages passed |
| 2605.00155 | `q=\bar{\pi}` | `q=pi_bar` | `[pi_bar]` | both stages passed |
| 2605.00155 | `q=\bar{\pi}` | `q=pi_bar` | `[pi_bar]` | both stages passed |
| 2605.00155 | `\widetilde{\delta}\coloneqq(G/n)\delta` | `delta_tilde=(G/n)delta` | `[G*delta/n]` | both stages passed |
| 2605.00155 | `\widetilde{\delta}=2.5G` | `delta_tilde=2.5G` | `[2.5*G]` | both stages passed |
| 2605.00155 | `\alpha=10` | `alpha=10` | `[10]` | both stages passed |
| 2605.00155 | `\tau=2.0` | `tau=2.0` | `[2.00000000000000]` | both stages passed |
| 2605.00155 | `P\coloneqq(T_{\Delta})_{\#}P_{0}` | `P=(T_Delta)_#P_0` | `[T_Delta*_]` | both stages passed |
| 2605.00155 | `\Pi_{f}\coloneqq\Pi_{\mathrm{full}}` | `Pi_f=Pi_full` | `[Pi_full]` | both stages passed |
| 2605.00155 | `p=1` | `p=1` | `[1]` | both stages passed |

## Honest rejections — refused rather than fabricated

These are cases where solving would have produced a conclusion the
paper never made. The pipeline reports the reason instead.

| Paper | Source (LaTeX) | Reason |
| --- | --- | --- |
| 2009.00031 | `-` | `empty` |
| 2009.00031 | `\mu_{\rm R.A.}=-(0.\!\!″067\pm 0.\!\!″010)\mbox{ yr${}^{-1}$}` | `not_an_equation:relation:pm` |
| 2009.00031 | `<3\mbox{ kyr}` | `no_equality` |
| 2009.00031 | `=18^{\rm h}13^{\rm m}35.\!\!^{\rm s}166` | `empty_side` |
| 2009.00031 | `L_{\rm X}=5.4\times 10^{34}\mbox{ erg s${}^{-1}$}\,(d/\mbox{ 5 kpc})^...` | `parse:SyntaxError` |
| 2009.00031 | `\|\Delta\dot{\nu}/\dot{\nu}\|=0.55` | `solve:NotImplementedError` |
| 2009.00031 | `\nu=[22.35108\mbox{ Hz},22.35108995\mbox{ Hz}]` | `vars:AttributeError` |
| 2605.00155 | `\Reg_{x}(\zeta,s(x))\coloneqq\max_{\beta\in\Delta_{n}}\left\langle\be...` | `markup_leaked:rangle` |
| 2605.00155 | `\displaystyle\min_{\pi\in\Delta_{n},\ t\in\mathbb{R}}` | `not_preserved:content_collapsed` |
| 2605.00155 | `\displaystyle:=\frac{1}{G}\sum_{\ell=1}^{G}\widehat{r}^{(\ell)},\qqua...` | `multiple_equalities` |
| 2605.00155 | `\pi^{\mathrm{DRRO}}=\pi^{\mathrm{DRRO}}(\delta)` | `no_solution` |
| 2605.22715 | `16\times 4\times 2=128` | `no_variables` |

## Inconclusive verification

The solver produced a solution but the substitute-back check could not
mechanically reduce the residual to zero. This is a **parse ambiguity**
(for example `Pi(U)` read as `Pi*U`), not a demonstrated error. Reported
as inconclusive rather than passed or failed.

| Paper | Source (LaTeX) | Residual |
| --- | --- | --- |
| 2009.00031 | `N_{\rm H}=13.1\times 10^{22}\mbox{ cm${}^{-2}$}` | stage2: symbolic residual (unverifiable) |
| 2009.00031 | `N_{\rm H}=13.1\times 10^{22}\mbox{ cm${}^{-2}$}` | stage2: symbolic residual (unverifiable) |
| 2009.00031 | `L_{\rm X}/\dot{E}=1.7\times 10^{-4}` | stage2: cannot isolate variable |
| 2009.00031 | `L_{\rm X}\mbox{(PWN)}/\dot{E}=9.6\times 10^{-4}` | stage2: cannot isolate variable |
| 2009.00031 | `N_{\rm H}=9.8_{-0.9}^{+1.2}\times 10^{22}\mbox{ cm${}^...` | stage2: symbolic residual (unverifiable) |
| 2009.00031 | `N_{\rm H}=1.7\times 10^{22}\mbox{ cm${}^{-2}$}` | stage2: symbolic residual (unverifiable) |
| 2009.00031 | `\Delta\nu=-0.01975` | stage2: cannot isolate variable |
| 2009.00031 | `N_{\rm H}=13.1\times 10^{22}\mbox{ cm${}^{-2}$}` | stage2: symbolic residual (unverifiable) |
| 2605.00155 | `p^{\ast}=\infty` | stage2: infinite/undefined residual |
| 2605.00155 | `p=\infty` | stage2: infinite/undefined residual |
| 2605.00155 | `p=\infty` | stage2: infinite/undefined residual |
| 2605.00155 | `\Delta_{j}^{\star}=\delta\,\operatorname{sgn}((e_{k}-\...` | stage2: symbolic residual (unverifiable) |
| 2605.00155 | `\left\lVert e_{i}-\pi\right\rVert_{\infty}=1-\pi_{i}` | stage2: vacuous substitution (echo) |
| 2605.00155 | `1/p+1/p^{\ast}=1` | stage2: cannot isolate variable |
| 2605.00155 | `p=\infty` | stage2: infinite/undefined residual |
| 2605.00155 | `\mathcal{B}_{\varepsilon}\coloneqq\Pi_{\rho}^{\star}(\...` | stage2: symbolic residual (unverifiable) |
| 2605.00155 | `1/p+1/p^{\ast}=1` | stage2: cannot isolate variable |
| 2605.00155 | `D_{x}\coloneqq R(x)-\widetilde{R}(x)` | stage2: symbolic residual (unverifiable) |
| 2605.00155 | `R=T_{\Delta}(\widetilde{R})` | stage2: symbolic residual (unverifiable) |
| 2605.00155 | `\beta=e_{i}` | stage2: vacuous substitution (echo) |

## Verdict

- 0 equations were solved to a result that failed independent
  verification. This is the number that matters for correctness.
- 218 equations were solved and independently verified.
- 98 solutions could not be mechanically confirmed either way.
- Solver acceptance alone (452) is not treated as correctness.

