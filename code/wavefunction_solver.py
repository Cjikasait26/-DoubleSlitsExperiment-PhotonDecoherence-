"""
wavefunction_solver.py

Solves modified Schrödinger equation with photon coupling
for double-slit interference pattern evolution
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.fft import fft2, ifft2, fftfreq


class DoubleSlitWavefunctionSolver:
    """
    Numerically solves the time-dependent Schrödinger equation with photon interaction.
    Tracks wavefunction evolution in double-slit setup.
    """
    
    def __init__(self, L=1e-6, N=512, dt=1e-18):
        """
        Initialize solver with spatial and temporal parameters.
        
        Parameters:
        -----------
        L : float
            Physical domain size in meters (default: 1 micrometer)
        N : int
            Number of grid points per dimension (default: 512)
        dt : float
            Time step in seconds (default: 1 femtosecond)
        """
        self.L = L
        self.N = N
        self.dt = dt
        self.dx = L / N
        
        # Precompute kinetic energy operator in Fourier space
        k = fftfreq(N, self.dx)
        self.k2 = (k**2)[:, np.newaxis] + (k**2)[np.newaxis, :]
        
        print(f"Solver initialized: Domain={L*1e6:.1f}μm, Grid={N}x{N}, Δt={dt*1e15:.1f}fs")
    
    def initial_superposition(self, x, y, slit_width=1e-7, slit_sep=2e-7):
        """
        Create initial superposition state representing electron passing through two slits.
        
        Parameters:
        -----------
        x, y : ndarray
            Spatial coordinates (meshgrid)
        slit_width : float
            Width of each slit
        slit_sep : float
            Separation between slit centers
            
        Returns:
        --------
        psi : ndarray (complex)
            Normalized superposition wavefunction
        """
        psi = np.zeros((self.N, self.N), dtype=complex)
        
        # Slit 1 (left)
        slit1_center = -slit_sep / 2
        mask1 = np.abs(x - slit1_center) < slit_width / 2
        psi[mask1] = 1.0
        
        # Slit 2 (right)
        slit2_center = slit_sep / 2
        mask2 = np.abs(x - slit2_center) < slit_width / 2
        psi[mask2] += 1.0
        
        # Normalize
        norm = np.linalg.norm(psi)
        return psi / norm if norm > 0 else psi
    
    def kinetic_energy_step(self, psi, hbar=1.055e-34, m_e=9.109e-31):
        """
        Apply kinetic energy evolution: exp(-i * T * dt / ℏ)
        Uses FFT for efficient Fourier space implementation.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
        hbar : float
            Reduced Planck constant
        m_e : float
            Electron mass
            
        Returns:
        --------
        psi_new : ndarray (complex)
            Evolved wavefunction
        """
        psi_k = fft2(psi)
        T_coeff = (hbar * self.k2) / (2 * m_e)
        phase = np.exp(-1j * T_coeff * self.dt / hbar)
        psi_k *= phase
        return ifft2(psi_k)
    
    def photon_reformation_force(self, psi, psi_eigenstate, 
                                 photon_energy=5e-19, c=3e8, hbar=1.055e-34):
        """
        Apply photon-mediated reformation force.
        Shifts wavefunction toward target eigenstate.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Current distorted wavefunction
        psi_eigenstate : ndarray (complex)
            Target eigenstate (e.g., localized to one slit)
        photon_energy : float
            Photon energy in Joules
        c : float
            Speed of light
        hbar : float
            Reduced Planck constant
            
        Returns:
        --------
        psi_reformed : ndarray (complex)
            Reformed wavefunction
        distortion : float
            Measure of current distortion (0-1)
        """
        # Photon wave vector
        k_gamma = np.sqrt(2 * photon_energy * hbar) / (hbar * c)
        
        # Distortion measure: D = 1 - |<psi_eigen|psi>|²
        overlap = np.abs(np.vdot(psi_eigenstate, psi))
        distortion = 1 - overlap**2
        
        # Force strength (larger distortion → stronger reformation)
        force_strength = distortion * k_gamma / self.dx
        
        # Apply phase correction (directional push toward eigenstate)
        phase_correction = np.exp(1j * force_strength * self.dt)
        psi_reformed = psi * phase_correction
        
        # Normalize
        norm = np.linalg.norm(psi_reformed)
        return psi_reformed / norm if norm > 0 else psi_reformed, distortion
    
    def evolve_no_photon(self, psi, steps=1000):
        """
        Evolve wavefunction without photon interaction (reference case).
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Initial wavefunction
        steps : int
            Number of evolution steps
            
        Returns:
        --------
        trajectory : list of ndarray
            Wavefunction at each time step
        """
        trajectory = [psi.copy()]
        
        print("Evolving without photon interaction...")
        for step in range(steps):
            psi = self.kinetic_energy_step(psi)
            trajectory.append(psi.copy())
            
            if (step + 1) % 100 == 0:
                print(f"  Step {step + 1}/{steps}")
        
        return trajectory
    
    def evolve_with_photon(self, psi, psi_eigenstate, 
                          photon_enable_step=500, steps=1000):
        """
        Evolve wavefunction with photon reformation starting at specified step.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Initial wavefunction
        psi_eigenstate : ndarray (complex)
            Target eigenstate for reformation
        photon_enable_step : int
            Time step when photon turns on
        steps : int
            Total evolution steps
            
        Returns:
        --------
        trajectory : list of ndarray
            Wavefunction at each time step
        distortion_history : list of float
            Distortion measure at each step after photon turns on
        """
        trajectory = [psi.copy()]
        distortion_history = []
        
        print(f"Evolving with photon reformation (starts at step {photon_enable_step})...")
        for step in range(steps):
            psi = self.kinetic_energy_step(psi)
            
            # Apply photon reformation force
            if step >= photon_enable_step:
                psi, distortion = self.photon_reformation_force(psi, psi_eigenstate)
            else:
                distortion = 1 - np.abs(np.vdot(psi_eigenstate, psi))**2
            
            trajectory.append(psi.copy())
            distortion_history.append(distortion)
            
            if (step + 1) % 100 == 0:
                print(f"  Step {step + 1}/{steps}, Distortion: {distortion:.4f}")
        
        return trajectory, distortion_history


# Usage Example
if __name__ == "__main__":
    # Initialize solver
    solver = DoubleSlitWavefunctionSolver(L=1e-6, N=256, dt=1e-18)
    
    # Create spatial grid
    x = np.linspace(-solver.L/2, solver.L/2, solver.N)
    y = np.linspace(-solver.L/2, solver.L/2, solver.N)
    X, Y = np.meshgrid(x, y)
    
    # Initial conditions
    psi_initial = solver.initial_superposition(X, Y)
    psi_eigenstate = solver.initial_superposition(X, Y - 1e-7)  # Eigenstate at slit 1
    
    # Run simulations
    trajectory_no_photon = solver.evolve_no_photon(psi_initial, steps=1000)
    trajectory_with_photon, distortion = solver.evolve_with_photon(
        psi_initial, psi_eigenstate, photon_enable_step=500, steps=1000
    )
    
    print("Simulations complete!")
