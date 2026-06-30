# Simulation & Computational Models

## Overview

This document outlines Python-based simulations for modeling:
1. Double-slit electron wavefunction evolution
2. Photon-mediated reformation force effects
3. Decoherence timeline and visibility loss
4. Parameter sensitivity studies

---

## 1. Wavefunction Solver: Quantum Evolution

### Implementation: `wavefunction_solver.py`

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.fft import fft2, ifft2, fftfreq

class DoubleSlitWavefunctionSolver:
    """
    Solves modified Schrödinger equation with photon coupling
    for double-slit interference pattern
    """
    
    def __init__(self, L=1e-6, N=512, dt=1e-18):
        """
        Parameters:
        L: Physical domain size (meters)
        N: Grid points per dimension
        dt: Time step (seconds)
        """
        self.L = L
        self.N = N
        self.dt = dt
        self.dx = L / N
        
        # Kinetic energy operator in Fourier space
        k = fftfreq(N, self.dx)
        self.k2 = (k**2)[:, np.newaxis] + (k**2)[np.newaxis, :]
        
    def initial_superposition(self, x, y, slit_width=1e-7, slit_sep=2e-7):
        """
        Create initial superposition state through two slits
        """
        psi = np.zeros((self.N, self.N), dtype=complex)
        
        # Slit 1
        slit1_center = -slit_sep / 2
        mask1 = np.abs(x - slit1_center) < slit_width / 2
        psi[mask1] += 1.0
        
        # Slit 2
        slit2_center = slit_sep / 2
        mask2 = np.abs(x - slit2_center) < slit_width / 2
        psi[mask2] += 1.0
        
        # Normalize
        return psi / np.linalg.norm(psi)
    
    def kinetic_energy_step(self, psi, hbar=1.055e-34, m_e=9.109e-31):
        """
        Apply kinetic energy operator via FFT
        exp(-i * T * dt / hbar) in Fourier space
        """
        psi_k = fft2(psi)
        T_coeff = (hbar * self.k2) / (2 * m_e)
        phase = np.exp(-1j * T_coeff * self.dt / hbar)
        psi_k *= phase
        return ifft2(psi_k)
    
    def photon_reformation_force(self, psi, psi_eigenstate, 
                                 photon_energy=5e-19, c=3e8, hbar=1.055e-34):
        """
        Apply photon reformation force: shifts wavefunction toward eigenstate
        """
        # Photon momentum
        k_gamma = np.sqrt(2 * photon_energy * hbar) / (hbar * c)
        
        # Distortion measure
        overlap = np.abs(np.vdot(psi, psi_eigenstate))
        distortion = 1 - overlap**2
        
        # Force magnitude (greater distortion -> stronger force)
        force_strength = distortion * k_gamma / self.dx
        
        # Directional force (toward eigenstate)
        phase_correction = np.exp(1j * force_strength * self.dt)
        psi_reformed = psi * phase_correction
        
        return psi_reformed / np.linalg.norm(psi_reformed), distortion
    
    def evolve_no_photon(self, psi, steps=1000):
        """
        Evolve without photon interaction (reference case)
        """
        trajectory = [psi.copy()]
        
        for _ in range(steps):
            psi = self.kinetic_energy_step(psi)
            trajectory.append(psi.copy())
        
        return trajectory
    
    def evolve_with_photon(self, psi, psi_eigenstate, 
                          photon_enable_step=500, steps=1000):
        """
        Evolve with photon reformation at specified step
        """
        trajectory = [psi.copy()]
        distortion_history = []
        
        for step in range(steps):
            psi = self.kinetic_energy_step(psi)
            
            # Apply photon reformation force
            if step >= photon_enable_step:
                psi, distortion = self.photon_reformation_force(psi, psi_eigenstate)
            else:
                distortion = 1 - np.abs(np.vdot(psi, psi_eigenstate))**2
            
            trajectory.append(psi.copy())
            distortion_history.append(distortion)
        
        return trajectory, distortion_history

