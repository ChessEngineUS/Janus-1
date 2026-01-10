"""Sensitivity Analysis and Parameter Sweep Framework

Performs systematic sensitivity analysis to understand how simulation
results vary with input parameters, identifying critical design variables.

Author: The Janus-1 Design Team
License: MIT
"""

import numpy as np
from typing import Dict, List, Tuple, Callable, Any
from dataclasses import dataclass, field
import itertools
from scipy.stats import spearmanr, pearsonr


@dataclass
class SensitivityResult:
    """Results from sensitivity analysis."""
    
    parameter_name: str
    values_tested: List[float]
    output_values: List[float]
    baseline_value: float
    baseline_output: float
    correlation: float
    correlation_p_value: float
    relative_sensitivity: float  # % change in output / % change in input
    
    def is_sensitive(self, threshold: float = 0.1) -> bool:
        """Check if parameter has significant sensitivity.
        
        Args:
            threshold: Minimum abs(relative_sensitivity) to be considered sensitive
            
        Returns:
            True if parameter is sensitive
        """
        return abs(self.relative_sensitivity) > threshold


@dataclass
class MultiParameterSensitivity:
    """Results from multi-parameter sensitivity analysis."""
    
    parameter_names: List[str]
    baseline_params: Dict[str, float]
    baseline_output: float
    single_param_results: List[SensitivityResult] = field(default_factory=list)
    interaction_effects: Dict[Tuple[str, str], float] = field(default_factory=dict)
    sobol_indices: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def rank_parameters(self) -> List[Tuple[str, float]]:
        """Rank parameters by sensitivity.
        
        Returns:
            List of (parameter_name, sensitivity) sorted by importance
        """
        ranked = [
            (result.parameter_name, abs(result.relative_sensitivity))
            for result in self.single_param_results
        ]
        return sorted(ranked, key=lambda x: x[1], reverse=True)


