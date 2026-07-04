import pandera.pandas as pa
import pandas as pd
from pandera.pandas import Column, DataFrameSchema, Check

raw_schema = DataFrameSchema({
    "source_name": Column(str, Check.isin([
        "wind", "gas", "coal", "interconnector", "hydro", "solar"
    ])),
    "generation_mw": Column(float, [
        Check.greater_than(0),
        Check.less_than(5000)
    ]),
    "carbon_intensity": Column(float, [
        Check.greater_than_or_equal_to(0),
        Check.less_than_or_equal_to(500)
    ]),
    "timestamp": Column(str, Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
})

def test_raw_schema_valid():
    valid_data = pd.DataFrame([
        {"source_name": "wind", "generation_mw": 500.0,
         "carbon_intensity": 10.0, "timestamp": "2026-07-04"},
        {"source_name": "gas", "generation_mw": 800.0,
         "carbon_intensity": 300.0, "timestamp": "2026-07-04"},
    ])
    raw_schema.validate(valid_data)

def test_raw_schema_rejects_wrong_source():
    invalid_data = pd.DataFrame([
        {"source_name": "nuclear", "generation_mw": 500.0,
         "carbon_intensity": 10.0, "timestamp": "2026-07-04"},
    ])
    try:
        raw_schema.validate(invalid_data)
        assert False, "Should have raised SchemaError"
    except pa.errors.SchemaError:
        pass

def test_raw_schema_rejects_negative_generation():
    invalid_data = pd.DataFrame([
        {"source_name": "wind", "generation_mw": -100.0,
         "carbon_intensity": 10.0, "timestamp": "2026-07-04"},
    ])
    try:
        raw_schema.validate(invalid_data)
        assert False, "Should have raised SchemaError"
    except pa.errors.SchemaError:
        pass

def test_raw_schema_rejects_bad_date_format():
    invalid_data = pd.DataFrame([
        {"source_name": "wind", "generation_mw": 500.0,
         "carbon_intensity": 10.0, "timestamp": "04-07-2026"},
    ])
    try:
        raw_schema.validate(invalid_data)
        assert False, "Should have raised SchemaError"
    except pa.errors.SchemaError:
        pass