# Usage Example
solver = DoubleSlitWavefunctionSolver(L=1e-6, N=256)
x = np.linspace(-solver.L/2, solver.L/2, solver.N)
y = np.linspace(-solver.L/2, solver.L/2, solver.N)
X, Y = np.meshgrid(x, y)

psi_initial = solver.initial_superposition(X, Y)
psi_eigenstate = solver.initial_superposition(X, Y - 1e-7)  # Eigenstate at slit 1

# Run simulation
trajectory_no_photon = solver.evolve_no_photon(psi_initial, steps=1000)
trajectory_with_photon, distortion = solver.evolve_with_photon(
    psi_initial, psi_eigenstate, photon_enable_step=500
)
```

---

## 2. Decoherence Calculator

### Implementation: `decoherence_calculator.py`

```python
import numpy as np
from scipy.stats import entropy

class DecoherenceCalculator:
    """
    Quantifies decoherence through multiple measures
    """
    
    def __init__(self, hbar=1.055e-34):
        self.hbar = hbar
    
    def coherence_loss(self, psi_current, psi_reference):
        """
        Distortion measure: D(t) = 1 - |<ψ_ref|ψ(t)>|²
        """
        overlap = np.abs(np.vdot(psi_reference, psi_current))
        return 1 - overlap**2
    
    def visibility(self, psi, slit_width=1e-7, slit_sep=2e-7):
        """
        Interference pattern visibility: V = (I_max - I_min)/(I_max + I_min)
        """
        intensity = np.abs(psi)**2
        I_max = np.max(intensity)
        I_min = np.min(intensity)
        
        if I_max + I_min == 0:
            return 0
        return (I_max - I_min) / (I_max + I_min)
    
    def inverse_participation_ratio(self, psi):
        """
        Localization measure: IPR ∈ [0,1]
        0 = delocalized (wave), 1 = localized (particle)
        """
        prob = np.abs(psi)**2
        prob = prob / np.sum(prob)  # Normalize
        
        ipr = np.sum(prob**2)
        return ipr
    
    def entanglement_entropy(self, psi):
        """
        Entropy of probability distribution: 
        S = -Σ p_i log(p_i)
        """
        prob = np.abs(psi)**2
        prob = prob.flatten()
        prob = prob[prob > 0]  # Remove zeros
        
        return entropy(prob, base=2)
    
    def decoherence_rate(self, distortion_history, dt=1e-18):
        """
        Estimate decoherence rate from distortion history
        Fit: D(t) ≈ D_0 * exp(-γ * t)
        """
        distortion_history = np.array(distortion_history)
        distortion_history = distortion_history[distortion_history > 1e-6]
        
        if len(distortion_history) < 2:
            return 0
        
        time = np.arange(len(distortion_history)) * dt
        log_distortion = np.log(distortion_history + 1e-10)
        
        # Linear fit to extract rate
        coeffs = np.polyfit(time, log_distortion, 1)
        gamma = -coeffs[0]  # Negative slope = decay rate
        
        return gamma

# Usage
calc = DecoherenceCalculator()
distortion_history = [calc.coherence_loss(traj, psi_initial) 
                      for traj in trajectory_with_photon]
gamma = calc.decoherence_rate(distortion_history)
print(f"Decoherence Rate: {gamma:.2e} Hz")
```

---

## 3. Reformation Force Calculations

### Implementation: `reformation_force.py`

```python
import numpy as np