class SensitivityAnalyzer:
    """Perform systematic sensitivity analysis on simulation parameters.
    
    Implements several sensitivity analysis methods:
    1. One-at-a-time (OAT) parameter sweeps
    2. Correlation-based sensitivity
    3. Variance-based sensitivity (Sobol indices)
    4. Interaction effect detection
    
    References:
        [1] Saltelli et al. "Global Sensitivity Analysis: The Primer." Wiley, 2008.
        [2] Iooss & Lemaitre. "A review on global sensitivity analysis methods."
            Operations Research Perspectives, 2015.
    """
    
    def __init__(self, model_function: Callable, parameter_space: Dict[str, Tuple]):
        """Initialize sensitivity analyzer.
        
        Args:
            model_function: Function that takes parameters and returns metric
            parameter_space: Dict of {param_name: (min, max, baseline)} tuples
        """
        self.model_function = model_function
        self.parameter_space = parameter_space
        self.baseline_params = {name: vals[2] for name, vals in parameter_space.items()}
    
    def one_at_a_time_analysis(
        self,
        n_points: int = 10,
        use_log_scale: bool = False
    ) -> MultiParameterSensitivity:
        """Perform one-at-a-time (OAT) sensitivity analysis.
        
        Varies each parameter independently while holding others constant.
        
        Args:
            n_points: Number of points to sample for each parameter
            use_log_scale: Use logarithmic spacing for parameters
            
        Returns:
            MultiParameterSensitivity object with results
        """
        # Compute baseline
        baseline_output = self.model_function(**self.baseline_params)
        
        results = []
        
        for param_name, (min_val, max_val, baseline_val) in self.parameter_space.items():
            # Generate test values
            if use_log_scale and min_val > 0:
                values = np.logspace(np.log10(min_val), np.log10(max_val), n_points)
            else:
                values = np.linspace(min_val, max_val, n_points)
            
            outputs = []
            for val in values:
                # Set current parameter, keep others at baseline
                params = self.baseline_params.copy()
                params[param_name] = val
                outputs.append(self.model_function(**params))
            
            # Compute correlation
            corr, p_value = spearmanr(values, outputs)
            
            # Compute relative sensitivity
            # (% change in output) / (% change in input)
            idx_baseline = np.argmin(np.abs(values - baseline_val))
            if idx_baseline < len(values) - 1:
                next_idx = idx_baseline + 1
            else:
                next_idx = idx_baseline - 1
            
            delta_input = (values[next_idx] - values[idx_baseline]) / values[idx_baseline]
            delta_output = (outputs[next_idx] - outputs[idx_baseline]) / outputs[idx_baseline]
            
            if delta_input != 0:
                rel_sensitivity = delta_output / delta_input
            else:
                rel_sensitivity = 0.0
            
            results.append(SensitivityResult(
                parameter_name=param_name,
                values_tested=values.tolist(),
                output_values=outputs,
                baseline_value=baseline_val,
                baseline_output=baseline_output,
                correlation=corr,
                correlation_p_value=p_value,
                relative_sensitivity=rel_sensitivity
            ))
        
        return MultiParameterSensitivity(
            parameter_names=list(self.parameter_space.keys()),
            baseline_params=self.baseline_params,
            baseline_output=baseline_output,
            single_param_results=results
        )
    
    def interaction_analysis(
        self,
        param_pairs: List[Tuple[str, str]] = None,
        n_points: int = 5
    ) -> Dict[Tuple[str, str], float]:
        """Analyze interaction effects between parameter pairs.
        
        Args:
            param_pairs: List of parameter pairs to test, or None for all pairs
            n_points: Number of points to test per parameter
            
        Returns:
            Dictionary of {(param1, param2): interaction_strength}
        """
        if param_pairs is None:
            # Generate all unique pairs
            params = list(self.parameter_space.keys())
            param_pairs = list(itertools.combinations(params, 2))
        
        interactions = {}
        
        for param1, param2 in param_pairs:
            min1, max1, _ = self.parameter_space[param1]
            min2, max2, _ = self.parameter_space[param2]
            
            values1 = np.linspace(min1, max1, n_points)
            values2 = np.linspace(min2, max2, n_points)
            
            # Compute grid of outputs
            outputs = np.zeros((n_points, n_points))
            for i, v1 in enumerate(values1):
                for j, v2 in enumerate(values2):
                    params = self.baseline_params.copy()
                    params[param1] = v1
                    params[param2] = v2
                    outputs[i, j] = self.model_function(**params)
            
            # Measure interaction as deviation from additivity
            # If additive: f(x,y) = f(x,baseline) + f(baseline,y) - f(baseline,baseline)
            baseline_output = self.model_function(**self.baseline_params)
            
            interaction_strength = 0.0
            count = 0
            for i in range(n_points):
                for j in range(n_points):
                    params1 = self.baseline_params.copy()
                    params1[param1] = values1[i]
                    f_x = self.model_function(**params1)
                    
                    params2 = self.baseline_params.copy()
                    params2[param2] = values2[j]
                    f_y = self.model_function(**params2)
                    
                    expected_additive = f_x + f_y - baseline_output
                    actual = outputs[i, j]
                    
                    if expected_additive != 0:
                        interaction_strength += abs((actual - expected_additive) / expected_additive)
                        count += 1
            
            interactions[(param1, param2)] = interaction_strength / count if count > 0 else 0.0
        
        return interactions
    
    def monte_carlo_sensitivity(
        self,
        n_samples: int = 10000,
        seed: int = None
    ) -> Dict[str, float]:
        """Perform Monte Carlo-based global sensitivity analysis.
        
        Uses variance decomposition to estimate sensitivity indices.
        
        Args:
            n_samples: Number of Monte Carlo samples
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary of {parameter: sensitivity_index}
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Generate random samples from parameter space
        samples = {}
        for param_name, (min_val, max_val, _) in self.parameter_space.items():
            samples[param_name] = np.random.uniform(min_val, max_val, n_samples)
        
        # Evaluate model at all samples
        outputs = np.array([
            self.model_function(**{k: v[i] for k, v in samples.items()})
            for i in range(n_samples)
        ])
        
        # Compute total variance
        total_var = np.var(outputs)
        
        if total_var == 0:
            return {param: 0.0 for param in self.parameter_space.keys()}
        
        # Compute first-order sensitivity indices using correlation
        sensitivity_indices = {}
        for param_name in self.parameter_space.keys():
            # Compute correlation between parameter and output
            corr, _ = pearsonr(samples[param_name], outputs)
            # Square to get proportion of variance explained
            sensitivity_indices[param_name] = corr ** 2
        
        return sensitivity_indices
    
    def generate_report(self, results: MultiParameterSensitivity) -> str:
        """Generate comprehensive sensitivity analysis report.
        
        Args:
            results: MultiParameterSensitivity object
            
        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 80)
        report.append("SENSITIVITY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        report.append("Baseline Configuration:")
        for param, value in results.baseline_params.items():
            report.append(f"  {param:30s}: {value}")
        report.append(f"\n  Baseline Output: {results.baseline_output:.6f}")
        report.append("")
        report.append("Parameter Sensitivity Ranking:")
        report.append(f"{'Rank':<6}{'Parameter':<30}{'Rel. Sensitivity':<20}{'Classification'}")
        report.append("-" * 80)
        
        ranked = results.rank_parameters()
        for rank, (param, sensitivity) in enumerate(ranked, 1):
            if sensitivity > 1.0:
                classification = "HIGHLY SENSITIVE"
            elif sensitivity > 0.1:
                classification = "MODERATELY SENSITIVE"
            else:
                classification = "LOW SENSITIVITY"
            
            report.append(f"{rank:<6}{param:<30}{sensitivity:<20.4f}{classification}")
        
        report.append("")
        report.append("Detailed Parameter Analysis:")
        report.append("=" * 80)
        
        for result in results.single_param_results:
            report.append(f"\nParameter: {result.parameter_name}")
            report.append(f"  Baseline Value: {result.baseline_value:.4f}")
            report.append(f"  Range Tested: [{min(result.values_tested):.4f}, {max(result.values_tested):.4f}]")
            report.append(f"  Output Range: [{min(result.output_values):.4f}, {max(result.output_values):.4f}]")
            report.append(f"  Correlation (Spearman): {result.correlation:.4f} (p={result.correlation_p_value:.4e})")
            report.append(f"  Relative Sensitivity: {result.relative_sensitivity:.4f}")
            
            if abs(result.correlation) > 0.7:
                direction = "positive" if result.correlation > 0 else "negative"
                report.append(f"  → Strong {direction} correlation")
        
        report.append("")
        report.append("=" * 80)
        report.append("")
        report.append("Recommendations:")
        report.append("  1. Focus optimization efforts on highly sensitive parameters")
        report.append("  2. Tight tolerances needed for sensitive parameters in fabrication")
        report.append("  3. Low sensitivity parameters offer design flexibility")
        report.append("")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    print("Sensitivity Analysis Example\n")
    
    # Define a simple test function (quadratic with interaction)
    def test_function(x1, x2, x3):
        return 2*x1**2 + 0.5*x2 + 0.1*x3 + 0.3*x1*x2
    
    # Define parameter space
    param_space = {
        'x1': (0, 10, 5),    # (min, max, baseline)
        'x2': (0, 20, 10),
        'x3': (0, 100, 50)
    }
    
    # Create analyzer
    analyzer = SensitivityAnalyzer(test_function, param_space)
    
    # Perform OAT analysis
    results = analyzer.one_at_a_time_analysis(n_points=20)
    
    # Print report
    print(analyzer.generate_report(results))
    
    # Interaction analysis
    print("\nInteraction Effects:")
    interactions = analyzer.interaction_analysis([('x1', 'x2'), ('x1', 'x3'), ('x2', 'x3')])
    for pair, strength in interactions.items():
        print(f"  {pair[0]} × {pair[1]}: {strength:.4f}")
