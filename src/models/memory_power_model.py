"""Memory Technology Power Modeling

Compares power consumption of different memory technologies for the
Janus-1 Tier-2 cache with enhanced area modeling and analysis.

Author: The Janus-1 Design Team
License: MIT
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TechnologyParams:
    """Memory technology parameters."""

    name: str
    read_energy_pj: float  # Picojoules per bit
    write_energy_pj: float
    static_power_per_mb_mw: float  # Milliwatts per MB
    latency_cycles: int
    # Area model (3nm GAA process)
    area_per_mbit_mm2: float  # mm² per Mbit


class MemoryPowerModel:
    """Model power consumption for different memory technologies.

    Estimates dynamic (read/write) and static (leakage) power for a given
    cache size and bandwidth, along with area estimation.

    Example:
        >>> model = MemoryPowerModel(cache_size_mb=224, bandwidth_gb_s=20)
        >>> results = model.compare_technologies()
        >>> print(results.to_markdown())
    """

    # Technology parameters from literature (3nm node)
    TECHNOLOGIES = {
        "HD_SRAM": TechnologyParams(
            name="HD_SRAM",
            read_energy_pj=0.05,
            write_energy_pj=0.05,
            static_power_per_mb_mw=80.0,  # High leakage
            latency_cycles=1,
            area_per_mbit_mm2=0.03,  # Dense but still large
        ),
        "eDRAM": TechnologyParams(
            name="eDRAM",
            read_energy_pj=0.15,
            write_energy_pj=0.15,
            static_power_per_mb_mw=5.0,  # Low leakage + refresh
            latency_cycles=3,
            area_per_mbit_mm2=0.01,  # Very dense
        ),
        "STT_MRAM": TechnologyParams(
            name="STT-MRAM",
            read_energy_pj=0.20,
            write_energy_pj=0.50,  # High write energy
            static_power_per_mb_mw=0.1,  # Near-zero leakage
            latency_cycles=5,
            area_per_mbit_mm2=0.015,  # Moderate density
        ),
    }

    def __init__(
        self,
        cache_size_mb: float,
        bandwidth_gb_s: float,
        technology: str = "eDRAM",
        read_ratio: float = 0.90,
        write_ratio: float = 0.10,
    ):
        """Initialize power model.

        Args:
            cache_size_mb: Total cache capacity in megabytes
            bandwidth_gb_s: Sustained memory bandwidth in GB/s
            technology: Technology to model ('HD_SRAM', 'eDRAM', 'STT_MRAM')
            read_ratio: Fraction of operations that are reads
            write_ratio: Fraction of operations that are writes
        """
        self.cache_size_mb = cache_size_mb
        self.bandwidth_gb_s = bandwidth_gb_s
        self.technology = technology
        self.read_ratio = read_ratio
        self.write_ratio = write_ratio

        # Convert to bits per second
        self.bandwidth_bits_s = bandwidth_gb_s * 8 * 1024 * 1024 * 1024
        self.read_bw_bits_s = self.bandwidth_bits_s * read_ratio
        self.write_bw_bits_s = self.bandwidth_bits_s * write_ratio

    def calculate_power(self, tech: TechnologyParams) -> Dict:
        """Calculate power for a specific technology.

        Args:
            tech: Technology parameters

        Returns:
            Dictionary with power breakdown
        """
        # Dynamic power: energy per bit * bits per second
        read_power_w = self.read_bw_bits_s * tech.read_energy_pj * 1e-12
        write_power_w = self.write_bw_bits_s * tech.write_energy_pj * 1e-12
        dynamic_power_w = read_power_w + write_power_w

        # Static power: leakage per MB * total MB
        static_power_w = self.cache_size_mb * tech.static_power_per_mb_mw / 1000

        total_power_w = dynamic_power_w + static_power_w

        # Area calculation: Mbit to MB conversion
        cache_size_mbit = self.cache_size_mb * 8
        area_mm2 = cache_size_mbit * tech.area_per_mbit_mm2

        return {
            "technology": tech.name,
            "dynamic_w": round(dynamic_power_w, 3),
            "static_w": round(static_power_w, 3),
            "total_w": round(total_power_w, 3),
            "area_mm2": round(area_mm2, 2),
            "latency_cycles": tech.latency_cycles,
            "read_latency_ns": round(tech.latency_cycles * 1.0, 1),  # @ 1GHz
            "mb_per_w": round(self.cache_size_mb / total_power_w, 1),
            "area_efficiency": round(self.cache_size_mb / area_mm2, 2),  # MB/mm²
        }

    def estimate_power(self) -> Dict:
        """Estimate power for the configured technology.

        Returns:
            Dictionary with power breakdown for selected technology
        """
        tech_params = self.TECHNOLOGIES[self.technology]
        return self.calculate_power(tech_params)

    def compare_technologies(self) -> pd.DataFrame:
        """Compare all supported technologies.

        Returns:
            DataFrame with power comparison
        """
        results = []
        for tech_key, tech_params in self.TECHNOLOGIES.items():
            power_data = self.calculate_power(tech_params)
            results.append(power_data)

        df = pd.DataFrame(results)
        df = df.sort_values("total_w")
        return df

    def calculate_memory_power(
        self, size_mb: float, technology: str, frequency_mhz: float = 1000
    ) -> Dict:
        """Helper method for calculating memory power at specific frequency.

        This method maintains API compatibility with older code.

        Args:
            size_mb: Memory size in MB
            technology: Technology type
            frequency_mhz: Operating frequency in MHz

        Returns:
            Dictionary with power and area metrics
        """
        tech_params = self.TECHNOLOGIES[technology]

        # Scale bandwidth proportionally with frequency (for dynamic power)
        freq_scale = frequency_mhz / 1000  # Relative to 1 GHz baseline
        scaled_bw = self.bandwidth_gb_s * freq_scale

        # Create temporary model with scaled parameters
        temp_bw_bits_s = scaled_bw * 8 * 1024 * 1024 * 1024
        read_bw_bits_s = temp_bw_bits_s * self.read_ratio
        write_bw_bits_s = temp_bw_bits_s * self.write_ratio

        # Calculate powers
        read_power_w = read_bw_bits_s * tech_params.read_energy_pj * 1e-12
        write_power_w = write_bw_bits_s * tech_params.write_energy_pj * 1e-12
        dynamic_power_w = read_power_w + write_power_w
        static_power_w = size_mb * tech_params.static_power_per_mb_mw / 1000
        total_power_w = dynamic_power_w + static_power_w

        # Area
        cache_size_mbit = size_mb * 8
        area_mm2 = cache_size_mbit * tech_params.area_per_mbit_mm2

        # Latency (scaled with frequency)
        latency_ns = (tech_params.latency_cycles / frequency_mhz) * 1000

        return {
            "dynamic_power_w": dynamic_power_w,
            "static_power_w": static_power_w,
            "total_power_w": total_power_w,
            "area_mm2": area_mm2,
            "read_latency_ns": latency_ns,
            "latency_cycles": tech_params.latency_cycles,
            "mb_per_w": size_mb / total_power_w if total_power_w > 0 else 0,
        }

    def print_comparison(self):
        """Print formatted technology comparison."""
        df = self.compare_technologies()

        print(f"\n{'='*70}")
        print(f"Memory Technology Power Analysis")
        print(f"{'='*70}")
        print(f"\nConfiguration:")
        print(f"  Cache Size: {self.cache_size_mb} MB")
        print(f"  Bandwidth: {self.bandwidth_gb_s} GB/s")
        print(
            f"  Read/Write Ratio: {self.read_ratio:.0%}/{self.write_ratio:.0%}"
        )
        print(f"\nPower Comparison:\n")
        print(df.to_string(index=False))
        print(f"\n{'='*70}\n")

        # Highlight winner
        best = df.iloc[0]
        worst = df.iloc[-1]
        print(f"Winner: {best['technology']}")
        print(f"  Total Power: {best['total_w']:.2f} W")
        print(f"  Area: {best['area_mm2']:.2f} mm²")
        print(f"  Efficiency: {best['mb_per_w']:.1f} MB/W")
        print(
            f"  Power Savings vs {worst['technology']}: "
            f"{worst['total_w'] / best['total_w']:.1f}x\n"
        )

    def sensitivity_analysis(
        self, param: str, values: List[float]
    ) -> pd.DataFrame:
        """Perform sensitivity analysis on a parameter.

        Args:
            param: Parameter to vary ('cache_size_mb' or 'bandwidth_gb_s')
            values: List of values to test

        Returns:
            DataFrame with results for each value
        """
        results = []
        for value in values:
            if param == "cache_size_mb":
                model = MemoryPowerModel(
                    cache_size_mb=value,
                    bandwidth_gb_s=self.bandwidth_gb_s,
                    technology=self.technology,
                )
            elif param == "bandwidth_gb_s":
                model = MemoryPowerModel(
                    cache_size_mb=self.cache_size_mb,
                    bandwidth_gb_s=value,
                    technology=self.technology,
                )
            else:
                raise ValueError(f"Unknown parameter: {param}")

            power_data = model.estimate_power()
            power_data[param] = value
            results.append(power_data)

        return pd.DataFrame(results)

    @staticmethod
    def get_optimal_technology(
        cache_size_mb: float,
        bandwidth_gb_s: float,
        optimize_for: str = "power",
    ) -> Tuple[str, Dict]:
        """Find optimal technology for given constraints.

        Args:
            cache_size_mb: Memory size requirement
            bandwidth_gb_s: Bandwidth requirement
            optimize_for: Optimization criterion ('power', 'area', 'efficiency')

        Returns:
            Tuple of (technology_name, metrics_dict)
        """
        model = MemoryPowerModel(cache_size_mb, bandwidth_gb_s)
        df = model.compare_technologies()

        if optimize_for == "power":
            best_idx = df["total_w"].idxmin()
        elif optimize_for == "area":
            best_idx = df["area_mm2"].idxmin()
        elif optimize_for == "efficiency":
            best_idx = df["mb_per_w"].idxmax()
        else:
            raise ValueError(f"Unknown optimization criterion: {optimize_for}")

        best_row = df.loc[best_idx]
        return best_row["technology"], best_row.to_dict()


if __name__ == "__main__":
    # Janus-1 T2 cache analysis
    print("\n" + "="*70)
    print("JANUS-1 TIER-2 CACHE TECHNOLOGY ANALYSIS")
    print("="*70)

    model = MemoryPowerModel(
        cache_size_mb=224,
        bandwidth_gb_s=20,
        technology="eDRAM",
        read_ratio=0.90,
        write_ratio=0.10,
    )

    model.print_comparison()

    # Sensitivity analysis
    print("\nSensitivity Analysis: Cache Size")
    print("=" * 70)
    sizes = [64, 128, 224, 256, 512]
    sens_df = model.sensitivity_analysis("cache_size_mb", sizes)
    print(sens_df[['cache_size_mb', 'total_w', 'area_mm2', 'mb_per_w']].to_string(index=False))

    # Optimal technology
    print("\n" + "="*70)
    tech_name, metrics = MemoryPowerModel.get_optimal_technology(
        cache_size_mb=224, bandwidth_gb_s=20, optimize_for="efficiency"
    )
    print(f"Optimal Technology (for efficiency): {tech_name}")
    print(f"  Power: {metrics['total_w']:.2f} W")
    print(f"  Area: {metrics['area_mm2']:.2f} mm²")
    print(f"  Efficiency: {metrics['mb_per_w']:.1f} MB/W")
    print("="*70 + "\n")
