"""
Generates eight sample documents across six genuinely different layouts,
so the extractor has to actually handle layout variation rather than
being hard-coded to one template. Covers the brief's "5-10 real examples"
step and the Advanced tier's "at least two layouts" deliverable several
times over.

1. invoice_acme.pdf            - itemized invoice, tax line, due date
2. receipt_cornerstore.pdf     - narrow retail receipt, no tax line
3. po_northwind.pdf            - purchase order, ship-to + delivery date
4. invoice_freelance.pdf       - hourly consulting invoice (qty = hours)
5. receipt_diner.pdf           - restaurant receipt with tax + tip line
6. invoice_utility.pdf         - utility bill, single line item
7. invoice_saas.pdf            - SaaS subscription invoice, single line item
8. receipt_hardware.pdf        - hardware store receipt, tax line present
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

OUT = "sample_documents"


def make_invoice():
    path = f"{OUT}/invoice_acme.pdf"
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 72

    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, y, "ACME Industrial Supply Co.")
    c.setFont("Helvetica", 9)
    c.drawString(72, y - 14, "42 Foundry Road, Detroit, MI 48201")

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 72, y, "INVOICE")
    y -= 40

    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Invoice #: INV-2026-0447")
    c.drawString(320, y, "Invoice Date: 2026-06-03")
    y -= 14
    c.drawString(72, y, "Bill To: Meridian Construction LLC")
    c.drawString(320, y, "Due Date: 2026-07-03")
    y -= 30

    # Table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, y, "Item")
    c.drawString(300, y, "Qty")
    c.drawString(350, y, "Unit Price")
    c.drawString(450, y, "Line Total")
    y -= 6
    c.line(72, y, width - 72, y)
    y -= 16

    items = [
        ("Galvanized Steel Bolt (M10)", 500, 0.42),
        ("Industrial Hinge, Heavy Duty", 40, 6.75),
        ("Safety Gloves (Pair)", 60, 3.20),
        ("Epoxy Sealant, 500ml", 15, 11.99),
    ]
    c.setFont("Helvetica", 10)
    subtotal = 0.0
    for name, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        c.drawString(72, y, name)
        c.drawString(300, y, str(qty))
        c.drawString(350, y, f"${price:.2f}")
        c.drawString(450, y, f"${line_total:.2f}")
        y -= 16

    y -= 6
    c.line(350, y, width - 72, y)
    y -= 16

    tax_rate = 0.06
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    c.setFont("Helvetica", 10)
    c.drawString(350, y, "Subtotal:")
    c.drawString(450, y, f"${subtotal:.2f}")
    y -= 16
    c.drawString(350, y, f"Tax (6%):")
    c.drawString(450, y, f"${tax:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, "Total Due:")
    c.drawString(450, y, f"${total:.2f}")

    y -= 40
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(72, y, "Payment terms: Net 30. Late payments subject to 1.5% monthly interest.")

    c.save()
    print(f"Wrote {path}  (subtotal={subtotal:.2f} tax={tax:.2f} total={total:.2f})")


def make_receipt():
    path = f"{OUT}/receipt_cornerstore.pdf"
    # Narrow receipt-style page
    page_size = (3.2 * inch, 7.5 * inch)
    c = canvas.Canvas(path, pagesize=page_size)
    width, height = page_size
    y = height - 30

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "CORNERSTORE MARKET")
    y -= 12
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "118 Elm St, Austin, TX 78701")
    y -= 18

    c.setFont("Helvetica", 7)
    c.drawString(10, y, "Receipt #: 88213")
    y -= 10
    c.drawString(10, y, "Date: 06/07/2026  14:22")
    y -= 16

    c.line(10, y, width - 10, y)
    y -= 12

    items = [
        ("Bottled Water 1L", 2, 1.25),
        ("Whole Wheat Bread", 1, 3.49),
        ("Bananas (lb)", 3, 0.59),
        ("Peanut Butter Jar", 1, 4.99),
        ("Paper Towels 2pk", 1, 5.75),
    ]
    c.setFont("Helvetica", 7)
    subtotal = 0.0
    for name, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        c.drawString(10, y, f"{name}")
        y -= 9
        c.drawString(14, y, f"{qty} x ${price:.2f}")
        c.drawRightString(width - 10, y, f"${line_total:.2f}")
        y -= 12

    c.line(10, y, width - 10, y)
    y -= 12

    # No tax line on this one deliberately (grocery staples, tax-exempt) -
    # tests that the extractor doesn't assume tax always exists.
    c.setFont("Helvetica-Bold", 8)
    c.drawString(10, y, "TOTAL")
    c.drawRightString(width - 10, y, f"${subtotal:.2f}")
    y -= 18

    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "Paid by VISA ****4471")
    y -= 10
    c.drawCentredString(width / 2, y, "Thank you for shopping with us!")

    c.save()
    print(f"Wrote {path}  (total={subtotal:.2f}, no tax line)")


def make_purchase_order():
    path = f"{OUT}/po_northwind.pdf"
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 60

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "Northwind Distribution Ltd.")
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - 72, y, "PURCHASE ORDER")
    y -= 20
    c.setFont("Helvetica", 9)
    c.drawString(72, y, "890 Harbor Way, Seattle, WA 98101")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(72, y, "PO Number: PO-88291")
    c.drawString(320, y, "Order Date: 2026-05-11")
    y -= 14
    c.drawString(72, y, "Vendor: Pacific Timber Supply")
    c.drawString(320, y, "Expected Delivery: 2026-05-25")
    y -= 14
    c.drawString(72, y, "Ship To: Northwind Warehouse #3")
    y -= 30

    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, y, "Description")
    c.drawString(320, y, "Qty")
    c.drawString(380, y, "Unit Price")
    c.drawString(470, y, "Line Total")
    y -= 6
    c.line(72, y, width - 72, y)
    y -= 16

    items = [
        ("Kiln-Dried Pine 2x4x8", 200, 4.15),
        ("Plywood Sheet 3/4in", 60, 28.50),
        ("Deck Screws, 5lb box", 25, 14.25),
    ]
    c.setFont("Helvetica", 10)
    subtotal = 0.0
    for name, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        c.drawString(72, y, name)
        c.drawString(320, y, str(qty))
        c.drawString(380, y, f"${price:.2f}")
        c.drawString(470, y, f"${line_total:.2f}")
        y -= 16

    y -= 6
    c.line(380, y, width - 72, y)
    y -= 16

    tax_rate = 0.085
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    c.setFont("Helvetica", 10)
    c.drawString(380, y, "Subtotal:")
    c.drawString(470, y, f"${subtotal:.2f}")
    y -= 16
    c.drawString(380, y, "Sales Tax (8.5%):")
    c.drawString(470, y, f"${tax:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(380, y, "PO Total:")
    c.drawString(470, y, f"${total:.2f}")

    y -= 40
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(72, y, "Please reference PO number on all packing slips and invoices.")

    c.save()
    print(f"Wrote {path}  (subtotal={subtotal:.2f} tax={tax:.2f} total={total:.2f})")


def make_freelance_invoice():
    path = f"{OUT}/invoice_freelance.pdf"
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 72

    c.setFont("Helvetica-Bold", 15)
    c.drawString(72, y, "Priya Raman — UX Consulting")
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawString(72, y, "Independent Contractor | priya@ramanux.example")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 72, y + 16, "INVOICE")
    y -= 34

    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Invoice #: PR-2026-014")
    c.drawString(320, y, "Date: 2026-06-20")
    y -= 14
    c.drawString(72, y, "Bill To: Lumen Software Inc.")
    c.drawString(320, y, "Due: 2026-07-04")
    y -= 30

    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, y, "Service")
    c.drawString(320, y, "Hours")
    c.drawString(380, y, "Rate/hr")
    c.drawString(470, y, "Amount")
    y -= 6
    c.line(72, y, width - 72, y)
    y -= 16

    items = [
        ("UX audit & research", 12, 95.00),
        ("Wireframe design", 18, 95.00),
        ("Client review sessions", 4, 95.00),
    ]
    c.setFont("Helvetica", 10)
    subtotal = 0.0
    for name, hours, rate in items:
        line_total = hours * rate
        subtotal += line_total
        c.drawString(72, y, name)
        c.drawString(320, y, str(hours))
        c.drawString(380, y, f"${rate:.2f}")
        c.drawString(470, y, f"${line_total:.2f}")
        y -= 16

    y -= 6
    c.line(380, y, width - 72, y)
    y -= 16

    # Freelancer is not tax-registered - no tax line at all, different from
    # the ACME invoice which has one.
    c.setFont("Helvetica-Bold", 11)
    c.drawString(380, y, "Total Due:")
    c.drawString(470, y, f"${subtotal:.2f}")

    y -= 40
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(72, y, "Payable via bank transfer within 14 days. No sales tax applicable (sole proprietor).")

    c.save()
    print(f"Wrote {path}  (total={subtotal:.2f}, no tax line)")


def make_diner_receipt():
    path = f"{OUT}/receipt_diner.pdf"
    page_size = (3.2 * inch, 7.5 * inch)
    c = canvas.Canvas(path, pagesize=page_size)
    width, height = page_size
    y = height - 30

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "BLUE PLATE DINER")
    y -= 12
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "27 Riverside Ave, Portland, OR")
    y -= 18

    c.setFont("Helvetica", 7)
    c.drawString(10, y, "Check #: 4471")
    y -= 10
    c.drawString(10, y, "Date: 06/21/2026  19:04")
    y -= 10
    c.drawString(10, y, "Server: M.")
    y -= 16

    c.line(10, y, width - 10, y)
    y -= 12

    items = [
        ("Grilled Salmon", 1, 24.00),
        ("Caesar Salad", 1, 11.50),
        ("Iced Tea", 2, 3.25),
        ("Cheesecake Slice", 1, 8.00),
    ]
    c.setFont("Helvetica", 7)
    subtotal = 0.0
    for name, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        c.drawString(10, y, f"{name}")
        y -= 9
        c.drawString(14, y, f"{qty} x ${price:.2f}")
        c.drawRightString(width - 10, y, f"${line_total:.2f}")
        y -= 12

    c.line(10, y, width - 10, y)
    y -= 12

    tax_rate = 0.0
    tax = round(subtotal * tax_rate, 2)  # Oregon: no sales tax, but line still printed as $0.00
    total = round(subtotal + tax, 2)

    c.setFont("Helvetica", 7)
    c.drawString(10, y, "Subtotal")
    c.drawRightString(width - 10, y, f"${subtotal:.2f}")
    y -= 10
    c.drawString(10, y, "Tax (OR - none)")
    c.drawRightString(width - 10, y, f"${tax:.2f}")
    y -= 10
    c.setFont("Helvetica-Bold", 8)
    c.drawString(10, y, "TOTAL")
    c.drawRightString(width - 10, y, f"${total:.2f}")
    y -= 18

    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "Suggested tip 18-22% not included")
    y -= 10
    c.drawCentredString(width / 2, y, "Thanks for dining with us!")

    c.save()
    print(f"Wrote {path}  (subtotal={subtotal:.2f} tax={tax:.2f} total={total:.2f})")


def make_utility_invoice():
    path = f"{OUT}/invoice_utility.pdf"
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 72

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "Cascade Power & Light")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 72, y, "STATEMENT")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Account #: 7734-991")
    c.drawString(320, y, "Statement Date: 2026-06-01")
    y -= 14
    c.drawString(72, y, "Service Address: 55 Cedar Ln, Boise, ID")
    c.drawString(320, y, "Due Date: 2026-06-21")
    y -= 34

    # Single line item, no table header row this time - deliberately
    # different presentation from the tabular invoices above.
    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Electricity usage, May 2026 (1,240 kWh @ $0.1129/kWh)")
    c.drawRightString(width - 72, y, "$140.00")
    y -= 30
    c.line(72, y, width - 72, y)
    y -= 16

    subtotal = 140.00
    tax_rate = 0.05
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    c.drawString(380, y, "Subtotal:")
    c.drawRightString(width - 72, y, f"${subtotal:.2f}")
    y -= 16
    c.drawString(380, y, "Utility Tax (5%):")
    c.drawRightString(width - 72, y, f"${tax:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(380, y, "Amount Due:")
    c.drawRightString(width - 72, y, f"${total:.2f}")

    y -= 40
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(72, y, "Auto-pay enrolled customers: no action needed.")

    c.save()
    print(f"Wrote {path}  (subtotal={subtotal:.2f} tax={tax:.2f} total={total:.2f})")


def make_saas_invoice():
    path = f"{OUT}/invoice_saas.pdf"
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 72

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "Ledgerly Inc.")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 72, y, "INVOICE")
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawString(72, y, "SaaS billing | billing@ledgerly.example")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Invoice #: LG-99213")
    c.drawString(320, y, "Billing Date: 2026-06-15")
    y -= 14
    c.drawString(72, y, "Customer: Fenwick & Marsh LLP")
    c.drawString(320, y, "Due Date: 2026-06-29")
    y -= 34

    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Ledgerly Pro Plan - Annual Subscription (12 mo)")
    c.drawString(400, y, "Qty: 1")
    c.drawRightString(width - 72, y, "$1,188.00")
    y -= 30
    c.line(72, y, width - 72, y)
    y -= 16

    subtotal = 1188.00
    tax_rate = 0.0
    tax = 0.0
    total = subtotal

    c.drawString(380, y, "Subtotal:")
    c.drawRightString(width - 72, y, f"${subtotal:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(380, y, "Total:")
    c.drawRightString(width - 72, y, f"${total:.2f}")
    y -= 20
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(72, y, "Tax: N/A - digital service, tax-exempt jurisdiction.")

    y -= 30
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(72, y, "Renews automatically unless cancelled 7 days before the billing date.")

    c.save()
    print(f"Wrote {path}  (subtotal={subtotal:.2f}, tax=N/A text (not a number), total={total:.2f})")


def make_hardware_receipt():
    path = f"{OUT}/receipt_hardware.pdf"
    page_size = (3.2 * inch, 8.0 * inch)
    c = canvas.Canvas(path, pagesize=page_size)
    width, height = page_size
    y = height - 30

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "BUILDRIGHT HARDWARE")
    y -= 12
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "990 Industrial Pkwy, Denver, CO")
    y -= 18

    c.setFont("Helvetica", 7)
    c.drawString(10, y, "Trans #: 552017")
    y -= 10
    c.drawString(10, y, "Date: 06/18/2026  10:47")
    y -= 16

    c.line(10, y, width - 10, y)
    y -= 12

    items = [
        ("Cordless Drill Kit", 1, 79.99),
        ("Drill Bit Set 20pc", 1, 14.99),
        ("Wood Screws 1in (100ct)", 2, 5.49),
        ("Safety Glasses", 1, 6.25),
    ]
    c.setFont("Helvetica", 7)
    subtotal = 0.0
    for name, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        c.drawString(10, y, f"{name}")
        y -= 9
        c.drawString(14, y, f"{qty} x ${price:.2f}")
        c.drawRightString(width - 10, y, f"${line_total:.2f}")
        y -= 12

    c.line(10, y, width - 10, y)
    y -= 12

    tax_rate = 0.073
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    c.setFont("Helvetica", 7)
    c.drawString(10, y, "Subtotal")
    c.drawRightString(width - 10, y, f"${subtotal:.2f}")
    y -= 10
    c.drawString(10, y, "Sales Tax 7.3%")
    c.drawRightString(width - 10, y, f"${tax:.2f}")
    y -= 10
    c.setFont("Helvetica-Bold", 8)
    c.drawString(10, y, "TOTAL")
    c.drawRightString(width - 10, y, f"${total:.2f}")
    y -= 18

    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "Paid by MASTERCARD ****2290")
    y -= 10
    c.drawCentredString(width / 2, y, "Returns accepted within 30 days w/ receipt.")

    c.save()
    print(f"Wrote {path}  (subtotal={subtotal:.2f} tax={tax:.2f} total={total:.2f})")


if __name__ == "__main__":
    make_invoice()
    make_receipt()
    make_purchase_order()
    make_freelance_invoice()
    make_diner_receipt()
    make_utility_invoice()
    make_saas_invoice()
    make_hardware_receipt()
