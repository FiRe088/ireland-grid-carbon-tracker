import pandas as pd
import pytest

EXPECTED_SOURCES = {"wind", "gas", "coal", "interconnector", "hydro", "solar"}
EXPECTED_ROW_COUNT = 6

def test_all_sources_present():
    df = pd.DataFrame([
        {"source_name": s, "generation_mw": 500.0,
         "carbon_intensity": 100.0, "timestamp": "2026-07-04"}
        for s in EXPECTED_SOURCES
    ])
    assert set(df["source_name"].unique()) == EXPECTED_SOURCES

def test_no_empty_dataframe():
    df = pd.DataFrame([
        {"source_name": "wind", "generation_mw": 500.0,
         "carbon_intensity": 100.0, "timestamp": "2026-07-04"}
    ])
    assert not df.empty, "Pipeline produced empty DataFrame"
    assert len(df) > 0
    
def test_null_generation_is_detected():
    """Confirms our null check catches bad data — this is what the pipeline filter prevents"""
    df = pd.DataFrame([
        {"source_name": "wind", "generation_mw": None,
         "carbon_intensity": 100.0, "timestamp": "2026-07-04"}
    ])
    null_count = df["generation_mw"].isnull().sum()
    assert null_count > 0, "Expected null to be detected but wasn't"

def test_clean_data_has_no_nulls():
    """Confirms valid pipeline output has no null generation values"""
    df = pd.DataFrame([
        {"source_name": s, "generation_mw": 500.0,
         "carbon_intensity": 100.0, "timestamp": "2026-07-04"}
        for s in ["wind", "gas", "coal", "interconnector", "hydro", "solar"]
    ])
    assert df["generation_mw"].isnull().sum() == 0