"""SRAM Area Estimation

Calculates physical die area for SRAM memory arrays.

Author: The Janus-1 Design Team
"""

from typing import Dict


class SRAMAreaModel:
    """Estimate SRAM macro area for different configurations.
    
    Models bit cell area plus overhead for decoders, sense amplifiers,
    and routing.
    
    Example:
        >>> model = SRAMAreaModel()
        >>> area = model.estimate(cache_size_mb=32, process_nm=3)
        >>> print(f"Total area: {area['total_mm2']:.2f} mm²")
    """
    
    # Bit cell area (um^2) by process node
    BIT_CELL_AREA = {
        3: 0.021,   # 3nm GAA
        5: 0.035,   # 5nm
        7: 0.055,   # 7nm
        10: 0.080,  # 10nm
        16: 0.150   # 16nm
    }
    
    def __init__(self, efficiency: float = 0.65):
        """Initialize area model.
        
        Args:
            efficiency: Array efficiency (bit cells / total area).
                       Typical values: 0.60-0.70
        """
        self.efficiency = efficiency
    
    def estimate(
        self, 
        cache_size_mb: float, 
        process_nm: int = 3
    ) -> Dict:
        """Estimate SRAM macro area.
        
        Args:
            cache_size_mb: Cache capacity in megabytes
            process_nm: Process node (3, 5, 7, 10, or 16 nm)
        
        Returns:
            Dictionary with area breakdown
        """
        if process_nm not in self.BIT_CELL_AREA:
            raise ValueError(f"Unsupported process node: {process_nm}nm")
        
        bit_cell_area_um2 = self.BIT_CELL_AREA[process_nm]
        
        # Calculate total bits
        total_bits = cache_size_mb * 1024 * 1024 * 8
        
        # Bit cell area
        bit_cell_total_um2 = total_bits * bit_cell_area_um2
        bit_cell_total_mm2 = bit_cell_total_um2 / 1e6
        
        # Add overhead for periphery
        overhead_factor = 1 / self.efficiency
        total_macro_mm2 = bit_cell_total_mm2 * overhead_factor
        
        return {
            'cache_size_mb': cache_size_mb,
            'process_nm': process_nm,
            'total_bits': total_bits,
            'bit_cell_area_um2': bit_cell_area_um2,
            'bit_cell_total_mm2': round(bit_cell_total_mm2, 2),
            'overhead_factor': overhead_factor,
            'efficiency': self.efficiency,
            'total_mm2': round(total_macro_mm2, 2)
        }
    
    def compare_process_nodes(
        self, 
        cache_size_mb: float
    ) -> Dict[int, Dict]:
        """Compare area across process nodes.
        
        Args:
            cache_size_mb: Cache capacity
        
        Returns:
            Dictionary mapping process node to area info
        """
        return {
            node: self.estimate(cache_size_mb, node)
            for node in self.BIT_CELL_AREA.keys()
        }
    
    def print_report(self, cache_size_mb: float, process_nm: int = 3):
        """Print formatted area report.
        
        Args:
            cache_size_mb: Cache capacity
            process_nm: Process node
        """
        result = self.estimate(cache_size_mb, process_nm)
        
        print(f"\n{'='*60}")
        print("SRAM Area Estimation")
        print(f"{'='*60}")
        print(f"\nConfiguration:")
        print(f"  Cache Size: {result['cache_size_mb']} MB")
        print(f"  Process: {result['process_nm']}nm")
        print(f"  Bit Cell Area: {result['bit_cell_area_um2']} µm²")
        print(f"  Array Efficiency: {result['efficiency']:.0%}")
        print(f"\nArea Breakdown:")
        print(f"  Bit Cells Only: {result['bit_cell_total_mm2']:.2f} mm²")
        print(f"  Overhead Factor: {result['overhead_factor']:.2f}x")
        print(f"  Total Macro Area: {result['total_mm2']:.2f} mm²")
        print(f"\n{'='*60}\n")
    
    def print_comparison(self, cache_size_mb: float):
        """Print process node comparison.
        
        Args:
            cache_size_mb: Cache capacity
        """
        results = self.compare_process_nodes(cache_size_mb)
        
        print(f"\n{'='*60}")
        print(f"SRAM Area vs Process Node ({cache_size_mb} MB Cache)")
        print(f"{'='*60}\n")
        print(f"{'Process':<10} {'Bit Cell (µm²)':<15} {'Total Area (mm²)':<20}")
        print(f"{'-'*50}")
        
        for node in sorted(results.keys()):
            info = results[node]
            print(f"{node}nm{'':<6} {info['bit_cell_area_um2']:<15.3f} "
                  f"{info['total_mm2']:<20.2f}")
        
        print(f"\n{'='*60}\n")


def estimate_sram_area(
    cache_size_mb: float,
    process_node_nm: int = 3,
    efficiency: float = 0.65
) -> float:
    """Convenience function to estimate SRAM area.
    
    Args:
        cache_size_mb: Cache capacity in megabytes
        process_node_nm: Process technology node in nanometers
        efficiency: Array efficiency (0.0-1.0)
    
    Returns:
        Total SRAM area in mm²
    """
    model = SRAMAreaModel(efficiency=efficiency)
    result = model.estimate(cache_size_mb, process_node_nm)
    return result['total_mm2']


if __name__ == "__main__":
    model = SRAMAreaModel(efficiency=0.65)
    
    # Janus-1 T1 cache (32 MB SRAM)
    model.print_report(cache_size_mb=32, process_nm=3)
    
    # Show scaling across nodes
    model.print_comparison(cache_size_mb=32)
