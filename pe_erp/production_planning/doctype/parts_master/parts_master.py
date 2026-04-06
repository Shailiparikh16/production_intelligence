# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartsMaster(Document):

    def validate(self):
        # self.validate_mandatory_fields()
        # self.validate_unique_part_code()
        self.set_defaults()

    def validate_mandatory_fields(self):
        if not self.part_code:
            frappe.throw("Part Code is required")

        if not self.part_name:
            frappe.throw("Part Name is required")

    def validate_unique_part_code(self):
        existing = frappe.db.exists(
            "Parts Master",
            {"part_code": self.part_code, "name": ["!=", self.name]}
        )
        if existing:
            frappe.throw(f"Part Code '{self.part_code}' already exists")

    def set_defaults(self):
        if not self.uom:
            self.uom = "Nos"

        if self.standard_rate and self.standard_rate < 0:
            frappe.throw("Standard Rate cannot be negative")

        if not self.part_type:
            self.part_type = "Raw"

    def before_save(self):
        # Auto format part code (uppercase, trimmed)
        if self.part_code:
            self.part_code = self.part_code.strip().upper()

    def on_update(self):
        # Optional: Log update or trigger downstream updates
        frappe.logger().info(f"Parts Master updated: {self.part_code}")
