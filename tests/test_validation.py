"""
Unit tests for validation.py. These run with plain Python data structures -
no API key, no PDFs, no network - so they test the sanity-check logic in
isolation from the AI extraction step.

Run with: python3 -m pytest tests/test_validation.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation import validate_extraction


GOOD_INVOICE = {
    "document_type": "invoice",
    "vendor_name": "ACME Industrial Supply Co.",
    "document_date": "2026-06-03",
    "due_date": "2026-07-03",
    "line_items": [
        {"description": "Bolt", "quantity": 500, "unit_price": 0.42, "line_total": 210.00},
        {"description": "Hinge", "quantity": 40, "unit_price": 6.75, "line_total": 270.00},
    ],
    "subtotal": 480.00,
    "tax_amount": 28.80,
    "total": 508.80,
}


def test_good_invoice_passes():
    result = validate_extraction(GOOD_INVOICE)
    assert result["valid"] is True
    assert result["issues"] == []


def test_catches_wrong_line_total():
    bad = dict(GOOD_INVOICE)
    bad["line_items"] = [
        {"description": "Bolt", "quantity": 500, "unit_price": 0.42, "line_total": 999.00},  # wrong
        {"description": "Hinge", "quantity": 40, "unit_price": 6.75, "line_total": 270.00},
    ]
    result = validate_extraction(bad)
    assert result["valid"] is False
    assert any("Bolt" in issue for issue in result["issues"])


def test_catches_subtotal_mismatch():
    bad = dict(GOOD_INVOICE)
    bad["subtotal"] = 999.99
    result = validate_extraction(bad)
    assert result["valid"] is False
    assert any("subtotal" in issue.lower() for issue in result["issues"])


def test_catches_total_mismatch():
    bad = dict(GOOD_INVOICE)
    bad["total"] = 1.00
    result = validate_extraction(bad)
    assert result["valid"] is False
    assert any("total" in issue.lower() for issue in result["issues"])


def test_catches_invalid_date_format():
    bad = dict(GOOD_INVOICE)
    bad["document_date"] = "June 3rd 2026"  # not ISO format
    result = validate_extraction(bad)
    assert result["valid"] is False
    assert any("document_date" in issue for issue in result["issues"])


def test_catches_due_date_before_document_date():
    bad = dict(GOOD_INVOICE)
    bad["document_date"] = "2026-07-03"
    bad["due_date"] = "2026-06-03"  # before document date - impossible
    result = validate_extraction(bad)
    assert result["valid"] is False
    assert any("before" in issue for issue in result["issues"])


def test_catches_missing_required_field():
    bad = dict(GOOD_INVOICE)
    del bad["vendor_name"]
    result = validate_extraction(bad)
    assert result["valid"] is False
    assert any("vendor_name" in issue for issue in result["issues"])


def test_receipt_with_no_tax_passes():
    # Mirrors the receipt sample: no tax_amount field at all, should not
    # be treated as an error, just tax=0.
    receipt = {
        "document_type": "receipt",
        "vendor_name": "Cornerstore Market",
        "document_date": "2026-06-07",
        "due_date": None,
        "line_items": [
            {"description": "Water", "quantity": 2, "unit_price": 1.25, "line_total": 2.50},
            {"description": "Bread", "quantity": 1, "unit_price": 3.49, "line_total": 3.49},
        ],
        "subtotal": 5.99,
        "tax_amount": None,
        "total": 5.99,
    }
    result = validate_extraction(receipt)
    assert result["valid"] is True


def test_missing_line_items_is_flagged():
    bad = dict(GOOD_INVOICE)
    bad["line_items"] = []
    result = validate_extraction(bad)
    assert result["valid"] is False
