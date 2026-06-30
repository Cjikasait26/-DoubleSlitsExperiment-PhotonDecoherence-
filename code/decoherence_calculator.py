"""
decoherence_calculator.py

Quantifies decoherence through multiple physical measures:
- Coherence loss (distortion)
- Visibility loss
- Localization (Inverse Participation Ratio)
- Entanglement entropy
- Decoherence rate extraction
"""

import numpy as np
from scipy.stats import entropy


class DecoherenceCalculator:
    """
    Quantifies decoherence and quantum-to-classical transition metrics.
    """
    
    def __init__(self, hbar=1.055e-34):
        """
        Initialize calculator with fundamental constants.
        
        Parameters:
        -----------
        hbar : float
            Reduced Planck constant
        """
        self.hbar = hbar
    
    def coherence_loss(self, psi_current, psi_reference):
        """
        Calculate distortion measure: D(t) = 1 - |<ψ_ref|ψ(t)>|²
        
        Quantifies how much the current wavefunction has deviated from reference.
        
        Parameters:
        -----------
        psi_current : ndarray (complex)
            Current wavefunction
        psi_reference : ndarray (complex)
            Reference (undistorted) wavefunction
            
        Returns:
        --------
        distortion : float
            Distortion measure (0 = perfect coherence, 1 = complete decoherence)
        """
        overlap = np.abs(np.vdot(psi_reference, psi_current))
        distortion = 1 - overlap**2
        return np.clip(distortion, 0, 1)
    
    def visibility(self, psi, threshold=1e-10):
        """
        Calculate interference pattern visibility: V = (I_max - I_min)/(I_max + I_min)
        
        Measures the contrast of interference fringes.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
        threshold : float
            Minimum intensity to consider (noise floor)
            
        Returns:
        --------
        visibility : float
            Visibility (0 = no interference, 1 = perfect interference)
        """
        intensity = np.abs(psi)**2
        intensity = np.where(intensity < threshold, 0, intensity)
        
        I_max = np.max(intensity)
        I_min = np.min(intensity)
        
        denominator = I_max + I_min
        if denominator == 0:
            return 0
        
        visibility = (I_max - I_min) / denominator
        return np.clip(visibility, 0, 1)
    
    def inverse_participation_ratio(self, psi):
        """
        Calculate Inverse Participation Ratio (IPR): localization measure.
        
        IPR = [∫ |ψ(r)|⁴ dr]⁻¹
        
        - IPR → 0: Highly delocalized (wave-like, spreads over space)
        - IPR → 1: Highly localized (particle-like, confined to region)
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
            
        Returns:
        --------
        ipr : float
            Localization measure (0-1)
        """
        prob = np.abs(psi)**2
        prob_sum = np.sum(prob)
        
        if prob_sum == 0:
            return 0
        
        # Normalize probability
        prob = prob / prob_sum
        
        # IPR calculation
        ipr = np.sum(prob**2)
        
        # Normalize by volume to get scale-independent measure
        volume = np.size(psi)
        normalized_ipr = ipr * volume
        
        return np.clip(normalized_ipr, 0, 1)
    
    def participation_number(self, psi):
        """
        Calculate participation number: inverse of IPR.
        
        N_P = 1 / Σ_i |ψ_i|⁴
        
        - N_P ≈ 1: Localized to one point
        - N_P >> 1: Delocalized across many points
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
            
        Returns:
        --------
        N_P : float
            Participation number (>0)
        """
        prob = np.abs(psi)**2
        prob = prob.flatten()
        prob = prob[prob > 0]  # Remove zeros
        
        prob = prob / np.sum(prob)  # Normalize
        
        sum_prob2 = np.sum(prob**2)
        if sum_prob2 > 0:
            return 1.0 / sum_prob2
        return 0
    
    def entanglement_entropy(self, psi):
        """
        Calculate Shannon entropy of probability distribution.
        
        S = -Σ p_i log₂(p_i)
        
        Measures degree of delocalization in information-theoretic sense.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
            
        Returns:
        --------
        entropy_val : float
            Shannon entropy (bits)
        """
        prob = np.abs(psi)**2
        prob = prob.flatten()
        prob = prob[prob > 0]  # Remove zeros
        
        prob = prob / np.sum(prob)  # Normalize
        
        ent = entropy(prob, base=2)
        return ent
    
    def decoherence_rate(self, distortion_history, dt=1e-18):
        """
        Extract decoherence rate from distortion history.
        
        Fits exponential decay: D(t) ≈ D_0 * exp(-γ * t)
        
        Parameters:
        -----------
        distortion_history : list or ndarray
            Time series of distortion values
        dt : float
            Time step between measurements
            
        Returns:
        --------
        gamma : float
            Decoherence rate in Hz (1/seconds)
        """
        distortion_history = np.array(distortion_history)
        
        # Remove zeros and very small values
        mask = distortion_history > 1e-6
        if np.sum(mask) < 2:
            return 0
        
        distortion_history = distortion_history[mask]
        
        # Time array
        time = np.arange(len(distortion_history)) * dt
        
        # Log transform
        log_distortion = np.log(distortion_history + 1e-10)
        
        # Linear fit to extract decay rate: log(D) = log(D_0) - γ*t
        coeffs = np.polyfit(time, log_distortion, 1)
        gamma = -coeffs[0]  # Negative slope = decay rate
        
        return max(0, gamma)  # Ensure non-negative
    
    def measure_quality(self, psi_reformed, psi_target):
        """
        Quality of reformation: how well does reformed state match target eigenstate?
        
        Q = |<ψ_target|ψ_reformed>|²
        
        Parameters:
        -----------
        psi_reformed : ndarray (complex)
            Reformed wavefunction
        psi_target : ndarray (complex)
            Target eigenstate
            
        Returns:
        --------
        quality : float
            Quality measure (0-1, where 1 is perfect match)
        """
        overlap = np.abs(np.vdot(psi_target, psi_reformed))
        quality = overlap**2
        return np.clip(quality, 0, 1)
    
    def summarize_decoherence(self, psi_initial, psi_current, photon_enabled=True):
        """
        Generate comprehensive decoherence summary.
        
        Parameters:
        -----------
        psi_initial : ndarray (complex)
            Initial wavefunction
        psi_current : ndarray (complex)
            Current wavefunction
        photon_enabled : bool
            Whether photon reformation is active
            
        Returns:
        --------
        summary : dict
            Dictionary of all decoherence metrics
        """
        summary = {
            'coherence_loss': self.coherence_loss(psi_current, psi_initial),
            'visibility': self.visibility(psi_current),
            'ipr': self.inverse_participation_ratio(psi_current),
            'participation_number': self.participation_number(psi_current),
            'entropy': self.entanglement_entropy(psi_current),
            'photon_enabled': photon_enabled
        }
        return summary


