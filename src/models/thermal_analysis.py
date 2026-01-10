"""Thermal Analysis

First-order thermal modeling for junction temperature estimation.

Author: The Janus-1 Design Team
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class ThermalPackage:
    """Thermal package characteristics."""
    name: str
    theta_ja_c_per_w: float  # Junction-to-ambient thermal resistance
    description: str


class ThermalAnalyzer:
    """Estimate steady-state junction temperature.
    
    Uses the fundamental thermal equation:
    T_junction = T_ambient + (Power * Theta_JA)
    
    Example:
        >>> analyzer = ThermalAnalyzer(power_w=4.05, ambient_c=25)
        >>> result = analyzer.estimate(package='standard')
        >>> print(f"Junction temp: {result['t_junction_c']:.1f}°C")
    """
    
    # Typical package thermal resistances
    PACKAGES = {
        'standard': ThermalPackage(
            name='Standard Package',
            theta_ja_c_per_w=30.0,
            description='No heat sink, natural convection'
        ),
        'enhanced': ThermalPackage(
            name='Enhanced Package',
            theta_ja_c_per_w=20.0,
            description='Enhanced copper slug or spreader'
        ),
        'heatsink': ThermalPackage(
            name='With Heat Sink',
            theta_ja_c_per_w=10.0,
            description='10°C/W heat sink, forced air'
        ),
        'liquid': ThermalPackage(
            name='Liquid Cooling',
            theta_ja_c_per_w=5.0,
            description='Liquid cooling solution'
        )
    }
    
    def __init__(
        self, 
        power_w: float, 
        ambient_c: float = 25.0
    ):
        """Initialize thermal analyzer.
        
        Args:
            power_w: Total chip power dissipation in watts
            ambient_c: Ambient temperature in Celsius
        """
        self.power_w = power_w
        self.ambient_c = ambient_c
    
    def estimate(
        self, 
        package: str = 'standard',
        custom_theta_ja: float = None
    ) -> Dict:
        """Estimate junction temperature.
        
        Args:
            package: Package type ('standard', 'enhanced', 'heatsink', 'liquid')
            custom_theta_ja: Custom thermal resistance (overrides package)
        
        Returns:
            Dictionary with thermal analysis results
        """
        if custom_theta_ja is not None:
            theta_ja = custom_theta_ja
            package_name = 'Custom'
            description = f'{theta_ja}°C/W thermal resistance'
        elif package in self.PACKAGES:
            pkg = self.PACKAGES[package]
            theta_ja = pkg.theta_ja_c_per_w
            package_name = pkg.name
            description = pkg.description
        else:
            raise ValueError(f"Unknown package: {package}")
        
        # Calculate junction temperature
        temperature_rise_c = self.power_w * theta_ja
        t_junction_c = self.ambient_c + temperature_rise_c
        
        # Determine safety margin (typical max is 125°C)
        t_max_c = 125.0
        margin_c = t_max_c - t_junction_c
        
        return {
            'power_w': self.power_w,
            'ambient_c': self.ambient_c,
            'package': package_name,
            'description': description,
            'theta_ja_c_per_w': theta_ja,
            'temperature_rise_c': round(temperature_rise_c, 2),
            't_junction_c': round(t_junction_c, 2),
            't_max_c': t_max_c,
            'margin_c': round(margin_c, 2),
            'within_spec': t_junction_c < t_max_c
        }
    
    def compare_packages(self) -> Dict[str, Dict]:
        """Compare junction temperature across package options.
        
        Returns:
            Dictionary mapping package type to thermal results
        """
        return {
            pkg_key: self.estimate(package=pkg_key)
            for pkg_key in self.PACKAGES.keys()
        }
    
    def print_report(self, package: str = 'standard'):
        """Print formatted thermal report.
        
        Args:
            package: Package type
        """
        result = self.estimate(package)
        
        print(f"\n{'='*70}")
        print("Thermal Analysis")
        print(f"{'='*70}")
        print(f"\nPower Dissipation: {result['power_w']:.2f} W")
        print(f"Ambient Temperature: {result['ambient_c']:.1f}°C")
        print(f"\nPackage Configuration:")
        print(f"  Type: {result['package']}")
        print(f"  Description: {result['description']}")
        print(f"  Thermal Resistance (Θ_JA): {result['theta_ja_c_per_w']:.1f}°C/W")
        print(f"\nResults:")
        print(f"  Temperature Rise: {result['temperature_rise_c']:.1f}°C")
        print(f"  Junction Temperature: {result['t_junction_c']:.1f}°C")
        print(f"  Maximum Spec: {result['t_max_c']:.1f}°C")
        print(f"  Safety Margin: {result['margin_c']:.1f}°C")
        
        status = "✅ Within spec" if result['within_spec'] else "❌ Exceeds spec"
        print(f"\nStatus: {status}")
        print(f"\n{'='*70}\n")
    
    def print_comparison(self):
        """Print package comparison table."""
        results = self.compare_packages()
        
        print(f"\n{'='*70}")
        print(f"Package Thermal Comparison ({self.power_w:.2f}W @ {self.ambient_c}°C)")
        print(f"{'='*70}\n")
        print(f"{'Package':<20} {'Θ_JA (°C/W)':<15} {'T_j (°C)':<15} {'Margin (°C)':<15}")
        print(f"{'-'*65}")
        
        for pkg_key, result in results.items():
            print(f"{result['package']:<20} {result['theta_ja_c_per_w']:<15.1f} "
                  f"{result['t_junction_c']:<15.1f} {result['margin_c']:<15.1f}")
        
        print(f"\n{'='*70}\n")


if __name__ == "__main__":
    # Janus-1 thermal analysis
    analyzer = ThermalAnalyzer(power_w=4.05, ambient_c=25.0)
    
    # Standard package
    analyzer.print_report(package='standard')
    
    # Compare all options
    analyzer.print_comparison()
