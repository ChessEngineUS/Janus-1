#!/usr/bin/env python3
"""
Advanced Optimization Example
==============================

This example demonstrates advanced optimization techniques for Janus-1:
- Multi-objective optimization (power vs. performance)
- Pareto frontier exploration
- Sensitivity analysis
- Design space exploration

Runtime: ~5 minutes on modern CPU
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import json
from pathlib import Path


class DesignPoint:
    """Represents a single point in the design space."""
    
    def __init__(self, sram_mb: float, edram_mb: float, 
                 lookahead: int, compute_tiles: int):
        self.sram_mb = sram_mb
        self.edram_mb = edram_mb
        self.lookahead = lookahead
        self.compute_tiles = compute_tiles
        
        # Evaluate metrics
        self.power = self._calculate_power()
        self.performance = self._calculate_performance()
        self.area = self._calculate_area()
    
    def _calculate_power(self) -> float:
        """Calculate total power consumption in watts."""
        # SRAM: ~0.55 mW/MB @ 3nm
        sram_power = self.sram_mb * 0.55e-3
        
        # eDRAM: ~5.13 mW/MB @ 3nm
        edram_power = self.edram_mb * 5.13e-3
        
        # Compute: ~120 mW per tile
        compute_power = self.compute_tiles * 0.12
        
        # Prefetcher: ~10 mW (fixed)
        prefetch_power = 0.01
        
        return sram_power + edram_power + compute_power + prefetch_power
    
    def _calculate_performance(self) -> float:
        """Calculate throughput in TOPS."""
        # Each tile: 256 MACs @ 2 GHz = 512 GOPs = 0.512 TOPS
        tops_per_tile = 0.512
        
        # Memory bottleneck factor (simplified)
        memory_factor = 1.0 - (0.01 / (1 + self.lookahead / 10))
        
        return self.compute_tiles * tops_per_tile * memory_factor
    
    def _calculate_area(self) -> float:
        """Calculate die area in mm²."""
        # SRAM: ~0.05 mm²/MB @ 3nm
        sram_area = self.sram_mb * 0.05
        
        # eDRAM: ~0.025 mm²/MB @ 3nm
        edram_area = self.edram_mb * 0.025
        
        # Compute: ~4.5 mm² per tile
        compute_area = self.compute_tiles * 4.5
        
        # Interconnect overhead: 10%
        total_area = (sram_area + edram_area + compute_area) * 1.1
        
        return total_area
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'sram_mb': self.sram_mb,
            'edram_mb': self.edram_mb,
            'lookahead': self.lookahead,
            'compute_tiles': self.compute_tiles,
            'power_w': self.power,
            'performance_tops': self.performance,
            'area_mm2': self.area,
            'efficiency_tops_per_watt': self.performance / self.power,
            'density_tops_per_mm2': self.performance / self.area
        }


def explore_design_space() -> List[DesignPoint]:
    """Explore the design space systematically."""
    print("\n" + "="*60)
    print("DESIGN SPACE EXPLORATION")
    print("="*60)
    
    design_points = []
    
    # Parameter ranges
    sram_sizes = [16, 24, 32, 40]  # MB
    edram_sizes = [192, 224, 256]  # MB
    lookaheads = [8, 12, 16, 20, 24]
    tile_counts = [12, 16, 20]
    
    total = len(sram_sizes) * len(edram_sizes) * len(lookaheads) * len(tile_counts)
    count = 0
    
    print(f"\nEvaluating {total} design points...")
    
    for sram in sram_sizes:
        for edram in edram_sizes:
            for lookahead in lookaheads:
                for tiles in tile_counts:
                    dp = DesignPoint(sram, edram, lookahead, tiles)
                    design_points.append(dp)
                    count += 1
                    
                    if count % 50 == 0:
                        print(f"Progress: {count}/{total} ({100*count/total:.1f}%)")
    
    print(f"\nCompleted evaluation of {len(design_points)} designs")
    return design_points


def find_pareto_frontier(designs: List[DesignPoint]) -> List[DesignPoint]:
    """Find Pareto-optimal designs (minimize power, maximize performance)."""
    print("\n" + "="*60)
    print("PARETO FRONTIER ANALYSIS")
    print("="*60)
    
    pareto_designs = []
    
    for candidate in designs:
        dominated = False
        
        for other in designs:
            # Check if 'other' dominates 'candidate'
            # (lower power AND higher performance)
            if (other.power <= candidate.power and 
                other.performance >= candidate.performance and
                (other.power < candidate.power or 
                 other.performance > candidate.performance)):
                dominated = True
                break
        
        if not dominated:
            pareto_designs.append(candidate)
    
    # Sort by performance
    pareto_designs.sort(key=lambda d: d.performance)
    
    print(f"\nFound {len(pareto_designs)} Pareto-optimal designs:")
    print("\n{:<8} {:<10} {:<12} {:<10}".format(
        "Power(W)", "Perf(TOPS)", "Efficiency", "Area(mm²)"))
    print("-" * 50)
    
    for design in pareto_designs[:5]:  # Show top 5
        eff = design.performance / design.power
        print(f"{design.power:<8.2f} {design.performance:<10.2f} "
              f"{eff:<12.2f} {design.area:<10.1f}")
    
    return pareto_designs


def sensitivity_analysis(baseline: DesignPoint) -> Dict:
    """Perform sensitivity analysis around baseline design."""
    print("\n" + "="*60)
    print("SENSITIVITY ANALYSIS")
    print("="*60)
    
    results = {}
    
    # Vary SRAM size ±25%
    print("\n1. SRAM Size Sensitivity:")
    sram_range = np.linspace(baseline.sram_mb * 0.75, 
                             baseline.sram_mb * 1.25, 5)
    sram_impact = []
    for sram in sram_range:
        dp = DesignPoint(sram, baseline.edram_mb, 
                        baseline.lookahead, baseline.compute_tiles)
        sram_impact.append(dp.power)
        print(f"  SRAM={sram:.0f}MB → Power={dp.power:.2f}W")
    results['sram'] = list(zip(sram_range, sram_impact))
    
    # Vary lookahead depth
    print("\n2. Lookahead Depth Sensitivity:")
    lookahead_range = range(4, 33, 4)
    lookahead_impact = []
    for la in lookahead_range:
        dp = DesignPoint(baseline.sram_mb, baseline.edram_mb, 
                        la, baseline.compute_tiles)
        lookahead_impact.append(dp.performance)
        print(f"  Lookahead={la} → Performance={dp.performance:.2f} TOPS")
    results['lookahead'] = list(zip(lookahead_range, lookahead_impact))
    
    # Vary tile count
    print("\n3. Compute Tile Count Sensitivity:")
    tile_range = range(8, 25, 2)
    tile_impact_power = []
    tile_impact_perf = []
    for tiles in tile_range:
        dp = DesignPoint(baseline.sram_mb, baseline.edram_mb, 
                        baseline.lookahead, tiles)
        tile_impact_power.append(dp.power)
        tile_impact_perf.append(dp.performance)
        print(f"  Tiles={tiles} → Power={dp.power:.2f}W, "
              f"Perf={dp.performance:.2f} TOPS")
    results['tiles'] = list(zip(tile_range, tile_impact_power, tile_impact_perf))
    
    return results


def visualize_results(designs: List[DesignPoint], 
                     pareto: List[DesignPoint],
                     sensitivity: Dict):
    """Create comprehensive visualization of results."""
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Power vs Performance scatter
    ax1 = plt.subplot(2, 3, 1)
    powers = [d.power for d in designs]
    perfs = [d.performance for d in designs]
    ax1.scatter(powers, perfs, alpha=0.3, s=20, label='All Designs')
    
    pareto_powers = [d.power for d in pareto]
    pareto_perfs = [d.performance for d in pareto]
    ax1.scatter(pareto_powers, pareto_perfs, color='red', s=50, 
               marker='*', label='Pareto Optimal', zorder=5)
    ax1.plot(pareto_powers, pareto_perfs, 'r--', alpha=0.5, linewidth=2)
    
    ax1.set_xlabel('Power (W)', fontsize=11)
    ax1.set_ylabel('Performance (TOPS)', fontsize=11)
    ax1.set_title('Power-Performance Trade-off', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Efficiency histogram
    ax2 = plt.subplot(2, 3, 2)
    efficiencies = [d.performance / d.power for d in designs]
    ax2.hist(efficiencies, bins=30, edgecolor='black', alpha=0.7)
    ax2.axvline(np.median(efficiencies), color='red', linestyle='--', 
               linewidth=2, label=f'Median: {np.median(efficiencies):.2f}')
    ax2.set_xlabel('Efficiency (TOPS/W)', fontsize=11)
    ax2.set_ylabel('Count', fontsize=11)
    ax2.set_title('Efficiency Distribution', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Area vs Performance
    ax3 = plt.subplot(2, 3, 3)
    areas = [d.area for d in designs]
    ax3.scatter(areas, perfs, alpha=0.3, s=20, c=powers, cmap='viridis')
    cbar = plt.colorbar(ax3.collections[0], ax=ax3)
    cbar.set_label('Power (W)', fontsize=10)
    ax3.set_xlabel('Die Area (mm²)', fontsize=11)
    ax3.set_ylabel('Performance (TOPS)', fontsize=11)
    ax3.set_title('Area vs Performance', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. SRAM sensitivity
    ax4 = plt.subplot(2, 3, 4)
    sram_vals, sram_powers = zip(*sensitivity['sram'])
    ax4.plot(sram_vals, sram_powers, marker='o', linewidth=2)
    ax4.set_xlabel('SRAM Size (MB)', fontsize=11)
    ax4.set_ylabel('Power (W)', fontsize=11)
    ax4.set_title('SRAM Size Sensitivity', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Lookahead sensitivity
    ax5 = plt.subplot(2, 3, 5)
    la_vals, la_perfs = zip(*sensitivity['lookahead'])
    ax5.plot(la_vals, la_perfs, marker='s', linewidth=2, color='green')
    ax5.set_xlabel('Lookahead Depth', fontsize=11)
    ax5.set_ylabel('Performance (TOPS)', fontsize=11)
    ax5.set_title('Lookahead Depth Sensitivity', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. Tile count sensitivity
    ax6 = plt.subplot(2, 3, 6)
    tile_data = sensitivity['tiles']
    tile_vals = [t[0] for t in tile_data]
    tile_powers = [t[1] for t in tile_data]
    tile_perfs = [t[2] for t in tile_data]
    
    ax6_twin = ax6.twinx()
    l1 = ax6.plot(tile_vals, tile_powers, marker='o', linewidth=2, 
                 color='red', label='Power')
    l2 = ax6_twin.plot(tile_vals, tile_perfs, marker='^', linewidth=2, 
                      color='blue', label='Performance')
    
    ax6.set_xlabel('Compute Tiles', fontsize=11)
    ax6.set_ylabel('Power (W)', fontsize=11, color='red')
    ax6_twin.set_ylabel('Performance (TOPS)', fontsize=11, color='blue')
    ax6.set_title('Compute Scaling', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # Combine legends
    lns = l1 + l2
    labs = [l.get_label() for l in lns]
    ax6.legend(lns, labs, loc='upper left')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('results/advanced_optimization')
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'optimization_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\nSaved figure to {output_dir / 'optimization_analysis.png'}")
    
    plt.close()


def export_results(designs: List[DesignPoint], pareto: List[DesignPoint]):
    """Export results to JSON for further analysis."""
    output_dir = Path('results/advanced_optimization')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export all designs
    all_designs = [d.to_dict() for d in designs]
    with open(output_dir / 'all_designs.json', 'w') as f:
        json.dump(all_designs, f, indent=2)
    
    # Export Pareto-optimal designs
    pareto_designs = [d.to_dict() for d in pareto]
    with open(output_dir / 'pareto_optimal.json', 'w') as f:
        json.dump(pareto_designs, f, indent=2)
    
    print(f"\nExported {len(designs)} designs to {output_dir}")
    print(f"Pareto-optimal designs: {len(pareto)}")


def main():
    """Main execution function."""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  Janus-1: Advanced Optimization Example".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Step 1: Explore design space
    designs = explore_design_space()
    
    # Step 2: Find Pareto frontier
    pareto = find_pareto_frontier(designs)
    
    # Step 3: Select baseline (middle of Pareto frontier)
    baseline_idx = len(pareto) // 2
    baseline = pareto[baseline_idx]
    
    print(f"\n" + "="*60)
    print("BASELINE DESIGN")
    print("="*60)
    print(f"SRAM: {baseline.sram_mb} MB")
    print(f"eDRAM: {baseline.edram_mb} MB")
    print(f"Lookahead: {baseline.lookahead}")
    print(f"Compute Tiles: {baseline.compute_tiles}")
    print(f"Power: {baseline.power:.2f} W")
    print(f"Performance: {baseline.performance:.2f} TOPS")
    print(f"Efficiency: {baseline.performance/baseline.power:.2f} TOPS/W")
    print(f"Area: {baseline.area:.1f} mm²")
    
    # Step 4: Sensitivity analysis
    sensitivity = sensitivity_analysis(baseline)
    
    # Step 5: Visualize
    visualize_results(designs, pareto, sensitivity)
    
    # Step 6: Export
    export_results(designs, pareto)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print(f"1. Explored {len(designs)} unique design configurations")
    print(f"2. Identified {len(pareto)} Pareto-optimal solutions")
    print(f"3. Best efficiency: {max(d.performance/d.power for d in designs):.2f} TOPS/W")
    print(f"4. Results saved to results/advanced_optimization/")
    print("\nNext steps:")
    print("- Review Pareto frontier for candidate designs")
    print("- Consider non-functional requirements (thermal, cost)")
    print("- Perform detailed RTL implementation of chosen design")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()