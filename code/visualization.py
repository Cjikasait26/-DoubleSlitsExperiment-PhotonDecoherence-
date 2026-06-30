"""
visualization.py

Publication-quality visualizations for wavefunction evolution,
decoherence dynamics, and photon calibration effects.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D


class WavefunctionVisualizer:
    """
    Creates publication-quality visualizations of quantum dynamics.
    """
    
    def __init__(self, figsize=(12, 9)):
        """
        Initialize visualizer.
        
        Parameters:
        -----------
        figsize : tuple
            Default figure size (inches)
        """
        self.figsize = figsize
        self.fig_count = 0
    
    def plot_wavefunction(self, psi, title="Wavefunction Intensity", 
                         cmap='viridis', vmin=None, vmax=None):
        """
        Create 2D contour plot of |ψ|² intensity.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
        title : str
            Plot title
        cmap : str
            Colormap name
        vmin, vmax : float
            Intensity scale limits
            
        Returns:
        --------
        fig, ax : matplotlib figure and axis
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        intensity = np.abs(psi)**2
        
        if vmin is None:
            vmin = np.min(intensity)
        if vmax is None:
            vmax = np.max(intensity)
        
        im = ax.contourf(intensity, levels=50, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Position X', fontsize=12)
        ax.set_ylabel('Position Y', fontsize=12)
        cbar = plt.colorbar(im, ax=ax, label='|ψ|² (Probability Density)')
        
        return fig, ax
    
    def plot_1d_cross_section(self, psi, axis=0, title="1D Cross-Section"):
        """
        Plot 1D cross-section of wavefunction intensity.
        
        Parameters:
        -----------
        psi : ndarray (complex)
            Wavefunction
        axis : int
            Which axis to take cross-section (0 or 1)
        title : str
            Plot title
            
        Returns:
        --------
        fig, ax : matplotlib figure and axis
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        intensity = np.abs(psi)**2
        
        if axis == 0:
            cross_section = intensity[intensity.shape[0]//2, :]
            xlabel = 'Position X'
        else:
            cross_section = intensity[:, intensity.shape[1]//2]
            xlabel = 'Position Y'
        
        position = np.arange(len(cross_section))
        ax.plot(position, cross_section, 'b-', linewidth=2)
        ax.fill_between(position, cross_section, alpha=0.3)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('|ψ|² (Probability Density)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return fig, ax
    
    def plot_trajectory_comparison(self, trajectory_no_photon, trajectory_with_photon,
                                   steps_to_show=5, vmin=None, vmax=None):
        """
        Side-by-side comparison of wavefunction evolution with/without photon.
        
        Parameters:
        -----------
        trajectory_no_photon : list of ndarray
            Trajectory without photon
        trajectory_with_photon : list of ndarray
            Trajectory with photon
        steps_to_show : int
            Number of timesteps to display
        vmin, vmax : float
            Intensity scale limits
            
        Returns:
        --------
        fig : matplotlib figure
        """
        fig, axes = plt.subplots(steps_to_show, 2, figsize=(14, 5*steps_to_show))
        
        # Determine shared scale
        all_intensities = [np.abs(t)**2 for t in trajectory_no_photon + trajectory_with_photon]
        if vmin is None:
            vmin = np.min([np.min(i) for i in all_intensities])
        if vmax is None:
            vmax = np.max([np.max(i) for i in all_intensities])
        
        indices = np.linspace(0, len(trajectory_no_photon)-1, steps_to_show, dtype=int)
        
        for i, idx in enumerate(indices):
            # Without photon
            intensity1 = np.abs(trajectory_no_photon[idx])**2
            im1 = axes[i, 0].contourf(intensity1, levels=50, cmap='viridis', 
                                      vmin=vmin, vmax=vmax)
            axes[i, 0].set_title(f'No Photon (t={idx})', fontweight='bold', fontsize=11)
            axes[i, 0].set_ylabel('Y Position', fontsize=10)
            plt.colorbar(im1, ax=axes[i, 0])
            
            # With photon
            intensity2 = np.abs(trajectory_with_photon[idx])**2
            im2 = axes[i, 1].contourf(intensity2, levels=50, cmap='viridis',
                                      vmin=vmin, vmax=vmax)
            axes[i, 1].set_title(f'With Photon (t={idx})', fontweight='bold', fontsize=11)
            axes[i, 1].set_ylabel('Y Position', fontsize=10)
            plt.colorbar(im2, ax=axes[i, 1])
        
        axes[-1, 0].set_xlabel('X Position', fontsize=11)
        axes[-1, 1].set_xlabel('X Position', fontsize=11)
        
        plt.suptitle('Wavefunction Evolution: With vs Without Photon Reformation',
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        return fig
    
    def plot_decoherence_timeline(self, distortion_history, dt=1e-18, gamma=None):
        """
        Plot distortion vs. time with exponential fit overlay.
        
        Parameters:
        -----------
        distortion_history : list or ndarray
            Time series of distortion values
        dt : float
            Time step (seconds)
        gamma : float
            Decoherence rate (optional, for fit overlay)
            
        Returns:
        --------
        fig, ax : matplotlib figure and axis
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        distortion_history = np.array(distortion_history)
        time = np.arange(len(distortion_history)) * dt * 1e15  # Convert to fs
        
        ax.plot(time, distortion_history, 'bo-', label='Measured Distortion',
               linewidth=2.5, markersize=5)
        
        # Overlay exponential decay fit
        if gamma is not None:
            fitted = distortion_history[0] * np.exp(-gamma * np.arange(len(distortion_history)) * dt)
            ax.plot(time, fitted, 'r--', label=f'Exponential Fit (γ={gamma:.2e} Hz)',
                   linewidth=2.5)
        
        ax.set_xlabel('Time (fs)', fontsize=13)
        ax.set_ylabel('Distortion D(t)', fontsize=13)
        ax.set_title('Photon-Mediated Decoherence Timeline', fontsize=14, fontweight='bold')
        ax.legend(fontsize=12, loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.05])
        
        return fig, ax
    
    def plot_multiple_metrics(self, metrics_dict, dt=1e-18):
        """
        Plot multiple decoherence metrics simultaneously.
        
        Parameters:
        -----------
        metrics_dict : dict
            Dictionary with keys: 'distortion', 'visibility', 'ipr', 'entropy'
            Each value is a list/array of time series
        dt : float
            Time step (seconds)
            
        Returns:
        --------
        fig : matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        time = np.arange(len(metrics_dict.get('distortion', [0]))) * dt * 1e15  # fs
        
        # Distortion
        if 'distortion' in metrics_dict:
            axes[0, 0].plot(time, metrics_dict['distortion'], 'b-o', linewidth=2)
            axes[0, 0].set_ylabel('Distortion D(t)', fontsize=11)
            axes[0, 0].set_title('Coherence Loss', fontweight='bold')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].set_ylim([0, 1])
        
        # Visibility
        if 'visibility' in metrics_dict:
            axes[0, 1].plot(time, metrics_dict['visibility'], 'g-o', linewidth=2)
            axes[0, 1].set_ylabel('Visibility V(t)', fontsize=11)
            axes[0, 1].set_title('Interference Contrast', fontweight='bold')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].set_ylim([0, 1])
        
        # IPR (Localization)
        if 'ipr' in metrics_dict:
            axes[1, 0].plot(time, metrics_dict['ipr'], 'r-o', linewidth=2)
            axes[1, 0].set_xlabel('Time (fs)', fontsize=11)
            axes[1, 0].set_ylabel('IPR (Localization)', fontsize=11)
            axes[1, 0].set_title('Wave-to-Particle Transition', fontweight='bold')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].set_ylim([0, 1])
        
        # Entropy
        if 'entropy' in metrics_dict:
            axes[1, 1].plot(time, metrics_dict['entropy'], 'm-o', linewidth=2)
            axes[1, 1].set_xlabel('Time (fs)', fontsize=11)
            axes[1, 1].set_ylabel('Entropy (bits)', fontsize=11)
            axes[1, 1].set_title('Information Content', fontweight='bold')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.suptitle('Decoherence Metrics Time Series', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_energy_dependence(self, energies, rates, log_scale=True):
        """
        Plot decoherence rate vs. photon energy.
        
        Parameters:
        -----------
        energies : ndarray
            Photon energies (eV)
        rates : ndarray
            Decoherence rates (Hz)
        log_scale : bool
            Use log-log scale
            
        Returns:
        --------
        fig, ax : matplotlib figure and axis
        """
        fig, ax = plt.subplots(figsize=(11, 7))
        
        if log_scale:
            ax.loglog(energies, rates, 'bo-', linewidth=2.5, markersize=7, label='Calculated')
            
            # Overlay E² theoretical scaling
            theoretical = rates[0] * (energies / energies[0])**2
            ax.loglog(energies, theoretical, 'r--', linewidth=2.5, label='E² Theoretical')
        else:
            ax.plot(energies, rates, 'bo-', linewidth=2.5, markersize=7, label='Calculated')
        
        ax.set_xlabel('Photon Energy (eV)', fontsize=13)
        ax.set_ylabel('Decoherence Rate γ (Hz)', fontsize=13)
        ax.set_title('Photon Energy Dependence: γ ∝ E²', fontsize=14, fontweight='bold')
        ax.legend(fontsize=12, loc='best')
        ax.grid(True, alpha=0.3, which='both')
        
        return fig, ax
    
    def animate_wavefunction(self, trajectory, dt=1e-18, 
                            output_file='wavefunction_animation.mp4', fps=30):
        """
        Create animation of wavefunction evolution.
        
        Parameters:
        -----------
        trajectory : list of ndarray
            Wavefunction at each time step
        dt : float
            Time step (seconds)
        output_file : str
            Output filename
        fps : int
            Frames per second
            
        Returns:
        --------
        anim : matplotlib animation object
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get intensity range for consistent scaling
        intensities = [np.abs(t)**2 for t in trajectory]
        vmin = np.min([np.min(i) for i in intensities])
        vmax = np.max([np.max(i) for i in intensities])
        
        def update(frame):
            ax.clear()
            intensity = np.abs(trajectory[frame])**2
            contour = ax.contourf(intensity, levels=50, cmap='viridis',
                                vmin=vmin, vmax=vmax)
            time_fs = frame * dt * 1e15
            ax.set_title(f'Wavefunction Evolution (t={time_fs:.1f} fs)',
                        fontweight='bold', fontsize=13)
            ax.set_xlabel('Position X', fontsize=11)
            ax.set_ylabel('Position Y', fontsize=11)
            plt.colorbar(contour, ax=ax, label='|ψ|²')
        
        anim = animation.FuncAnimation(fig, update, frames=len(trajectory),
                                      interval=1000//fps, repeat=True)
        
        try:
            anim.save(output_file, writer='ffmpeg', dpi=100)
            print(f"✓ Animation saved to {output_file}")
        except Exception as e:
            print(f"✗ Could not save animation: {e}")
            print("  (Make sure ffmpeg is installed)")
        
        return anim
    
    def create_summary_figure(self, psi_initial, psi_final, 
                             distortion_history, metrics_dict):
        """
        Create comprehensive summary figure with multiple panels.
        
        Parameters:
        -----------
        psi_initial : ndarray (complex)
            Initial wavefunction
        psi_final : ndarray (complex)
            Final wavefunction
        distortion_history : list
            Time series of distortion
        metrics_dict : dict
            Dictionary of other metrics
            
        Returns:
        --------
        fig : matplotlib figure
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
        
        # Initial wavefunction
        ax1 = fig.add_subplot(gs[0, 0])
        intensity_i = np.abs(psi_initial)**2
        im1 = ax1.contourf(intensity_i, levels=30, cmap='viridis')
        ax1.set_title('Initial |ψ|²', fontweight='bold')
        plt.colorbar(im1, ax=ax1)
        
        # Final wavefunction
        ax2 = fig.add_subplot(gs[0, 1])
        intensity_f = np.abs(psi_final)**2
        im2 = ax2.contourf(intensity_f, levels=30, cmap='viridis')
        ax2.set_title('Final |ψ|²', fontweight='bold')
        plt.colorbar(im2, ax=ax2)
        
        # Difference
        ax3 = fig.add_subplot(gs[0, 2])
        diff = np.abs(intensity_f - intensity_i)
        im3 = ax3.contourf(diff, levels=30, cmap='hot')
        ax3.set_title('Change in Intensity', fontweight='bold')
        plt.colorbar(im3, ax=ax3)
        
        # Distortion timeline
        ax4 = fig.add_subplot(gs[1, :])
        time = np.arange(len(distortion_history))
        ax4.plot(time, distortion_history, 'b-o', linewidth=2, markersize=4)
        ax4.fill_between(time, distortion_history, alpha=0.3)
        ax4.set_ylabel('Distortion', fontsize=11)
        ax4.set_title('Decoherence Timeline', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Other metrics
        if 'visibility' in metrics_dict:
            ax5 = fig.add_subplot(gs[2, 0])
            ax5.plot(metrics_dict['visibility'], 'g-o', linewidth=2)
            ax5.set_ylabel('Visibility', fontsize=10)
            ax5.set_title('Interference Contrast', fontweight='bold', fontsize=10)
            ax5.grid(True, alpha=0.3)
        
        if 'ipr' in metrics_dict:
            ax6 = fig.add_subplot(gs[2, 1])
            ax6.plot(metrics_dict['ipr'], 'r-o', linewidth=2)
            ax6.set_ylabel('IPR', fontsize=10)
            ax6.set_title('Localization', fontweight='bold', fontsize=10)
            ax6.grid(True, alpha=0.3)
        
        if 'entropy' in metrics_dict:
            ax7 = fig.add_subplot(gs[2, 2])
            ax7.plot(metrics_dict['entropy'], 'm-o', linewidth=2)
            ax7.set_ylabel('Entropy (bits)', fontsize=10)
            ax7.set_title('Information', fontweight='bold', fontsize=10)
            ax7.grid(True, alpha=0.3)
        
        fig.suptitle('Photon Calibration Decoherence Analysis Summary',
                    fontsize=15, fontweight='bold', y=0.995)
        
        return fig


# Usage Example
if __name__ == "__main__":
    print("Visualization module ready. Import and use WavefunctionVisualizer class.")