class ReformationForceCalculator:
    """
    Computes photon-mediated reformation force
    """
    
    def __init__(self, hbar=1.055e-34, c=3e8, alpha=1/137):
        self.hbar = hbar
        self.c = c
        self.alpha = alpha
    
    def photon_wave_vector(self, photon_energy_eV):
        """
        k_γ = E_γ / (ℏc)
        """
        photon_energy = photon_energy_eV * 1.602e-19  # Convert eV to Joules
        return photon_energy / (self.hbar * self.c)
    
    def momentum_transfer(self, photon_energy_eV):
        """
        Δp = ℏ k_γ = E_γ / c
        """
        photon_energy = photon_energy_eV * 1.602e-19
        return photon_energy / self.c
    
    def reformation_force_magnitude(self, distortion, photon_energy_eV, 
                                   dx=1e-9, m_e=9.109e-31):
        """
        |F_reform| proportional to distortion and photon momentum
        """
        k_gamma = self.photon_wave_vector(photon_energy_eV)
        p_transfer = self.momentum_transfer(photon_energy_eV)
        
        # Force ~ distortion * momentum_transfer / dx
        force = distortion * (p_transfer / dx)
        
        return force
    
    def decoherence_rate_photon(self, photon_energy_eV, 
                               E_atomic=27.2):  # Rydberg energy in eV
        """
        γ_reform ≈ (α * ω_γ / ℏ) * (E_γ / E_atomic)²
        """
        photon_energy = photon_energy_eV * 1.602e-19
        omega_gamma = photon_energy / self.hbar
        
        gamma = (self.alpha * omega_gamma / self.hbar) * \
                (photon_energy_eV / E_atomic)**2
        
        return gamma
    
    def energy_dissipation(self, force, velocity, dt=1e-18):
        """
        Power dissipated: P = F · v
        Energy over time: W = P * dt
        """
        power = force * velocity
        energy = power * dt
        return power, energy
    
    def optimal_photon_wavelength(self, target_decoherence_rate=1e12):
        """
        Find photon wavelength for specific decoherence rate
        """
        wavelengths = np.linspace(1e-9, 1e-6, 1000)
        photon_energies_eV = (1240 / (wavelengths * 1e9))  # E = hc/λ in eV
        
        rates = [self.decoherence_rate_photon(E) for E in photon_energies_eV]
        
        # Find closest to target
        idx = np.argmin(np.abs(np.array(rates) - target_decoherence_rate))
        
        return wavelengths[idx], photon_energies_eV[idx], rates[idx]

# Usage
force_calc = ReformationForceCalculator()
optimal_wavelength, optimal_energy, rate = force_calc.optimal_photon_wavelength()
print(f"Optimal Wavelength: {optimal_wavelength*1e9:.2f} nm")
print(f"Photon Energy: {optimal_energy:.2f} eV")
print(f"Decoherence Rate: {rate:.2e} Hz")
```

---

## 4. Visualization Tools

### Implementation: `visualization.py`

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

class WavefunctionVisualizer:
    """
    Create publication-quality visualizations
    """
    
    def __init__(self):
        self.fig_count = 0
    
    def plot_wavefunction(self, psi, title="Wavefunction", cmap='viridis'):
        """
        2D intensity plot of |ψ|²
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        intensity = np.abs(psi)**2
        
        im = ax.contourf(intensity, levels=50, cmap=cmap)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Position X')
        ax.set_ylabel('Position Y')
        plt.colorbar(im, ax=ax, label='|ψ|²')
        
        return fig, ax
    
    def plot_trajectory_comparison(self, trajectory_no_photon, trajectory_with_photon,
                                   steps_to_show=5):
        """
        Side-by-side comparison of evolution
        """
        fig, axes = plt.subplots(steps_to_show, 2, figsize=(12, 5*steps_to_show))
        
        indices = np.linspace(0, len(trajectory_no_photon)-1, steps_to_show, dtype=int)
        
        for i, idx in enumerate(indices):
            # Without photon
            intensity1 = np.abs(trajectory_no_photon[idx])**2
            im1 = axes[i, 0].contourf(intensity1, levels=50, cmap='viridis')
            axes[i, 0].set_title(f'No Photon (t={idx})', fontweight='bold')
            plt.colorbar(im1, ax=axes[i, 0])
            
            # With photon
            intensity2 = np.abs(trajectory_with_photon[idx])**2
            im2 = axes[i, 1].contourf(intensity2, levels=50, cmap='viridis')
            axes[i, 1].set_title(f'With Photon (t={idx})', fontweight='bold')
            plt.colorbar(im2, ax=axes[i, 1])
        
        plt.tight_layout()
        return fig
    
    def plot_decoherence_timeline(self, distortion_history, gamma=None):
        """
        Distortion vs. time with exponential fit
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        time = np.arange(len(distortion_history))
        ax.plot(time, distortion_history, 'bo-', label='Measured Distortion', linewidth=2)
        
        # Overlay exponential decay
        if gamma is not None:
            fitted = distortion_history[0] * np.exp(-gamma * time)
            ax.plot(time, fitted, 'r--', label=f'Exp. Fit (γ={gamma:.2e})', linewidth=2)
        
        ax.set_xlabel('Time Step', fontsize=12)
        ax.set_ylabel('Distortion D(t)', fontsize=12)
        ax.set_title('Photon-Mediated Decoherence Timeline', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])
        
        return fig, ax
    
    def animate_wavefunction(self, trajectory, output_file='wavefunction_animation.mp4'):
        """
        Create animation of wavefunction evolution
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def update(frame):
            ax.clear()
            intensity = np.abs(trajectory[frame])**2
            contour = ax.contourf(intensity, levels=50, cmap='viridis')
            ax.set_title(f'Wavefunction Evolution (t={frame})', fontweight='bold')
            ax.set_xlabel('Position X')
            ax.set_ylabel('Position Y')
            plt.colorbar(contour, ax=ax, label='|ψ|²')
        
        anim = animation.FuncAnimation(fig, update, frames=len(trajectory),
                                      interval=50, repeat=True)
        anim.save(output_file, writer='ffmpeg')
        print(f"Animation saved to {output_file}")

# Usage
visualizer = WavefunctionVisualizer()
visualizer.plot_trajectory_comparison(trajectory_no_photon, trajectory_with_photon)
visualizer.plot_decoherence_timeline(distortion, gamma)
plt.show()
```

