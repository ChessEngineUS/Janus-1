"""SRAM Area Estimation

Estimates silicon area for on-chip SRAM at different process nodes.

Author: The Janus-1 Design Team
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class ProcessNode:
    """Process technology node parameters."""

    node_nm: int
    sram_bit_cell_area_um2: float  # Area per SRAM bit cell in um^2
    periphery_overhead: float  # Overhead for decoders, sense amps, etc.


class SRAMAreaModel:
    """Estimate SRAM area for different process nodes.

    Uses empirical bit cell densities from industry data.

    Example:
        >>> model = SRAMAreaModel(cache_size_mb=32, process_node_nm=3)
        >>> area = model.estimate_area()
        >>> print(f"Area: {area['total_mm2']:.2f} mm^2")
    """

    # Industry-standard SRAM bit cell areas (um^2 per bit)
    PROCESS_NODES = {
        3: ProcessNode(
            node_nm=3, sram_bit_cell_area_um2=0.012, periphery_overhead=1.15
        ),
        5: ProcessNode(
            node_nm=5, sram_bit_cell_area_um2=0.020, periphery_overhead=1.15
        ),
        7: ProcessNode(
            node_nm=7, sram_bit_cell_area_um2=0.030, periphery_overhead=1.15
        ),
        10: ProcessNode(
            node_nm=10, sram_bit_cell_area_um2=0.055, periphery_overhead=1.20
        ),
    }

    def __init__(self, cache_size_mb: float, process_node_nm: int = 3):
        """Initialize area model.

        Args:
            cache_size_mb: Cache capacity in megabytes
            process_node_nm: Process node (3, 5, 7, or 10 nm)
        """
        self.cache_size_mb = cache_size_mb
        self.process_node_nm = process_node_nm

        if process_node_nm not in self.PROCESS_NODES:
            raise ValueError(
                f"Unsupported process node: {process_node_nm}nm. "
                f"Supported: {list(self.PROCESS_NODES.keys())}"
            )

        self.process = self.PROCESS_NODES[process_node_nm]

    def estimate_area(self) -> Dict:
        """Estimate SRAM area.

        Returns:
            Dictionary with area breakdown
        """
        # Convert MB to bits
        total_bits = self.cache_size_mb * 8 * 1024 * 1024

        # Calculate bit cell array area
        bit_cell_area_um2 = total_bits * self.process.sram_bit_cell_area_um2

        # Add periphery overhead
        total_area_um2 = bit_cell_area_um2 * self.process.periphery_overhead

        # Convert to mm^2
        total_area_mm2 = total_area_um2 / (1000 * 1000)

        return {
            "cache_size_mb": self.cache_size_mb,
            "process_node_nm": self.process_node_nm,
            "bit_cell_area_um2_per_bit": self.process.sram_bit_cell_area_um2,
            "total_bits": total_bits,
            "bit_cell_array_mm2": bit_cell_area_um2 / (1000 * 1000),
            "periphery_overhead": self.process.periphery_overhead,
            "total_mm2": round(total_area_mm2, 2),
        }

    def compare_process_nodes(self) -> Dict[int, float]:
        """Compare area across different process nodes.

        Returns:
            Dictionary mapping process node to area in mm^2
        """
        results = {}
        for node_nm in self.PROCESS_NODES.keys():
            model = SRAMAreaModel(
                cache_size_mb=self.cache_size_mb, process_node_nm=node_nm
            )
            results[node_nm] = model.estimate_area()["total_mm2"]
        return results

    def print_report(self):
        """Print formatted area report."""
        area_data = self.estimate_area()

        print(f"\n{'='*70}")
        print("SRAM Area Analysis")
        print(f"{'='*70}")
        print(f"\nConfiguration:")
        print(f"  Cache Size: {self.cache_size_mb} MB")
        print(f"  Process Node: {self.process_node_nm} nm")
        print(
            f"  Bit Cell Area: {area_data['bit_cell_area_um2_per_bit']:.3f} µm²/bit"
        )
        print(f"\nArea Breakdown:")
        print(f"  Bit Cell Array: {area_data['bit_cell_array_mm2']:.2f} mm²")
        print(
            f"  Periphery Overhead: {(area_data['periphery_overhead'] - 1) * 100:.0f}%"
        )
        print(f"  Total Area: {area_data['total_mm2']:.2f} mm²")
        print(f"\n{'='*70}\n")

    def print_comparison(self):
        """Print process node comparison."""
        comparison = self.compare_process_nodes()

        print(f"\n{'='*70}")
        print(f"Process Node Comparison ({self.cache_size_mb} MB SRAM)")
        print(f"{'='*70}\n")
        print(f"{'Process Node':<20} {'Area (mm²)':<15}")
        print(f"{'-'*35}")

        for node_nm, area_mm2 in sorted(comparison.items()):
            print(f"{node_nm} nm{' '*16} {area_mm2:<15.2f}")

        print(f"\n{'='*70}\n")


def estimate_sram_area(cache_size_mb: float, process_node_nm: int = 3) -> float:
    """Standalone function to estimate SRAM area.

    Args:
        cache_size_mb: Cache capacity in megabytes
        process_node_nm: Process node (3, 5, 7, or 10 nm)

    Returns:
        Total SRAM area in mm^2
    """
    model = SRAMAreaModel(cache_size_mb, process_node_nm)
    return model.estimate_area()["total_mm2"]


if __name__ == "__main__":
    # Janus-1 T1 SRAM area analysis
    model = SRAMAreaModel(cache_size_mb=32, process_node_nm=3)
    model.print_report()
    model.print_comparison()
