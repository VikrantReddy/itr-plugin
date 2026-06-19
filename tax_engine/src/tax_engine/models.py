from dataclasses import dataclass, field
from enum import Enum


class AssetClass(str, Enum):
    EQUITY_STT = "equity_stt"
    GENERAL = "general"
    LAND_BUILDING = "land_building"
    VDA = "vda"


@dataclass(frozen=True)
class CapitalGainEntry:
    asset_class: AssetClass
    is_long_term: bool
    gain: float
    acquired_before_2024_07_23: bool = False
    indexed_gain: float | None = None


@dataclass(frozen=True)
class TaxInput:
    salary_gross: float
    other_income: float
    capital_gains: list[CapitalGainEntry] = field(default_factory=list)
    deductions_80c: float = 0.0
    deductions_80d: float = 0.0
    is_senior_citizen: bool = False


@dataclass(frozen=True)
class RegimeResult:
    regime: str
    taxable_income_at_slab: float
    slab_tax: float
    capital_gains_tax: float
    rebate: float
    cess: float
    total_tax: float
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComparisonResult:
    old: RegimeResult
    new: RegimeResult
    recommended: str