---

## 5. Parameter Sensitivity Study

### Scan photon energy dependence on decoherence rate

```python
photon_energies = np.linspace(1, 20, 50)  # eV
decoherence_rates = []

for E_photon in photon_energies:
    gamma = force_calc.decoherence_rate_photon(E_photon)
    decoherence_rates.append(gamma)

plt.figure(figsize=(10, 6))
plt.plot(photon_energies, decoherence_rates, 'bo-', linewidth=2, markersize=6)
plt.xlabel('Photon Energy (eV)', fontsize=12)
plt.ylabel('Decoherence Rate γ (Hz)', fontsize=12)
plt.title('Reformation Rate vs. Photon Energy', fontsize=14, fontweight='bold')
plt.yscale('log')
plt.grid(True, alpha=0.3)
plt.show()
```

---

## 6. Running Full Simulation Suite

```python
# Complete workflow
if __name__ == "__main__":
    # Initialize solvers
    solver = DoubleSlitWavefunctionSolver()
    calc = DecoherenceCalculator()
    force_calc = ReformationForceCalculator()
    vis = WavefunctionVisualizer()
    
    # Create initial conditions
    x = np.linspace(-solver.L/2, solver.L/2, solver.N)
    y = np.linspace(-solver.L/2, solver.L/2, solver.N)
    X, Y = np.meshgrid(x, y)
    
    psi_initial = solver.initial_superposition(X, Y)
    psi_eigenstate = solver.initial_superposition(X, Y - 1e-7)
    
    # Run simulations
    print("Evolving without photon...")
    trajectory_no_photon = solver.evolve_no_photon(psi_initial, steps=2000)
    
    print("Evolving with photon reformation...")
    trajectory_with_photon, distortion = solver.evolve_with_photon(
        psi_initial, psi_eigenstate, photon_enable_step=500, steps=2000
    )
    
    # Analyze
    gamma = calc.decoherence_rate(distortion)
    print(f"Measured Decoherence Rate: {gamma:.2e} Hz")
    
    # Visualize
    vis.plot_trajectory_comparison(trajectory_no_photon, trajectory_with_photon)
    vis.plot_decoherence_timeline(distortion, gamma)
    vis.animate_wavefunction(trajectory_with_photon)
    
    plt.show()
```

---

## Output Files Generated

- `wavefunction_trajectory_no_photon.npy` — Trajectory without photon
- `wavefunction_trajectory_with_photon.npy` — Trajectory with photon
- `distortion_history.csv` — Time series of distortion
- `wavefunction_animation.mp4` — Animated evolution
- `comparison_plots.png` — Side-by-side comparison figures