# Batch Analysis Functions
class DecoherenceBatchAnalyzer:
    """
    Analyze trajectories and extract decoherence characteristics.
    """
    
    def __init__(self):
        self.calc = DecoherenceCalculator()
    
    def analyze_trajectory(self, trajectory, psi_initial):
        """
        Analyze complete trajectory and extract all metrics.
        
        Parameters:
        -----------
        trajectory : list of ndarray
            Complete wavefunction trajectory
        psi_initial : ndarray (complex)
            Initial wavefunction
            
        Returns:
        --------
        metrics : dict
            Dictionary containing time series of all metrics
        """
        metrics = {
            'distortion': [],
            'visibility': [],
            'ipr': [],
            'entropy': []
        }
        
        for psi in trajectory:
            metrics['distortion'].append(
                self.calc.coherence_loss(psi, psi_initial)
            )
            metrics['visibility'].append(
                self.calc.visibility(psi)
            )
            metrics['ipr'].append(
                self.calc.inverse_participation_ratio(psi)
            )
            metrics['entropy'].append(
                self.calc.entanglement_entropy(psi)
            )
        
        return metrics
    
    def compare_trajectories(self, traj_no_photon, traj_with_photon, psi_initial):
        """
        Compare decoherence signatures with and without photon.
        
        Parameters:
        -----------
        traj_no_photon : list of ndarray
            Trajectory without photon
        traj_with_photon : list of ndarray
            Trajectory with photon
        psi_initial : ndarray (complex)
            Initial wavefunction
            
        Returns:
        --------
        comparison : dict
            Metrics for both trajectories
        """
        comparison = {
            'no_photon': self.analyze_trajectory(traj_no_photon, psi_initial),
            'with_photon': self.analyze_trajectory(traj_with_photon, psi_initial)
        }
        
        return comparison


# Usage Example
if __name__ == "__main__":
    from wavefunction_solver import DoubleSlitWavefunctionSolver
    
    # Setup
    solver = DoubleSlitWavefunctionSolver(L=1e-6, N=256)
    calc = DecoherenceCalculator()
    
    x = np.linspace(-solver.L/2, solver.L/2, solver.N)
    y = np.linspace(-solver.L/2, solver.L/2, solver.N)
    X, Y = np.meshgrid(x, y)
    
    psi_initial = solver.initial_superposition(X, Y)
    psi_eigenstate = solver.initial_superposition(X, Y - 1e-7)
    
    # Run simulation
    traj, distortion = solver.evolve_with_photon(
        psi_initial, psi_eigenstate, photon_enable_step=500, steps=1000
    )
    
    # Analyze
    gamma = calc.decoherence_rate(distortion)
    print(f"Decoherence Rate: {gamma:.2e} Hz")
    
    # Final summary
    final_summary = calc.summarize_decoherence(psi_initial, traj[-1])
    print("\nFinal Decoherence Summary:")
    for key, val in final_summary.items():
        if isinstance(val, (int, float)):
            print(f"  {key}: {val:.4f}")
