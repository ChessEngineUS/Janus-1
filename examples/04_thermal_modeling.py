#!/usr/bin/env python3
"""
Thermal Modeling Example
========================

Demonstrates thermal analysis for Janus-1:
- Junction temperature calculation
- Thermal resistance modeling
- Hotspot identification
- Cooling solution evaluation

Runtime: ~2 minutes
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from pathlib import Path


class ThermalModel:
    """Thermal model for Janus-1 SoC."""
    
    def __init__(self, ambient_temp: float = 25.0):
        """
        Initialize thermal model.
        
        Args:
            ambient_temp: Ambient temperature in °C
        """
        self.t_ambient = ambient_temp
        
        # Thermal resistance values (°C/W)
        self.r_jc = 0.15  # Junction to case
        self.r_cs = 0.05  # Case to heat spreader
        self.r_sa = 1.50  # Heat spreader to ambient (with fan)
        
        # Component power distribution
        self.power_map = {
            'compute': 0.0,
            'sram': 0.0,
            'edram': 0.0,
            'interconnect': 0.0,
            'prefetcher': 0.01
        }
    
    def set_power_distribution(self, total_power: float, 
                              compute_tiles: int = 16,
                              sram_mb: float = 32.0,
                              edram_mb: float = 224.0):
        """Set power distribution across components."""
        # Compute power (120 mW per tile)
        self.power_map['compute'] = compute_tiles * 0.12
        
        # SRAM power (0.55 mW/MB)
        self.power_map['sram'] = sram_mb * 0.55e-3
        
        # eDRAM power (5.13 mW/MB)
        self.power_map['edram'] = edram_mb * 5.13e-3
        
        # Interconnect (8% of total)
        self.power_map['interconnect'] = total_power * 0.08
        
        # Normalize to match total
        current_total = sum(self.power_map.values())
        scale = total_power / current_total
        for key in self.power_map:
            self.power_map[key] *= scale
    
    def calculate_junction_temp(self, power: float) -> float:
        """Calculate junction temperature."""
        r_total = self.r_jc + self.r_cs + self.r_sa
        temp_rise = power * r_total
        return self.t_ambient + temp_rise
    
    def thermal_profile(self, x_coord: float, y_coord: float, 
                       die_size: float = 8.9) -> float:
        """
        Calculate temperature at a given (x, y) coordinate on die.
        
        Args:
            x_coord: X coordinate in mm (0 to die_size)
            y_coord: Y coordinate in mm (0 to die_size)
            die_size: Die edge length in mm
        
        Returns:
            Temperature in °C at that location
        """
        # Compute tiles are hotspots (located at quadrants)
        hotspots = [
            (die_size * 0.25, die_size * 0.25),  # Quadrant 1
            (die_size * 0.75, die_size * 0.25),  # Quadrant 2
            (die_size * 0.25, die_size * 0.75),  # Quadrant 3
            (die_size * 0.75, die_size * 0.75),  # Quadrant 4
        ]
        
        # Base temperature (average)
        base_temp = self.calculate_junction_temp(sum(self.power_map.values()))
        
        # Add hotspot contributions (Gaussian)
        hotspot_temp = 0.0
        for hx, hy in hotspots:
            dist_sq = (x_coord - hx)**2 + (y_coord - hy)**2
            hotspot_temp += 15.0 * np.exp(-dist_sq / 2.0)  # Peak 15°C
        
        return base_temp + hotspot_temp


def analyze_thermal_scenarios() -> Dict:
    """Analyze thermal performance under various scenarios."""
    print("\n" + "="*60)
    print("THERMAL SCENARIO ANALYSIS")
    print("="*60)
    
    scenarios = {
        'idle': 0.5,        # Idle power
        'typical': 4.05,    # Typical workload
        'peak': 6.0,        # Peak performance
        'stress': 8.0       # Stress test
    }
    
    results = {}
    model = ThermalModel(ambient_temp=25.0)
    
    print("\n{:<15} {:<12} {:<15} {:<10}".format(
        "Scenario", "Power (W)", "Junction (°C)", "Margin (°C)"))
    print("-" * 60)
    
    t_max = 105.0  # Maximum junction temperature
    
    for scenario, power in scenarios.items():
        model.set_power_distribution(power)
        t_junction = model.calculate_junction_temp(power)
        margin = t_max - t_junction
        
        results[scenario] = {
            'power': power,
            'junction_temp': t_junction,
            'thermal_margin': margin,
            'safe': margin > 0
        }
        
        status = "✓" if margin > 0 else "✗"
        print(f"{scenario:<15} {power:<12.2f} {t_junction:<15.1f} "
              f"{margin:<10.1f} {status}")
    
    return results


def cooling_solution_comparison() -> Dict:
    """Compare different cooling solutions."""
    print("\n" + "="*60)
    print("COOLING SOLUTION COMPARISON")
    print("="*60)
    
    power = 4.05  # Typical operating power
    
    # Different cooling solutions (thermal resistance in °C/W)
    solutions = {
        'passive': {
            'r_jc': 0.15,
            'r_cs': 0.05,
            'r_sa': 10.0,  # No fan
            'cost': 0.50
        },
        'fan_low': {
            'r_jc': 0.15,
            'r_cs': 0.05,
            'r_sa': 3.0,   # Low-speed fan
            'cost': 2.00
        },
        'fan_medium': {
            'r_jc': 0.15,
            'r_cs': 0.05,
            'r_sa': 1.5,   # Medium-speed fan
            'cost': 4.00
        },
        'fan_high': {
            'r_jc': 0.15,
            'r_cs': 0.05,
            'r_sa': 0.8,   # High-speed fan
            'cost': 8.00
        },
        'liquid': {
            'r_jc': 0.15,
            'r_cs': 0.05,
            'r_sa': 0.3,   # Liquid cooling
            'cost': 50.00
        }
    }
    
    print("\n{:<15} {:<15} {:<12} {:<10}".format(
        "Solution", "Junction (°C)", "Margin (°C)", "Cost ($)"))
    print("-" * 60)
    
    results = {}
    t_max = 105.0
    
    for name, params in solutions.items():
        r_total = params['r_jc'] + params['r_cs'] + params['r_sa']
        t_junction = 25.0 + power * r_total
        margin = t_max - t_junction
        
        results[name] = {
            'r_total': r_total,
            'junction_temp': t_junction,
            'margin': margin,
            'cost': params['cost']
        }
        
        print(f"{name:<15} {t_junction:<15.1f} {margin:<12.1f} "
              f"{params['cost']:<10.2f}")
    
    return results


def create_thermal_map():
    """Create 2D thermal map of die."""
    print("\n" + "="*60)
    print("GENERATING THERMAL MAP")
    print("="*60)
    
    die_size = 8.9  # mm
    resolution = 100
    
    model = ThermalModel(ambient_temp=25.0)
    model.set_power_distribution(4.05)
    
    x = np.linspace(0, die_size, resolution)
    y = np.linspace(0, die_size, resolution)
    X, Y = np.meshgrid(x, y)
    
    # Calculate temperature at each point
    print("Calculating thermal profile...")
    Z = np.zeros_like(X)
    for i in range(resolution):
        for j in range(resolution):
            Z[i, j] = model.thermal_profile(X[i, j], Y[i, j], die_size)
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Heatmap
    im = ax1.contourf(X, Y, Z, levels=20, cmap='hot')
    ax1.set_xlabel('X Position (mm)', fontsize=12)
    ax1.set_ylabel('Y Position (mm)', fontsize=12)
    ax1.set_title('Die Temperature Distribution', fontsize=13, fontweight='bold')
    ax1.set_aspect('equal')
    
    # Add quadrant markers
    quadrants = [(die_size * 0.25, die_size * 0.25),
                 (die_size * 0.75, die_size * 0.25),
                 (die_size * 0.25, die_size * 0.75),
                 (die_size * 0.75, die_size * 0.75)]
    for i, (qx, qy) in enumerate(quadrants, 1):
        ax1.plot(qx, qy, 'w*', markersize=15)
        ax1.text(qx, qy + 0.3, f'Q{i}', color='white', 
                ha='center', fontsize=10, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Temperature (°C)', fontsize=11)
    
    # Temperature histogram
    temps_flat = Z.flatten()
    ax2.hist(temps_flat, bins=50, edgecolor='black', alpha=0.7)
    ax2.axvline(temps_flat.mean(), color='red', linestyle='--', 
               linewidth=2, label=f'Mean: {temps_flat.mean():.1f}°C')
    ax2.axvline(temps_flat.max(), color='orange', linestyle='--', 
               linewidth=2, label=f'Max: {temps_flat.max():.1f}°C')
    ax2.axvline(105, color='darkred', linestyle='-', 
               linewidth=2, label='T_max: 105°C')
    ax2.set_xlabel('Temperature (°C)', fontsize=12)
    ax2.set_ylabel('Pixel Count', fontsize=12)
    ax2.set_title('Temperature Distribution', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_dir = Path('results/thermal_analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'thermal_map.png', dpi=300, bbox_inches='tight')
    print(f"\nSaved thermal map to {output_dir / 'thermal_map.png'}")
    
    plt.close()
    
    # Statistics
    print(f"\nThermal Statistics:")
    print(f"  Mean Temperature: {temps_flat.mean():.1f}°C")
    print(f"  Max Temperature:  {temps_flat.max():.1f}°C")
    print(f"  Min Temperature:  {temps_flat.min():.1f}°C")
    print(f"  Std Deviation:    {temps_flat.std():.1f}°C")
    print(f"  Thermal Margin:   {105 - temps_flat.max():.1f}°C")


def main():
    """Main execution function."""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  Janus-1: Thermal Modeling Example".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Scenario analysis
    scenario_results = analyze_thermal_scenarios()
    
    # Cooling solutions
    cooling_results = cooling_solution_comparison()
    
    # Thermal map
    create_thermal_map()
    
    # Summary
    print("\n" + "="*60)
    print("THERMAL ANALYSIS SUMMARY")
    print("="*60)
    
    print("\nKey Findings:")
    print("1. Typical operation: 4.05W → ~32°C junction temperature")
    print("2. Thermal margin: >70°C at typical workload")
    print("3. Recommended cooling: Medium-speed fan ($4)")
    print("4. Hotspots located in compute quadrants")
    print("5. Peak temperature gradient: ~15°C across die")
    
    print("\nRecommendations:")
    print("- Monitor junction temperature during stress tests")
    print("- Implement dynamic frequency scaling if T_j > 85°C")
    print("- Consider copper heat spreader for better uniformity")
    print("- Add thermal sensors near compute tiles")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()