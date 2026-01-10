"""Tests for power, area, and performance models."""

import pytest


def test_import_models():
    """Test that model modules can be imported."""
    from src.models.kv_cache_sizing import KVCacheSizer, ModelConfig
    from src.models.memory_power_model import MemoryPowerModel

    assert KVCacheSizer is not None
    assert ModelConfig is not None
    assert MemoryPowerModel is not None


def test_model_config_defaults():
    """Test ModelConfig default values."""
    from src.models.kv_cache_sizing import ModelConfig

    config = ModelConfig()
    assert config.num_layers == 32
    assert config.hidden_dim == 4096
    assert config.context_length == 4096


def test_kv_cache_int4_size():
    """Test KV-cache size calculation for INT4."""
    from src.models.kv_cache_sizing import KVCacheSizer

    sizer = KVCacheSizer()
    result = sizer.calculate("INT4")

    assert result["precision"] == "INT4"
    assert result["size_mb"] == 512.0
    assert result["bytes_per_element"] == 0.5


def test_kv_cache_int8_size():
    """Test KV-cache size calculation for INT8."""
    from src.models.kv_cache_sizing import KVCacheSizer

    sizer = KVCacheSizer()
    result = sizer.calculate("INT8")

    assert result["precision"] == "INT8"
    assert result["size_mb"] == 1024.0
    assert result["bytes_per_element"] == 1.0


def test_kv_cache_all_precisions():
    """Test KV-cache calculation for all precisions."""
    from src.models.kv_cache_sizing import KVCacheSizer

    sizer = KVCacheSizer()
    results = sizer.calculate_all_precisions()

    assert "FP32" in results
    assert "FP16" in results
    assert "INT8" in results
    assert "INT4" in results

    # Verify size ordering
    assert results["FP32"]["size_mb"] > results["FP16"]["size_mb"]
    assert results["FP16"]["size_mb"] > results["INT8"]["size_mb"]
    assert results["INT8"]["size_mb"] > results["INT4"]["size_mb"]


def test_memory_power_model_edram():
    """Test eDRAM power model."""
    from src.models.memory_power_model import MemoryPowerModel

    model = MemoryPowerModel(224, 20, "eDRAM")
    power = model.estimate_power()

    assert power["technology"] == "eDRAM"
    assert power["total_w"] > 0
    assert power["total_w"] < 5.0  # Should be reasonable for edge
    assert power["dynamic_w"] > 0
    assert power["static_w"] > 0


def test_memory_power_model_sram():
    """Test SRAM power model."""
    from src.models.memory_power_model import MemoryPowerModel

    model = MemoryPowerModel(32, 20, "HD_SRAM")
    power = model.estimate_power()

    assert power["technology"] == "HD_SRAM"
    assert power["total_w"] > 0


def test_sram_area_estimation():
    """Test SRAM area estimation."""
    from src.models.sram_area_model import estimate_sram_area

    area = estimate_sram_area(cache_size_mb=32, process_node_nm=3)

    assert area > 0
    assert area < 10.0  # Reasonable for 32 MB at 3nm


def test_thermal_analyzer():
    """Test thermal analysis."""
    from src.models.thermal_analysis import ThermalAnalyzer

    # Use enhanced package with lower thermal resistance (20°C/W)
    thermal = ThermalAnalyzer(power_w=4.0, ambient_c=25.0)
    result = thermal.calculate_junction_temp(package="enhanced")

    assert result["ambient_temp_c"] == 25.0
    assert result["power_w"] == 4.0
    assert result["junction_temp_c"] > 25.0
    assert result["junction_temp_c"] < 125.0  # Below max spec
    assert result["thermal_margin_c"] > 0
    assert result["within_spec"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
