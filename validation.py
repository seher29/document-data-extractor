"""
Validation and sanity-check logic for extracted document data.

This is deliberately kept separate from the AI extraction step and uses
plain Python arithmetic/date parsing - not the model - to check the
model's output. This is the "real computation" the assignment brief asks
for: we don't trust the AI to add up numbers correctly, we check it.
"""

from datetime import datetime


def check_line_items_sum_to_total(data: dict, tolerance: float = 0.02) -> list:
    """
    Returns a list of issue strings (empty list = passed).
    Compares sum(line item totals) [+ tax, if present] against the stated total.
    """
    issues = []
    items = data.get("line_items", [])
    if not items:
        issues.append("No line items found to validate against total.")
        return issues

    computed_subtotal = 0.0
    for i, item in enumerate(items):
        qty = item.get("quantity")
        unit_price = item.get("unit_price")
        line_total = item.get("line_total")

        if qty is None or unit_price is None or line_total is None:
            issues.append(f"Line item {i} ('{item.get('description', '?')}') is missing quantity/unit_price/line_total.")
            continue

        expected_line_total = round(qty * unit_price, 2)
        if abs(expected_line_total - line_total) > tolerance:
            issues.append(
                f"Line item {i} ('{item.get('description', '?')}'): "
                f"{qty} x {unit_price} = {expected_line_total}, but line_total says {line_total}."
            )
        computed_subtotal += line_total

    stated_subtotal = data.get("subtotal")
    if stated_subtotal is not None and abs(computed_subtotal - stated_subtotal) > tolerance:
        issues.append(
            f"Sum of line items ({computed_subtotal:.2f}) does not match stated subtotal ({stated_subtotal})."
        )

    tax = data.get("tax_amount") or 0.0
    total = data.get("total")
    if total is not None:
        base = stated_subtotal if stated_subtotal is not None else computed_subtotal
        expected_total = round(base + tax, 2)
        if abs(expected_total - total) > tolerance:
            issues.append(
                f"subtotal ({base:.2f}) + tax ({tax:.2f}) = {expected_total:.2f}, but stated total is {total}."
            )

    return issues


def check_dates_valid(data: dict) -> list:
    """
    Checks that any date fields are present and parse as real calendar dates
    in ISO format (YYYY-MM-DD). Does not require any specific date to exist,
    but if a field is present it must be a valid, parseable date, and
    due_date (if present) must not be before document_date.
    """
    issues = []
    date_fields = ["document_date", "due_date"]
    parsed = {}

    for field in date_fields:
        val = data.get(field)
        if val is None:
            continue
        try:
            parsed[field] = datetime.strptime(val, "%Y-%m-%d")
        except (ValueError, TypeError):
            issues.append(f"Field '{field}' is not a valid ISO date (YYYY-MM-DD): {val!r}")

    if "document_date" in parsed and "due_date" in parsed:
        if parsed["due_date"] < parsed["document_date"]:
            issues.append(
                f"due_date ({data['due_date']}) is before document_date ({data['document_date']}) - likely misread."
            )

    return issues


def check_required_fields(data: dict) -> list:
    """Confirms the minimum fields needed for the document to be usable are present."""
    issues = []
    required = ["document_type", "vendor_name", "document_date", "total", "line_items"]
    for field in required:
        if data.get(field) in (None, "", []):
            issues.append(f"Required field '{field}' is missing or empty.")
    return issues


def validate_extraction(data: dict) -> dict:
    """
    Runs all sanity checks and returns a summary dict:
    {
        "valid": bool,
        "issues": [...],
    }
    "valid" is True only if there are zero issues across all checks.
    """
    issues = []
    issues += check_required_fields(data)
    issues += check_dates_valid(data)
    issues += check_line_items_sum_to_total(data)

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }
