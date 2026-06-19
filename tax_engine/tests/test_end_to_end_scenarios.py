import json
from pathlib import Path

import pytest

from tax_engine.compute_tax import compare_regimes
from tax_engine.models import AssetClass, CapitalGainEntry, TaxInput

RULES = json.loads((Path(__file__).parent.parent / "rules" / "tax_year_2026_27.json").read_text())


def test_scenario_salaried_no_investments_new_regime_wins():
    tax_input = TaxInput(salary_gross=900000, other_income=20000)
    result = compare_regimes(tax_input, RULES)
    assert result.recommended == "new"
    assert result.new.total_tax < result.old.total_tax


def test_scenario_high_80c_80d_old_regime_can_win():
    tax_input = TaxInput(
        salary_gross=1100000,
        other_income=0,
        deductions_80c=150000,
        deductions_80d=50000,
        is_senior_citizen=False,
    )
    result = compare_regimes(tax_input, RULES)
    cheaper = "old" if result.old.total_tax < result.new.total_tax else "new"
    assert result.recommended == cheaper


def test_scenario_equity_trader_with_stcg_and_ltcg():
    tax_input = TaxInput(
        salary_gross=1500000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=False, gain=300000),
            CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=True, gain=400000),
        ],
    )
    result = compare_regimes(tax_input, RULES)
    expected_cg_tax = 300000 * 0.20 + (400000 - 125000) * 0.125
    assert result.new.capital_gains_tax == pytest.approx(expected_cg_tax)
    assert result.old.capital_gains_tax == pytest.approx(expected_cg_tax)


def test_scenario_crypto_investor_with_loss_warning():
    tax_input = TaxInput(
        salary_gross=800000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(asset_class=AssetClass.VDA, is_long_term=False, gain=150000),
            CapitalGainEntry(asset_class=AssetClass.VDA, is_long_term=False, gain=-60000),
        ],
    )
    result = compare_regimes(tax_input, RULES)
    assert result.new.capital_gains_tax == pytest.approx(45000)
    assert any("loss" in w.lower() for w in result.new.warnings)


def test_scenario_pre_2024_property_sale_grandfathering_benefits_taxpayer():
    tax_input = TaxInput(
        salary_gross=1200000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(
                asset_class=AssetClass.LAND_BUILDING,
                is_long_term=True,
                gain=2000000,
                acquired_before_2024_07_23=True,
                indexed_gain=1200000,
            )
        ],
    )
    result = compare_regimes(tax_input, RULES)
    assert result.new.capital_gains_tax == pytest.approx(240000)


def test_scenario_zero_income_produces_zero_tax():
    tax_input = TaxInput(salary_gross=0, other_income=0)
    result = compare_regimes(tax_input, RULES)
    assert result.old.total_tax == 0
    assert result.new.total_tax == 0
