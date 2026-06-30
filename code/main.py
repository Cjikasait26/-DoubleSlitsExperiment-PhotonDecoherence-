"""
main.py

Complete workflow for Photon Calibration Double-Slit Experiment.
Integrates solver, calculator, force analysis, and visualization.

Run this script to execute the full simulation and analysis pipeline.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import custom modules
from wavefunction_solver import DoubleSlitWavefunctionSolver
from decoherence_calculator import DecoherenceCalculator, DecoherenceBatchAnalyzer
from reformation_force import ReformationForceCalculator, PhotocalibrationAnalysis
from visualization import WavefunctionVisualizer


def setup_directories():
    """Create output directories for results."""
    Path('results').mkdir(exist_ok=True)
    Path('results/plots').mkdir(exist_ok=True)
    Path('results/data').mkdir(exist_ok=True)
    print("✓ Output directories ready")


def run_simulation(save_data=True):
    """
    Execute complete simulation workflow.
    
    Parameters:
    -----------
    save_data : bool
        Whether to save numerical results
        
    Returns:
    --------
    results : dict
        Dictionary containing all simulation outputs
    """
    print("\n" + "="*70)
    print("PHOTON CALIBRATION DOUBLE-SLIT EXPERIMENT SIMULATION")
    print("="*70 + "\n")
    
    # ========== STEP 1: Initialize Solvers ==========
    print("STEP 1: Initializing Solvers")
    print("-" * 70)
    
    solver = DoubleSlitWavefunctionSolver(L=1e-6, N=256, dt=1e-18)
    calc = DecoherenceCalculator()
    force_calc = ReformationForceCalculator()
    analyzer = DecoherenceBatchAnalyzer()
    vis = WavefunctionVisualizer()
    
    print("✓ Wavefunction Solver initialized")
    print("✓ Decoherence Calculator initialized")
    print("✓ Reformation Force Calculator initialized")
    print("✓ Visualizer initialized\n")
    
    # ========== STEP 2: Setup Initial Conditions ==========
    print("STEP 2: Setting up Initial Conditions")
    print("-" * 70)
    
    x = np.linspace(-solver.L/2, solver.L/2, solver.N)
    y = np.linspace(-solver.L/2, solver.L/2, solver.N)
    X, Y = np.meshgrid(x, y)
    
    psi_initial = solver.initial_superposition(X, Y, 
                                               slit_width=1e-7, 
                                               slit_sep=2e-7)
    psi_eigenstate = solver.initial_superposition(X, Y - 1e-7)
    
    print(f"✓ Initial superposition state created")
    print(f"  - Grid: {solver.N}x{solver.N}")
    print(f"  - Domain: {solver.L*1e6:.1f} μm × {solver.L*1e6:.1f} μm")
    print(f"  - Initial visibility: {calc.visibility(psi_initial):.3f}")
    print(f"  - Initial localization (IPR): {calc.inverse_participation_ratio(psi_initial):.4f}\n")
    
    # ========== STEP 3: Run Simulations ==========
    print("STEP 3: Running Simulations")
    print("-" * 70)
    
    print("\n[A] Baseline Evolution (No Photon)")
    trajectory_no_photon = solver.evolve_no_photon(psi_initial, steps=1000)
    
    print("\n[B] With Photon Reformation (enabled at step 500)")
    trajectory_with_photon, distortion = solver.evolve_with_photon(
        psi_initial, psi_eigenstate, 
        photon_enable_step=500, 
        steps=1000
    )
    
    print("✓ Simulations complete\n")
    
    # ========== STEP 4: Calculate Decoherence Metrics ==========
    print("STEP 4: Analyzing Decoherence Metrics")
    print("-" * 70)
    
    gamma = calc.decoherence_rate(distortion)
    
    print(f"✓ Decoherence rate extracted: γ = {gamma:.2e} Hz")
    print(f"  Interpretation: System collapses in ~{1/gamma*1e15:.1f} fs")
    
    # Analyze both trajectories
    comparison = analyzer.compare_trajectories(
        trajectory_no_photon, 
        trajectory_with_photon, 
        psi_initial
    )
    
    print(f"\nFinal State Analysis:")
    print(f"  No Photon:")
    print(f"    - Visibility: {comparison['no_photon']['visibility'][-1]:.3f}")
    print(f"    - IPR (Localization): {comparison['no_photon']['ipr'][-1]:.4f}")
    print(f"    - Entropy: {comparison['no_photon']['entropy'][-1]:.2f} bits")
    
    print(f"  With Photon:")
    print(f"    - Visibility: {comparison['with_photon']['visibility'][-1]:.3f}")
    print(f"    - IPR (Localization): {comparison['with_photon']['ipr'][-1]:.4f}")
    print(f"    - Entropy: {comparison['with_photon']['entropy'][-1]:.2f} bits\n")
    
    # ========== STEP 5: Calculate Reformation Force Properties ==========
    print("STEP 5: Analyzing Reformation Force Properties")
    print("-" * 70)
    
    # Energy scaling analysis
    energies, rates = force_calc.parameter_study_energy_scaling()
    exponent = force_calc.verify_quadratic_scaling(energies, rates)
    
    print(f"✓ Energy Scaling Verification:")
    print(f"  Predicted: γ ∝ E²")
    print(f"  Measured exponent: {exponent:.2f}")
    print(f"  Deviation: {abs(exponent - 2.0):.2f} (should be < 0.3)")
    
    # Optimal wavelength
    optimal_wl, optimal_E, optimal_gamma = force_calc.optimal_photon_wavelength(
        target_decoherence_rate=1e12
    )
    
    print(f"\n✓ Optimal Photon Properties (for γ = 1e12 Hz):")
    print(f"  Wavelength: {optimal_wl*1e9:.1f} nm")
    print(f"  Energy: {optimal_E:.2f} eV")
    print(f"  Actual rate: {optimal_gamma:.2e} Hz")
    print(f"  (Predicted optimal range: 500-1000 nm)\n")
    
    # ========== STEP 6: Generate Visualizations ==========
    print("STEP 6: Generating Visualizations")
    print("-" * 70)
    
    # Trajectory comparison
    fig_traj = vis.plot_trajectory_comparison(
        trajectory_no_photon, 
        trajectory_with_photon, 
        steps_to_show=5
    )
    fig_traj.savefig('results/plots/01_trajectory_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 01_trajectory_comparison.png")
    
    # Decoherence timeline
    fig_timeline, _ = vis.plot_decoherence_timeline(distortion, gamma=gamma)
    fig_timeline.savefig('results/plots/02_decoherence_timeline.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 02_decoherence_timeline.png")
    
    # Multiple metrics
    fig_metrics = vis.plot_multiple_metrics(comparison['with_photon'])
    fig_metrics.savefig('results/plots/03_decoherence_metrics.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 03_decoherence_metrics.png")
    
    # Energy scaling
    photocal_analysis = PhotocalibrationAnalysis()
    fig_energy, _ = photocal_analysis.plot_energy_scaling()
    fig_energy.savefig('results/plots/04_energy_scaling.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 04_energy_scaling.png")
    
    # Wavelength dependence
    fig_wavelength, _ = photocal_analysis.plot_wavelength_dependence()
    fig_wavelength.savefig('results/plots/05_wavelength_dependence.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 05_wavelength_dependence.png")
    
    # Summary figure
    fig_summary = vis.create_summary_figure(
        psi_initial, 
        trajectory_with_photon[-1],
        distortion,
        comparison['with_photon']
    )
    fig_summary.savefig('results/plots/06_summary_figure.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 06_summary_figure.png")
    
    print()
    
    # ========== STEP 7: Save Data ==========
    if save_data:
        print("STEP 7: Saving Numerical Results")
        print("-" * 70)
        
        np.save('results/data/distortion_history.npy', distortion)
        np.save('results/data/visibility_with_photon.npy', comparison['with_photon']['visibility'])
        np.save('results/data/visibility_no_photon.npy', comparison['no_photon']['visibility'])
        np.save('results/data/energy_values.npy', energies)
        np.save('results/data/decoherence_rates.npy', rates)
        
        print("✓ Saved: distortion_history.npy")
        print("✓ Saved: visibility_*.npy")
        print("✓ Saved: energy_values.npy, decoherence_rates.npy")
        print()
    
    # ========== Compile Results ==========
    results = {
        'solver': solver,
        'calculator': calc,
        'force_calculator': force_calc,
        'psi_initial': psi_initial,
        'trajectory_no_photon': trajectory_no_photon,
        'trajectory_with_photon': trajectory_with_photon,
        'distortion': distortion,
        'gamma': gamma,
        'comparison': comparison,
        'energies': energies,
        'rates': rates,
        'exponent': exponent,
        'optimal_wavelength': optimal_wl,
        'optimal_energy': optimal_E,
    }
    
    return results


def print_summary(results):
    """Print final summary report."""
    print("\n" + "="*70)
    print("SIMULATION SUMMARY & KEY FINDINGS")
    print("="*70 + "\n")
    
    print("HYPOTHESIS VERIFICATION")
    print("-" * 70)
    print(f"✓ Photon Energy Scaling: γ ∝ E^{results['exponent']:.2f}")
    print(f"  → Prediction (γ ∝ E²) {'CONFIRMED ✓' if abs(results['exponent']-2) < 0.3 else 'INCONCLUSIVE'}")
    
    print(f"\n✓ Optimal Wavelength: {results['optimal_wavelength']*1e9:.1f} nm")
    print(f"  → Prediction (500-1000 nm) {'CONFIRMED ✓' if 500 <= results['optimal_wavelength']*1e9 <= 1000 else 'MISMATCH'}")
    
    gamma = results['gamma']
    print(f"\n✓ Decoherence Rate: γ = {gamma:.2e} Hz")
    print(f"  → Collapse timescale: ~{1/gamma*1e15:.1f} fs")
    
    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print("\nPlots saved to: results/plots/")
    print("  • 01_trajectory_comparison.png")
    print("  • 02_decoherence_timeline.png")
    print("  • 03_decoherence_metrics.png")
    print("  • 04_energy_scaling.png")
    print("  • 05_wavelength_dependence.png")
    print("  • 06_summary_figure.png")
    
    print("\nData saved to: results/data/")
    print("  • distortion_history.npy")
    print("  • visibility_with_photon.npy")
    print("  • visibility_no_photon.npy")
    print("  • energy_values.npy")
    print("  • decoherence_rates.npy")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Review generated plots in results/plots/
2. Compare predictions with experimental data (if available)
3. Refine parameters based on comparison
4. Test additional predictions from PREDICTIONS.md
5. Conduct sensitivity analysis on key parameters

For detailed mathematical framework, see: MATHEMATICS.md
For full experimental predictions, see: PREDICTIONS.md
For simulation architecture, see: SIMULATIONS.md
""")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Setup
    setup_directories()
    
    # Run full simulation
    results = run_simulation(save_data=True)
    
    # Display summary
    print_summary(results)
    
    # Keep plots open
    plt.show()
