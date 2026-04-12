# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import formatdate


class PartStockEntry(Document):

    # 🔷 AUTO NAME
    def autoname(self):

        if not self.entry_type or not self.quantity or not self.posting_date:
            frappe.throw("Entry Type, Quantity and Posting Date are required")

        entry_map = {
            "INWARD (Production)": "IN",
            "OUTWARD (Dispatch)": "OUT",
            "ADJUSTMENT": "ADJ"
        }

        prefix = entry_map.get(self.entry_type, "ENT")
        date_str = formatdate(self.posting_date, "yyyyMMdd")
        qty = int(self.quantity)

        self.name = frappe.model.naming.make_autoname(
            f"{prefix}-{qty}-{date_str}-.##"
        )

    # 🔷 VALIDATION
    def validate(self):
        if not self.part:
            frappe.throw("Part is required")

        if not self.quantity or self.quantity <= 0:
            frappe.throw("Quantity must be greater than 0")

        if self.entry_type not in [
            "INWARD (Production)",
            "OUTWARD (Dispatch)",
            "ADJUSTMENT"
        ]:
            frappe.throw("Invalid Entry Type")

    # 🔷 ON SUBMIT
    def on_submit(self):
        self.update_stock()

    # 🔷 MAIN LOGIC
    def update_stock(self):

        if self.entry_type == "INWARD (Production)":
            self.update_inventory(self.part, self.quantity)

        elif self.entry_type == "OUTWARD (Dispatch)":
            self.update_inventory(self.part, -self.quantity)

        elif self.entry_type == "ADJUSTMENT":
            self.update_inventory(self.part, self.quantity)

    # 🔷 INVENTORY UPDATE
    def update_inventory(self, part, qty):

        record = frappe.db.get_value(
            "Part Inventory",
            {"part": part},
            ["name", "current_stock", "reserved_qty"],
            as_dict=True
        )

        if record:
            current = record.current_stock or 0
            reserved = record.reserved_qty or 0

            new_stock = current + qty

            # 🔴 Prevent negative stock
            if new_stock < 0:
                frappe.throw(f"Insufficient stock for Part {part}")

            available = new_stock - reserved

            frappe.db.set_value(
                "Part Inventory",
                record.name,
                {
                    "current_stock": new_stock,
                    "available_qty": available
                }
            )

        else:
            # 🔥 First-time stock creation
            if qty < 0:
                frappe.throw("Cannot create negative stock")

            frappe.get_doc({
                "doctype": "Part Inventory",
                "part": part,
                "current_stock": qty,
                "reserved_qty": 0,
                "available_qty": qty
            }).insert(ignore_permissions=True)