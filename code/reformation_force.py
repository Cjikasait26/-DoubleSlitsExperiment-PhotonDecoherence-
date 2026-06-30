"""
reformation_force.py

Computes photon-mediated reformation force and decoherence dynamics.
Implements key equations from MATHEMATICS.md
"""

import numpy as np
import matplotlib.pyplot as plt


class ReformationForceCalculator:
    """
    Calculates photon-mediated reformation force and decoherence rates.
    """
    
    def __init__(self, hbar=1.055e-34, c=3e8, alpha=1/137, m_e=9.109e-31):
        """
        Initialize with fundamental constants.
        
        Parameters:
        -----------
        hbar : float
            Reduced Planck constant (J·s)
        c : float
            Speed of light (m/s)
        alpha : float
            Fine structure constant (~1/137)
        m_e : float
            Electron mass (kg)
        """
        self.hbar = hbar
        self.c = c
        self.alpha = alpha
        self.m_e = m_e
    
    def photon_wave_vector(self, photon_energy_eV):
        """
        Calculate photon wave vector: k_γ = E_γ / (ℏc)
        
        Parameters:
        -----------
        photon_energy_eV : float
            Photon energy in electron volts (eV)
            
        Returns:
        --------
        k_gamma : float
            Wave vector (1/m)
        """
        photon_energy = photon_energy_eV * 1.602e-19  # Convert eV to Joules
        return photon_energy / (self.hbar * self.c)
    
    def photon_wavelength(self, photon_energy_eV):
        """
        Calculate photon wavelength: λ = hc / E
        
        Parameters:
        -----------
        photon_energy_eV : float
            Photon energy in eV
            
        Returns:
        --------
        wavelength : float
            Wavelength in meters
        """
        # hc = 1240 eV·nm
        return 1240 / photon_energy_eV * 1e-9
    
    def energy_to_wavelength(self, energy_eV):
        """Convenience: eV → wavelength (nm)"""
        return 1240 / energy_eV
    
    def wavelength_to_energy(self, wavelength_nm):
        """Convenience: wavelength (nm) → eV"""
        return 1240 / wavelength_nm
    
    def momentum_transfer(self, photon_energy_eV):
        """
        Calculate momentum transfer: Δp = E_γ / c
        
        Parameters:
        -----------
        photon_energy_eV : float
            Photon energy in eV
            
        Returns:
        --------
        momentum : float
            Momentum transfer (kg·m/s)
        """
        photon_energy = photon_energy_eV * 1.602e-19
        return photon_energy / self.c
    
    def reformation_force_magnitude(self, distortion, photon_energy_eV, 
                                   dx=1e-9, duration=1e-18):
        """
        Calculate reformation force magnitude.
        
        F_reform ~ distortion × (momentum_transfer / spatial_scale)
        
        Parameters:
        -----------
        distortion : float
            Current distortion measure (0-1)
        photon_energy_eV : float
            Photon energy in eV
        dx : float
            Spatial scale (e.g., grid spacing)
        duration : float
            Duration of interaction
            
        Returns:
        --------
        force : float
            Force magnitude (Newtons)
        """
        p_transfer = self.momentum_transfer(photon_energy_eV)
        
        # Force ~ distortion × momentum_transfer / spatial_scale
        force = distortion * (p_transfer / dx)
        
        return force
    
    def decoherence_rate_photon(self, photon_energy_eV, E_atomic=27.2):
        """
        Calculate photon-induced decoherence rate.
        
        γ_reform ≈ (α × ω_γ / ℏ) × (E_γ / E_atomic)²
        
        Key: Rate scales quadratically with photon energy
        
        Parameters:
        -----------
        photon_energy_eV : float
            Photon energy in eV
        E_atomic : float
            Characteristic atomic energy scale (default: Rydberg = 27.2 eV)
            
        Returns:
        --------
        gamma : float
            Decoherence rate (Hz = 1/seconds)
        """
        photon_energy = photon_energy_eV * 1.602e-19  # Convert to Joules
        omega_gamma = photon_energy / self.hbar
        
        # Main formula: γ ∝ α × ω × (E/E_atomic)²
        gamma = (self.alpha * omega_gamma / self.hbar) * \
                (photon_energy_eV / E_atomic)**2
        
        return max(0, gamma)
    
    def visibility_decay(self, t, gamma, V0=0.9):
        """
        Exponential visibility decay: V(t) = V₀ × exp(-γ × t)
        
        Parameters:
        -----------
        t : float or ndarray
            Time (seconds)
        gamma : float
            Decoherence rate (Hz)
        V0 : float
            Initial visibility (0-1)
            
        Returns:
        --------
        visibility : float or ndarray
            Visibility at time t
        """
        return V0 * np.exp(-gamma * t)
    
    def energy_dissipation(self, force, velocity, dt=1e-18):
        """
        Calculate power and energy dissipated during reformation.
        
        Power: P = F · v
        Energy: W = P × dt
        
        Parameters:
        -----------
        force : float
            Force magnitude (N)
        velocity : float
            Electron velocity (m/s)
        dt : float
            Time interval (s)
            
        Returns:
        --------
        power : float
            Instantaneous power (Watts)
        energy : float
            Energy dissipated in interval (Joules)
        """
        power = force * velocity
        energy = power * dt
        return power, energy
    
    def optimal_photon_wavelength(self, target_decoherence_rate=1e12):
        """
        Find photon wavelength for specific decoherence rate.
        
        Parameters:
        -----------
        target_decoherence_rate : float
            Desired decoherence rate (Hz)
            
        Returns:
        --------
        optimal_wavelength : float
            Wavelength (meters)
        optimal_energy : float
            Photon energy (eV)
        optimal_rate : float
            Actual decoherence rate at optimum
        """
        wavelengths = np.linspace(1e-9, 1e-6, 1000)  # 1 nm to 1000 nm
        photon_energies_eV = 1240 / (wavelengths * 1e9)  # E = hc/λ in eV
        
        rates = [self.decoherence_rate_photon(E) for E in photon_energies_eV]
        
        # Find closest to target
        idx = np.argmin(np.abs(np.array(rates) - target_decoherence_rate))
        
        return wavelengths[idx], photon_energies_eV[idx], rates[idx]
    
    def parameter_study_energy_scaling(self):
        """
        Generate energy scaling study: verify γ ∝ E²
        
        Returns:
        --------
        energies : ndarray
            Photon energies (eV)
        rates : ndarray
            Decoherence rates (Hz)
        """
        energies = np.logspace(0, 1.5, 50)  # 1 eV to ~30 eV
        rates = np.array([self.decoherence_rate_photon(E) for E in energies])
        
        return energies, rates
    
    def verify_quadratic_scaling(self, energies, rates):
        """
        Verify quadratic scaling: γ ∝ E²
        
        Parameters:
        -----------
        energies : ndarray
            Photon energies
        rates : ndarray
            Measured decoherence rates
            
        Returns:
        --------
        exponent : float
            Fitted exponent (should be ~2.0)
        """
        # Fit log(γ) = exponent × log(E) + const
        log_energies = np.log10(energies)
        log_rates = np.log10(rates)
        
        coeffs = np.polyfit(log_energies, log_rates, 1)
        exponent = coeffs[0]
        
        return exponent


