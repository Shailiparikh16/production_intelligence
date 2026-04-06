# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PartProductionMaster(Document):

    def validate(self):
        self.validate_part()
        self.validate_cycle_times()
        self.calculate_total_cycle_time()
        self.prevent_duplicate()

    # 🔷 Validate Part
    def validate_part(self):
        if not self.part:
            frappe.throw("Part is mandatory")

        part_doc = frappe.get_doc("Parts Master", self.part)

        if not part_doc.is_active:
            frappe.throw(f"Part {self.part} is inactive")

    # 🔷 Validate Cycle Times
    def validate_cycle_times(self):
        fields = [
            ("foundry_cycle_time", "Foundry Cycle Time"),
            ("machining_cycle_time", "Machining Cycle Time"),
            ("dispatch_cycle_time", "Dispatch Cycle Time"),
        ]

        for field, label in fields:
            value = self.get(field) or 0

            if value < 0:
                frappe.throw(f"{label} cannot be negative")

    # 🔷 Calculate Total Cycle Time + Bottleneck
    def calculate_total_cycle_time(self):
        foundry = self.foundry_cycle_time or 0
        machining = self.machining_cycle_time or 0
        dispatch = self.dispatch_cycle_time or 0

        self.total_cycle_time = foundry + machining + dispatch

        if self.total_cycle_time <= 0:
            frappe.throw("Total Cycle Time must be greater than 0")

        # 🔥 Bottleneck Detection
        stages = {
            "Foundry": foundry,
            "Machining": machining,
            "Dispatch": dispatch
        }

        self.bottleneck_stage = max(stages, key=stages.get)

    # 🔷 Prevent Duplicate Entry
    def prevent_duplicate(self):
        existing = frappe.db.exists(
            "Part Production Master",
            {
                "part": self.part,
                "name": ["!=", self.name]
            }
        )

        if existing:
            frappe.throw(f"Production Master already exists for Part: {self.part}")
