# Copyright (c) 2026, Shaili Parikh
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PartProductionPlan(Document):

    def validate(self):
        self.validate_inputs()
        self.fetch_cycle_time()
        self.calculate_required_qty()
        self.calculate_capacity()
        self.calculate_required_shifts()
        self.generate_shift_plan()

    # 🔷 Validate Inputs
    def validate_inputs(self):
        if not self.part:
            frappe.throw("Part is required")

        if (self.demand_qty or 0) < 0:
            frappe.throw("Demand Qty cannot be negative")

        if (self.current_stock or 0) < 0:
            frappe.throw("Current Stock cannot be negative")

    # 🔷 Fetch Cycle Time + Bottleneck
    def fetch_cycle_time(self):
        master = frappe.get_doc("Part Production Master", {"part": self.part})

        self.total_cycle_time = master.total_cycle_time
        self.bottleneck_stage = master.bottleneck_stage

        if not self.total_cycle_time:
            frappe.throw("Cycle time not defined for this part")

    # 🔷 Required Qty
    def calculate_required_qty(self):
        self.required_qty = max(
            (self.demand_qty or 0) - (self.current_stock or 0),
            0
        )

    # 🔷 Capacity Per Shift (ALL SHIFTS COMBINED)
    def calculate_capacity(self):
        shifts = frappe.get_all(
            "Shift Configuration",
            fields=["name", "working_hours", "efficiency"],
            order_by="name"
        )

        if not shifts:
            frappe.throw("No Shift Configuration found")

        total_capacity = 0

        for shift in shifts:
            available_minutes = shift.working_hours * 60 * (shift.efficiency / 100)

            if self.total_cycle_time:
                total_capacity += available_minutes / self.total_cycle_time

        self.capacity_per_shift = round(total_capacity, 2)

    # 🔷 Required Shifts
    def calculate_required_shifts(self):
        if self.capacity_per_shift:
            self.required_shifts = round(
                self.required_qty / self.capacity_per_shift, 2
            )
        else:
            self.required_shifts = 0

    # 🔷 Auto Generate Shift Plan (FIXED 🔥)
    def generate_shift_plan(self):
        self.part_production_plan_shift_detail = []

        if not self.required_qty or not self.capacity_per_shift:
            return

        shifts = frappe.get_all(
            "Shift Configuration",
            fields=["name"],
            order_by="name"
        )

        if not shifts:
            frappe.throw("No Shift Configuration found")

        remaining_qty = self.required_qty
        i = 0

        while remaining_qty > 0:
            shift = shifts[i % len(shifts)]

            qty = min(self.capacity_per_shift, remaining_qty)

            self.append("part_production_plan_shift_detail", {
                "shift": shift.name,
                "planned_qty": round(qty, 2)
            })

            remaining_qty -= qty
            i += 1