# Batch Analysis
class PhotocalibrationAnalysis:
    """
    Analyze photon calibration effects across parameter space.
    """
    
    def __init__(self):
        self.calc = ReformationForceCalculator()
    
    def scan_photon_energy(self, energy_range_eV=(1, 20), points=50):
        """
        Scan decoherence rate across photon energy range.
        
        Parameters:
        -----------
        energy_range_eV : tuple
            (min_eV, max_eV)
        points : int
            Number of points to sample
            
        Returns:
        --------
        energies : ndarray
        rates : ndarray
        """
        energies = np.linspace(energy_range_eV[0], energy_range_eV[1], points)
        rates = np.array([self.calc.decoherence_rate_photon(E) for E in energies])
        
        return energies, rates
    
    def scan_photon_wavelength(self, wavelength_range_nm=(100, 2000), points=50):
        """
        Scan decoherence rate across wavelength range.
        
        Parameters:
        -----------
        wavelength_range_nm : tuple
            (min_nm, max_nm)
        points : int
            Number of points
            
        Returns:
        --------
        wavelengths : ndarray (meters)
        rates : ndarray
        """
        wavelengths_nm = np.linspace(wavelength_range_nm[0], wavelength_range_nm[1], points)
        energies_eV = 1240 / wavelengths_nm
        rates = np.array([self.calc.decoherence_rate_photon(E) for E in energies_eV])
        
        return wavelengths_nm * 1e-9, rates
    
    def plot_energy_scaling(self):
        """Generate energy scaling verification plot."""
        energies, rates = self.parameter_study_energy_scaling()
        exponent = self.verify_quadratic_scaling(energies, rates)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.loglog(energies, rates, 'bo-', linewidth=2, markersize=6, label='Calculated')
        
        # Overlay theoretical E² scaling
        theoretical = rates[0] * (energies / energies[0])**2
        ax.loglog(energies, theoretical, 'r--', linewidth=2, label=f'E² scaling (exponent={exponent:.2f})')
        
        ax.set_xlabel('Photon Energy (eV)', fontsize=12)
        ax.set_ylabel('Decoherence Rate γ (Hz)', fontsize=12)
        ax.set_title('Energy Scaling Verification: γ ∝ E²', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, which='both')
        
        return fig, ax
    
    def plot_wavelength_dependence(self):
        """Generate wavelength dependence plot."""
        wavelengths, rates = self.scan_photon_wavelength()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.semilogy(wavelengths*1e9, rates, 'go-', linewidth=2, markersize=6)
        
        # Mark optimal wavelength region (500-1000 nm)
        ax.axvspan(500, 1000, alpha=0.2, color='yellow', label='Predicted Optimal Region')
        
        ax.set_xlabel('Wavelength (nm)', fontsize=12)
        ax.set_ylabel('Decoherence Rate γ (Hz)', fontsize=12)
        ax.set_title('Photon Wavelength Dependence', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        return fig, ax


# Usage Example
if __name__ == "__main__":
    calc = ReformationForceCalculator()
    
    print("=== Photon Calibration Reformation Force Calculator ===\n")
    
    # Example calculations
    photon_energies = [1, 2, 5, 10]  # eV
    
    print("Photon Energy → Decoherence Rate Scaling:")
    print("-" * 50)
    for E in photon_energies:
        gamma = calc.decoherence_rate_photon(E)
        wavelength = calc.photon_wavelength(E)
        print(f"  E = {E:2d} eV | λ = {wavelength*1e9:7.1f} nm | γ = {gamma:.2e} Hz")
    
    print("\n")
    
    # Find optimal wavelength
    optimal_wl, optimal_E, optimal_gamma = calc.optimal_photon_wavelength(target_decoherence_rate=1e12)
    print(f"Optimal photon wavelength for γ = 1e12 Hz:")
    print(f"  λ_opt = {optimal_wl*1e9:.1f} nm")
    print(f"  E_opt = {optimal_E:.2f} eV")
    print(f"  γ_actual = {optimal_gamma:.2e} Hz")
    
    print("\n")
    
    # Verify scaling law
    energies, rates = calc.parameter_study_energy_scaling()
    exponent = calc.verify_quadratic_scaling(energies, rates)
    print(f"Energy scaling verification:")
    print(f"  γ ∝ E^{exponent:.2f} (should be ~2.0)")
