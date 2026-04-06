# Copyright (c) 2026, Shaili Parikh
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PartProductionPlan(Document):

    def validate(self):
        self.validate_inputs()
        self.fetch_inputs()  # 🔥 unified call
        self.fetch_capacity_from_master()
        self.calculate_required_qty()
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

    # 🔥 UNIFIED FETCH (Demand + Stock)
    def fetch_inputs(self):

        if not self.part or not self.date:
            return

        # 🔷 Demand
        demand = frappe.db.sql("""
            SELECT SUM(dp.quantity)
            FROM `tabCustomer Demand Schedule` cds
            JOIN `tabDemand Parts` dp 
                ON dp.parent = cds.name
            WHERE cds.schedule_date = %s
            AND dp.part = %s
            AND cds.docstatus < 2
        """, (self.date, self.part))

        self.demand_qty = demand[0][0] if demand and demand[0][0] else 0

        # 🔷 Stock
        stock = frappe.db.get_value(
            "Part Inventory",
            {"part": self.part},
            "current_stock"
        )

        self.current_stock = stock or 0

    # 🔷 Fetch Capacity from Master
    def fetch_capacity_from_master(self):

        master = frappe.db.get_value(
            "Part Production Master",
            {"part": self.part},
            ["capacityshift", "bottleneck_operation"],
            as_dict=True
        )

        if not master:
            frappe.throw(f"No Production Master found for Part {self.part}")

        self.capacity_per_shift = master.capacityshift or 0
        self.bottleneck_stage = master.bottleneck_operation

        if not self.capacity_per_shift:
            frappe.throw("Capacity not defined in Part Production Master")

    # 🔷 Required Qty
    def calculate_required_qty(self):
        self.required_qty = max(
            (self.demand_qty or 0) - (self.current_stock or 0),
            0
        )

    # 🔷 Required Shifts
    def calculate_required_shifts(self):
        if self.capacity_per_shift:
            self.required_shifts = round(
                self.required_qty / self.capacity_per_shift, 2
            )
        else:
            self.required_shifts = 0

    # 🔷 Generate Shift Plan (Optimized)
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

        for shift in shifts:
            if remaining_qty <= 0:
                break

            qty = min(self.capacity_per_shift, remaining_qty)

            self.append("part_production_plan_shift_detail", {
                "shift": shift.name,
                "planned_qty": round(qty, 2)
            })

            remaining_qty -= qty

        # 🔥 If still remaining → loop again
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