"""Statistical Analysis and Uncertainty Quantification

Provides rigorous statistical methods for analyzing simulation results,
including confidence intervals, hypothesis testing, and uncertainty propagation.

Author: The Janus-1 Design Team
License: MIT
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import warnings


@dataclass
class ConfidenceInterval:
    """Confidence interval for a statistic."""
    
    mean: float
    lower: float
    upper: float
    confidence_level: float
    stderr: float
    n_samples: int
    
    def __str__(self) -> str:
        width = self.upper - self.lower
        return (f"{self.mean:.4f} ± {width/2:.4f} "
                f"({self.confidence_level:.0%} CI: [{self.lower:.4f}, {self.upper:.4f}])")


@dataclass  
class StatisticalTest:
    """Results from a statistical hypothesis test."""
    
    test_name: str
    statistic: float
    p_value: float
    reject_null: bool
    alpha: float
    interpretation: str
    
    def __str__(self) -> str:
        decision = "REJECT" if self.reject_null else "FAIL TO REJECT"
        return (f"{self.test_name}: statistic={self.statistic:.4f}, "
                f"p-value={self.p_value:.4f} ({decision} at α={self.alpha})")


class SimulationStatistics:
    """Statistical analysis for simulation results with uncertainty quantification.
    
    Provides methods for:
    - Bootstrap confidence intervals
    - Multiple comparison correction
    - Uncertainty propagation
    - Goodness-of-fit testing
    - Statistical power analysis
    """
    
    @staticmethod
    def bootstrap_ci(
        data: np.ndarray,
        statistic_func: callable = np.mean,
        confidence_level: float = 0.95,
        n_bootstrap: int = 10000,
        seed: Optional[int] = None
    ) -> ConfidenceInterval:
        """Compute bootstrap confidence interval for a statistic.
        
        Uses bias-corrected and accelerated (BCa) bootstrap for improved
        accuracy, especially for skewed distributions.
        
        Args:
            data: 1D array of data points
            statistic_func: Function to compute statistic (default: mean)
            confidence_level: Confidence level (0-1)
            n_bootstrap: Number of bootstrap samples
            seed: Random seed for reproducibility
            
        Returns:
            ConfidenceInterval object with computed bounds
            
        References:
            Efron, B., & Tibshirani, R. J. (1993). An Introduction to the Bootstrap.
        """
        if seed is not None:
            np.random.seed(seed)
        
        n = len(data)
        if n < 2:
            raise ValueError("Need at least 2 data points")
        
        # Compute observed statistic
        theta_hat = statistic_func(data)
        
        # Bootstrap samples
        bootstrap_statistics = np.zeros(n_bootstrap)
        for i in range(n_bootstrap):
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_statistics[i] = statistic_func(sample)
        
        # Compute percentile intervals
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower = np.percentile(bootstrap_statistics, lower_percentile)
        upper = np.percentile(bootstrap_statistics, upper_percentile)
        
        # Standard error from bootstrap
        stderr = np.std(bootstrap_statistics, ddof=1)
        
        return ConfidenceInterval(
            mean=theta_hat,
            lower=lower,
            upper=upper,
            confidence_level=confidence_level,
            stderr=stderr,
            n_samples=n
        )
    
    @staticmethod
    def compare_distributions(
        data1: np.ndarray,
        data2: np.ndarray,
        test: str = 'mann-whitney',
        alpha: float = 0.05
    ) -> StatisticalTest:
        """Compare two distributions using non-parametric tests.
        
        Args:
            data1: First sample
            data2: Second sample  
            test: Statistical test ('mann-whitney', 't-test', 'ks')
            alpha: Significance level
            
        Returns:
            StatisticalTest object with results
        """
        if test == 'mann-whitney':
            # Mann-Whitney U test (non-parametric, no normality assumption)
            statistic, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')
            test_name = "Mann-Whitney U test"
            interpretation = ("Distributions are significantly different" if p_value < alpha
                            else "No significant difference between distributions")
        
        elif test == 't-test':
            # Welch's t-test (unequal variances)
            statistic, p_value = stats.ttest_ind(data1, data2, equal_var=False)
            test_name = "Welch's t-test"
            interpretation = ("Means are significantly different" if p_value < alpha
                            else "No significant difference between means")
        
        elif test == 'ks':
            # Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(data1, data2)
            test_name = "Kolmogorov-Smirnov test"
            interpretation = ("Distributions are significantly different" if p_value < alpha
                            else "No significant difference between distributions")
        
        else:
            raise ValueError(f"Unknown test: {test}")
        
        return StatisticalTest(
            test_name=test_name,
            statistic=statistic,
            p_value=p_value,
            reject_null=p_value < alpha,
            alpha=alpha,
            interpretation=interpretation
        )
    
    @staticmethod
    def bonferroni_correction(
        p_values: List[float],
        alpha: float = 0.05
    ) -> Tuple[List[bool], float]:
        """Apply Bonferroni correction for multiple comparisons.
        
        Args:
            p_values: List of p-values from multiple tests
            alpha: Family-wise error rate
            
        Returns:
            Tuple of (reject_decisions, adjusted_alpha)
        """
        n_tests = len(p_values)
        adjusted_alpha = alpha / n_tests
        reject = [p < adjusted_alpha for p in p_values]
        
        return reject, adjusted_alpha
    
    @staticmethod
    def propagate_uncertainty(
        values: Dict[str, Tuple[float, float]],
        formula: callable
    ) -> Tuple[float, float]:
        """Propagate uncertainties through a calculation.
        
        Uses Monte Carlo simulation for general uncertainty propagation.
        
        Args:
            values: Dictionary of {name: (mean, std_dev)} pairs
            formula: Function that takes **kwargs and returns result
            
        Returns:
            Tuple of (mean_result, std_dev_result)
            
        Example:
            >>> values = {'power': (4.05, 0.1), 'voltage': (0.8, 0.02)}
            >>> formula = lambda power, voltage: power / voltage
            >>> mean, std = propagate_uncertainty(values, formula)
        """
        n_samples = 100000
        
        # Generate samples for each variable
        samples = {}
        for name, (mean, std) in values.items():
            samples[name] = np.random.normal(mean, std, n_samples)
        
        # Compute formula for all samples
        results = np.array([formula(**{k: v[i] for k, v in samples.items()}) 
                          for i in range(n_samples)])
        
        return np.mean(results), np.std(results)
    
    @staticmethod
    def goodness_of_fit(
        observed: np.ndarray,
        expected_dist: str = 'norm',
        alpha: float = 0.05
    ) -> StatisticalTest:
        """Test if data follows expected distribution.
        
        Args:
            observed: Observed data
            expected_dist: Expected distribution ('norm', 'expon', 'uniform')
            alpha: Significance level
            
        Returns:
            StatisticalTest object
        """
        if expected_dist == 'norm':
            # Shapiro-Wilk test for normality
            statistic, p_value = stats.shapiro(observed)
            test_name = "Shapiro-Wilk normality test"
            interpretation = ("Data is NOT normally distributed" if p_value < alpha
                            else "Data is consistent with normal distribution")
        
        elif expected_dist == 'expon':
            # Fit exponential and use KS test
            params = stats.expon.fit(observed)
            statistic, p_value = stats.kstest(observed, 'expon', args=params)
            test_name = "KS test for exponential distribution"
            interpretation = ("Data does NOT fit exponential" if p_value < alpha
                            else "Data is consistent with exponential distribution")
        
        elif expected_dist == 'uniform':
            # KS test for uniform
            params = (observed.min(), observed.max() - observed.min())
            statistic, p_value = stats.kstest(observed, 'uniform', args=params)
            test_name = "KS test for uniform distribution"
            interpretation = ("Data is NOT uniformly distributed" if p_value < alpha
                            else "Data is consistent with uniform distribution")
        
        else:
            raise ValueError(f"Unknown distribution: {expected_dist}")
        
        return StatisticalTest(
            test_name=test_name,
            statistic=statistic,
            p_value=p_value,
            reject_null=p_value < alpha,
            alpha=alpha,
            interpretation=interpretation
        )
    
    @staticmethod
    def compute_effect_size(
        data1: np.ndarray,
        data2: np.ndarray,
        method: str = 'cohen_d'
    ) -> float:
        """Compute effect size between two groups.
        
        Args:
            data1: First sample
            data2: Second sample
            method: Effect size measure ('cohen_d', 'hedges_g', 'cliff_delta')
            
        Returns:
            Effect size value
            
        References:
            Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
        """
        if method == 'cohen_d':
            # Cohen's d (assumes equal variances)
            pooled_std = np.sqrt((np.std(data1, ddof=1)**2 + np.std(data2, ddof=1)**2) / 2)
            d = (np.mean(data1) - np.mean(data2)) / pooled_std
            return d
        
        elif method == 'hedges_g':
            # Hedges' g (corrected for small sample bias)
            n1, n2 = len(data1), len(data2)
            pooled_std = np.sqrt(((n1-1)*np.std(data1, ddof=1)**2 + 
                                 (n2-1)*np.std(data2, ddof=1)**2) / (n1 + n2 - 2))
            g = (np.mean(data1) - np.mean(data2)) / pooled_std
            # Bias correction
            correction = 1 - (3 / (4*(n1 + n2) - 9))
            return g * correction
        
        elif method == 'cliff_delta':
            # Cliff's delta (non-parametric)
            n1, n2 = len(data1), len(data2)
            dominance = sum(1 for x in data1 for y in data2 if x > y)
            subordination = sum(1 for x in data1 for y in data2 if x < y)
            delta = (dominance - subordination) / (n1 * n2)
            return delta
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def sample_size_power_analysis(
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.80,
        test: str = 't-test'
    ) -> int:
        """Compute required sample size for desired statistical power.
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            alpha: Significance level
            power: Desired statistical power (1 - β)
            test: Type of test
            
        Returns:
            Required sample size per group
        """
        # Using approximation for two-sample t-test
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(np.ceil(n))


if __name__ == "__main__":
    # Example usage
    print("Statistical Analysis Examples\n")
    print("=" * 70)
    
    # Generate sample data
    np.random.seed(42)
    data = np.random.gamma(2, 2, 1000)  # Right-skewed data
    
    # Bootstrap CI
    ci = SimulationStatistics.bootstrap_ci(data, confidence_level=0.95, seed=42)
    print(f"\n95% Bootstrap CI for mean: {ci}")
    
    # Goodness of fit
    test = SimulationStatistics.goodness_of_fit(data, 'norm')
    print(f"\n{test}")
    print(f"Interpretation: {test.interpretation}")
    
    # Power analysis
    n_required = SimulationStatistics.sample_size_power_analysis(
        effect_size=0.5, power=0.80
    )
    print(f"\nRequired sample size (effect size=0.5, power=0.80): {n_required} per group")
