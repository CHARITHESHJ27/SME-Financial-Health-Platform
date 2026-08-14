"""
Financial Data Validation Module.
Ensures consistency, non-negativity, and structural validity of SME financial records.
"""

from typing import Dict, Any, List, Tuple
from ml.features.feature_definitions import ALLOWED_INDUSTRIES


class FinancialValidationError(ValueError):
    """Custom exception raised when financial data fails business or structural validation."""
    def __init__(self, message: str, field: str = "", code: str = "INVALID_FINANCIAL_DATA"):
        super().__init__(message)
        self.field = field
        self.code = code
        self.message = message


def validate_raw_financial_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a dictionary of raw financial figures.
    Returns:
        (is_valid: bool, error_messages: List[str])
    """
    errors = []

    # 1. Check required fields exist
    required_keys = [
        "revenue", "total_expenses", "current_assets",
        "current_liabilities", "total_assets", "total_debt"
    ]
    for key in required_keys:
        if key not in data or data[key] is None:
            errors.append(f"Missing required financial field: '{key}'")

    if errors:
        return False, errors

    try:
        revenue = float(data.get("revenue", 0))
        expenses = float(data.get("total_expenses", 0))
        current_assets = float(data.get("current_assets", 0))
        current_liabilities = float(data.get("current_liabilities", 0))
        total_assets = float(data.get("total_assets", 0))
        total_debt = float(data.get("total_debt", 0))
        inventory = float(data.get("inventory", 0) or 0)
        accounts_receivable = float(data.get("accounts_receivable", 0) or 0)
        accounts_payable = float(data.get("accounts_payable", 0) or 0)
        growth_rate = float(data.get("revenue_growth_rate", 0) or 0)
    except (ValueError, TypeError) as e:
        return False, [f"Financial values must be numeric: {e}"]

    # 2. Non-negativity constraints
    non_negative_checks = [
        ("revenue", revenue),
        ("total_expenses", expenses),
        ("current_assets", current_assets),
        ("current_liabilities", current_liabilities),
        ("total_assets", total_assets),
        ("total_debt", total_debt),
        ("inventory", inventory),
        ("accounts_receivable", accounts_receivable),
        ("accounts_payable", accounts_payable),
    ]
    for field_name, val in non_negative_checks:
        if val < 0:
            errors.append(f"'{field_name}' must be non-negative (received {val})")

    # 3. Minimum active business threshold
    if revenue <= 0:
        errors.append("Revenue must be greater than zero for financial health assessment")

    if total_assets <= 0:
        errors.append("Total assets must be greater than zero")

    # 4. Balance sheet consistency checks
    if current_assets > total_assets * 1.001:  # small epsilon for floating point
        errors.append(f"Current assets ({current_assets:,.2f}) cannot exceed total assets ({total_assets:,.2f})")

    if total_debt > total_assets * 3.0:  # extreme distress or invalid entry
        errors.append(f"Total debt ({total_debt:,.2f}) cannot exceed 300% of total assets ({total_assets:,.2f})")

    if inventory > current_assets * 1.001:
        errors.append(f"Inventory ({inventory:,.2f}) cannot exceed current assets ({current_assets:,.2f})")

    if accounts_receivable > current_assets * 1.001:
        errors.append(f"Accounts receivable ({accounts_receivable:,.2f}) cannot exceed current assets ({current_assets:,.2f})")

    # 5. Growth rate sanity check (-100% to +500%)
    if growth_rate < -1.0 or growth_rate > 5.0:
        errors.append(f"Revenue growth rate ({growth_rate*100:.1f}%) must be between -100% and +500%")

    # 6. Industry check
    industry = str(data.get("industry", "services")).lower()
    if industry not in ALLOWED_INDUSTRIES:
        errors.append(f"Invalid industry '{industry}'. Allowed industries: {ALLOWED_INDUSTRIES}")

    return (len(errors) == 0), errors


def sanitize_financial_inputs(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and provide safe defaults for financial inputs.
    """
    clean = {}
    float_fields = [
        "revenue", "total_expenses", "current_assets",
        "current_liabilities", "total_assets", "total_debt",
        "inventory", "accounts_receivable", "accounts_payable",
        "revenue_growth_rate"
    ]
    for f in float_fields:
        val = data.get(f, 0.0)
        try:
            clean[f] = float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            clean[f] = 0.0

    industry = str(data.get("industry", "services")).lower().strip()
    clean["industry"] = industry if industry in ALLOWED_INDUSTRIES else "services"
    return clean
