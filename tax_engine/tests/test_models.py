from tax_engine.models import AssetClass, CapitalGainEntry, TaxInput


def test_capital_gain_entry_defaults():
    entry = CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=True, gain=10000)
    assert entry.acquired_before_2024_07_23 is False
    assert entry.indexed_gain is None


def test_tax_input_defaults():
    tax_input = TaxInput(salary_gross=1200000, other_income=0, capital_gains=[])
    assert tax_input.deductions_80c == 0.0
    assert tax_input.is_senior_citizen is False
