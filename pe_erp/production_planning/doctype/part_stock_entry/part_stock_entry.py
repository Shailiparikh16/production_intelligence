# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document



class PartStockEntry(Document):

    def validate(self):
        self.validate_inputs()

    def on_submit(self):
        self.update_stock()

    # 🔷 VALIDATIONS
    def validate_inputs(self):
        if not self.part:
            frappe.throw("Part is required")

        if not self.quantity or self.quantity <= 0:
            frappe.throw("Quantity must be greater than 0")

        if self.entry_type == "INWARD (Production)" and not self.target_warehouse:
            frappe.throw("Target Warehouse is required for INWARD")

        if self.entry_type == "OUTWARD (Dispatch)" and not self.source_warehouse:
            frappe.throw("Source Warehouse is required for OUTWARD")

        if self.entry_type == "TRANSFER":
            if not self.source_warehouse or not self.target_warehouse:
                frappe.throw("Both warehouses required for TRANSFER")

            if self.source_warehouse == self.target_warehouse:
                frappe.throw("Source and Target warehouse cannot be same")

    # 🔷 MAIN LOGIC
    def update_stock(self):

        if self.entry_type == "INWARD (Production)":
            self.update_inventory(self.part, self.quantity)

        elif self.entry_type == "OUTWARD (Dispatch)":
            self.update_inventory(self.part, -self.quantity)

        elif self.entry_type == "TRANSFER":
            self.update_inventory(self.part, -self.quantity)  # remove
            self.update_inventory(self.part, self.quantity)   # add

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