"""Memory Technology Power Modeling

Compares power consumption of different memory technologies for the
Janus-1 Tier-2 cache.

Author: The Janus-1 Design Team
"""

import pandas as pd
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class TechnologyParams:
    """Memory technology parameters."""

    name: str
    read_energy_pj: float  # Picojoules per bit
    write_energy_pj: float
    static_power_per_mb_mw: float  # Milliwatts per MB
    latency_cycles: int


class MemoryPowerModel:
    """Model power consumption for different memory technologies.

    Estimates dynamic (read/write) and static (leakage) power for a given
    cache size and bandwidth.

    Example:
        >>> model = MemoryPowerModel(cache_size_mb=224, bandwidth_gb_s=20)
        >>> results = model.compare_technologies()
        >>> print(results.to_markdown())
    """

    # Technology parameters from literature (3nm node)
    TECHNOLOGIES = {
        "HD_SRAM": TechnologyParams(
            name="HD_SRAM",  # Fixed: Use key name for consistency
            read_energy_pj=0.05,
            write_energy_pj=0.05,
            static_power_per_mb_mw=80.0,
            latency_cycles=1,
        ),
        "eDRAM": TechnologyParams(
            name="eDRAM",
            read_energy_pj=0.15,
            write_energy_pj=0.15,
            static_power_per_mb_mw=5.0,
            latency_cycles=3,
        ),
        "STT_MRAM": TechnologyParams(
            name="STT-MRAM",
            read_energy_pj=0.20,
            write_energy_pj=0.50,
            static_power_per_mb_mw=0.1,
            latency_cycles=5,
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

        return {
            "technology": tech.name,
            "dynamic_w": round(dynamic_power_w, 3),
            "static_w": round(static_power_w, 3),
            "total_w": round(total_power_w, 3),
            "latency_cycles": tech.latency_cycles,
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
        print(
            f"  Savings vs {worst['technology']}: "
            f"{worst['total_w'] / best['total_w']:.1f}x\n"
        )


if __name__ == "__main__":
    # Janus-1 T2 cache analysis
    model = MemoryPowerModel(
        cache_size_mb=224,
        bandwidth_gb_s=20,
        technology="eDRAM",
        read_ratio=0.90,
        write_ratio=0.10,
    )

    model.print_comparison()
