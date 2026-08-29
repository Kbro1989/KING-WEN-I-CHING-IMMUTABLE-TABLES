"""
King Wen x QuantumLab -- Wave Packet Pre-Warming Engine
Deterministic 1D->2D->3D split-step Fourier pre-warming.
Grids: 1D=64, 2D=8x8, 3D=9x9x9=729 vertices.
"""
import json, time
from pathlib import Path
import numpy as np
from scipy.fft import fft, ifft, fft2, ifft2, fftn, ifftn

KINGWEN_ROOT = Path(r'c:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')
DATASETS_DIR = KINGWEN_ROOT / 'DATASETS'
HBAR, MASS, DT, WARMUP_STEPS = 1.0, 1.0, 0.02, 3
N1 = 64
N2X, N2Y = 8, 8
N3X, N3Y, N3Z = 9, 9, 9
PI = 3.14159265358979323846
COPRIMES = [97, 89, 83, 79, 73]

def _kw_pot_1d(x):
    V = np.zeros_like(x, dtype=float)
    for p in COPRIMES:
        V += np.sin(p * x / np.pi) / p
    return V

def _kw_pot_2d(X, Y):
    V = np.zeros_like(X, dtype=float)
    for p in COPRIMES:
        V += np.sin(p * X / np.pi) * np.cos(p * Y / np.pi) / (p * p)
    return V

def _kw_pot_3d(X, Y, Z):
    V = np.zeros_like(X, dtype=float)
    for p in COPRIMES:
        V += np.sin(p * X / np.pi) * np.cos(p * Y / np.pi) * np.sin(p * Z / np.pi) / (p ** 3)
    return V

def prewarm_1d():
    t0 = time.perf_counter()
    dx = (2*PI) / N1
    x  = np.linspace(-PI, PI, N1, endpoint=False)
    k  = 2 * np.pi * np.fft.fftfreq(N1, dx)
    V   = _kw_pot_1d(x)
    T_k = HBAR**2 * k**2 / (2.0 * MASS)
    U_V = np.exp(-1j * V * DT / (2.0 * HBAR))
    U_T = np.exp(-1j * T_k * DT / HBAR)
    psi = np.exp(-(x**2) / (4.0*0.5**2)) * np.exp(1j * 1.0 * x)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)
    for _ in range(WARMUP_STEPS):
        psi = ifft(fft(psi * U_V) * U_T) * U_V
    elapsed = time.perf_counter() - t0
    print(f'  [1D] N={N1} warmup={WARMUP_STEPS} elapsed={elapsed:.4f}s')
    return dict(dim=1,N=N1,grid_x=x,k=k,V=V,T_k=T_k,U_V=U_V,U_T=U_T,psi_warm=psi,elapsed_s=elapsed)

def prewarm_2d():
    t0 = time.perf_counter()
    dx = (2*PI) / N2X; dy = (2*PI) / N2Y
    x  = np.linspace(-PI, PI, N2X, endpoint=False)
    y  = np.linspace(-PI, PI, N2Y, endpoint=False)
    X, Y = np.meshgrid(x, y, indexing='ij')
    k_x  = 2*np.pi*np.fft.fftfreq(N2X, dx); k_y  = 2*np.pi*np.fft.fftfreq(N2Y, dy)
    K_x, K_y = np.meshgrid(k_x, k_y, indexing='ij')
    V   = _kw_pot_2d(X, Y)
    T_k = HBAR**2 * (K_x**2 + K_y**2) / (2.0 * MASS)
    U_V = np.exp(-1j * V * DT / (2.0 * HBAR))
    U_T = np.exp(-1j * T_k * DT / HBAR)
    psi = np.exp(-(X**2)/(4*0.5**2)) * np.exp(-(Y**2)/(4*0.5**2)) * np.exp(1j*(X+Y))
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx * dy)
    for _ in range(WARMUP_STEPS):
        psi = ifft2(fft2(psi * U_V) * U_T) * U_V
    elapsed = time.perf_counter() - t0
    print(f'  [2D] N={N2X}x{N2Y} warmup={WARMUP_STEPS} elapsed={elapsed:.4f}s')
    return dict(dim=2,N_x=N2X,N_y=N2Y,V=V,T_k=T_k,U_V=U_V,U_T=U_T,psi_warm=psi,elapsed_s=elapsed)

def prewarm_3d():
    t0 = time.perf_counter()
    dx = (2*PI)/N3X; dy = (2*PI)/N3Y; dz = (2*PI)/N3Z
    x  = np.linspace(-PI, PI, N3X, endpoint=False)
    y  = np.linspace(-PI, PI, N3Y, endpoint=False)
    z  = np.linspace(-PI, PI, N3Z, endpoint=False)
    X, Y, Zg = np.meshgrid(x, y, z, indexing='ij')
    k_x = 2*np.pi*np.fft.fftfreq(N3X, dx)
    k_y = 2*np.pi*np.fft.fftfreq(N3Y, dy)
    k_z = 2*np.pi*np.fft.fftfreq(N3Z, dz)
    K_x, K_y, K_z = np.meshgrid(k_x, k_y, k_z, indexing='ij')
    V   = _kw_pot_3d(X, Y, Zg)
    T_k = HBAR**2 * (K_x**2 + K_y**2 + K_z**2) / (2.0 * MASS)
    U_V = np.exp(-1j * V * DT / (2.0 * HBAR))
    U_T = np.exp(-1j * T_k * DT / HBAR)
    psi = (np.exp(-(X**2)/(4*0.5**2)) * np.exp(-(Y**2)/(4*0.5**2)) *
           np.exp(-(Zg**2)/(4*0.5**2)) * np.exp(1j*(X+Y+Zg)))
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx * dy * dz)
    for _ in range(WARMUP_STEPS):
        psi = ifftn(fftn(psi * U_V, workers=-1) * U_T, workers=-1) * U_V
    vc = N3X * N3Y * N3Z
    elapsed = time.perf_counter() - t0
    print(f'  [3D] N={N3X}x{N3Y}x{N3Z}={vc} warmup={WARMUP_STEPS} elapsed={elapsed:.4f}s')
    return dict(dim=3,N_x=N3X,N_y=N3Y,N_z=N3Z,vertex_count=vc,
                V=V,T_k=T_k,U_V=U_V,U_T=U_T,psi_warm=psi,
                prob_density_flat=np.abs(psi).flatten(),elapsed_s=elapsed)

def _split(arr, prefix):
    return {f'{prefix}_real': arr.real.astype(np.float64), f'{prefix}_imag': arr.imag.astype(np.float64)}

def save_cache(r1, r2, r3):
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    path = DATASETS_DIR / 'quantum_prewarm_cache.npz'
    d = {}
    for r, tag in [(r1,'1d'),(r2,'2d'),(r3,'3d')]:
        for key in ('U_V','U_T','psi_warm'):
            d.update(_split(r[key], f'{tag}_{key}'))
    d['3d_prob_density_flat'] = r3['prob_density_flat'].astype(np.float64)
    d['1d_grid_x'] = r1['grid_x'].astype(np.float64)
    np.savez_compressed(path, **d)
    return path

def save_manifest(r1, r2, r3, cp):
    m = {
        'prewarm_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'warmup_steps': WARMUP_STEPS, 'dt': DT, 'hbar': HBAR, 'mass': MASS,
        'coprimes': COPRIMES, 'cache_file': str(cp),
        'stages': {
            '1d': {'N': N1, 'x_range': [-PI, PI], 'basis_states': N1,
                   'U_V_shape': list(r1['U_V'].shape), 'U_T_shape': list(r1['U_T'].shape),
                   'elapsed_s': round(r1['elapsed_s'],6),
                   'description': '64 discrete hexagram basis vectors'},
            '2d': {'N_x': N2X, 'N_y': N2Y, 'binary_phase_states': N2X*N2Y*8,
                   'U_V_shape': list(r2['U_V'].shape), 'U_T_shape': list(r2['U_T'].shape),
                   'elapsed_s': round(r2['elapsed_s'],6),
                   'description': '512 binary phase probability density grid'},
            '3d': {'N_x': N3X, 'N_y': N3Y, 'N_z': N3Z,
                   'vertex_count': r3['vertex_count'],
                   'ternary_phase_states': r3['vertex_count']*8,
                   'U_V_shape': list(r3['U_V'].shape), 'U_T_shape': list(r3['U_T'].shape),
                   'elapsed_s': round(r3['elapsed_s'],6),
                   'description': '729-vertex ternary manifold 9x9x9, 5832 phase states'},
        },
        'verification': {
            '1d_basis_states': N1,
            '2d_cell_count': N2X*N2Y, '2d_binary_states': N2X*N2Y*8,
            '3d_vertex_count': N3X*N3Y*N3Z, '3d_ternary_states': N3X*N3Y*N3Z*8,
        },
    }
    path = DATASETS_DIR / 'quantum_prewarm_manifest.json'
    with open(path,'w',encoding='utf-8') as fh: json.dump(m, fh, indent=2)
    return path

def main():
    print('[PREWARM] King Wen Wave Packet Pre-Warming Engine')
    print(f'  warmup_steps={WARMUP_STEPS}, dt={DT}, hbar={HBAR}, mass={MASS}')
    print(f'  coprimes={COPRIMES}')
    print()
    t_total = time.perf_counter()
    print('[STAGE 1/3] 1D -- 64-hexagram basis space')
    r1 = prewarm_1d()
    print('[STAGE 2/3] 2D -- 512 binary phase probability density')
    r2 = prewarm_2d()
    print('[STAGE 3/3] 3D -- 729-vertex ternary manifold')
    r3 = prewarm_3d()
    total_elapsed = time.perf_counter() - t_total
    assert r1['U_V'].shape == (64,),     'FAIL 1D U_V shape'
    assert r2['U_V'].shape == (8, 8),    'FAIL 2D U_V shape'
    assert r3['U_V'].shape == (9, 9, 9), 'FAIL 3D U_V shape'
    assert r3['vertex_count'] == 729,    'FAIL 3D vertex_count != 729'
    print()
    print('[SAVE] Writing operator cache and manifest...')
    cp = save_cache(r1, r2, r3)
    mp = save_manifest(r1, r2, r3, cp)
    print()
    print(f'[OK] Pre-warm complete in {total_elapsed:.3f}s')
    print(f'     Cache:    {cp}')
    print(f'     Manifest: {mp}')
    print(f'  1D U_V:{r1["U_V"].shape}  U_T:{r1["U_T"].shape}')
    print(f'  2D U_V:{r2["U_V"].shape}  U_T:{r2["U_T"].shape}')
    print(f'  3D U_V:{r3["U_V"].shape}  U_T:{r3["U_T"].shape}')
    print(f'  3D vertex_count  : {r3["vertex_count"]}  (must be 729)')
    print(f'  3D ternary_states: {r3["vertex_count"]*8}  (must be 5832)')
    print(f'  2D binary_states : {N2X*N2Y*8}  (must be 512)')

if __name__ == '__main__':
    main()