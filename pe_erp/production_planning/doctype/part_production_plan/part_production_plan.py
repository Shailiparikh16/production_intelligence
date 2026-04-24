# # Copyright (c) 2026, Shaili Parikh
# # For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import formatdate
import re
import math



class PartProductionPlan(Document):

    def autoname(self):

        if not self.part or not self.date:
            frappe.throw("Part and Date are required for naming")

        # 🔷 Clean part name/code
        part_clean = re.sub(r'[^A-Za-z0-9]', '', self.part).upper()

        # 🔷 Format date
        date_str = formatdate(self.date, "yyyyMMdd")

        # 🔷 Final Name
        self.name = frappe.model.naming.make_autoname(
            f"PPP-{part_clean}-{date_str}-.###"
        )

    def validate(self):
        self.validate_inputs()
        self.fetch_demand()
        self.fetch_current_stock()
        self.fetch_capacity_from_master()
        self.calculate_required_qty()
        self.calculate_required_shifts()
        self.generate_shift_plan()

    # 🔷 Validate Inputs
    def validate_inputs(self):
        if not self.part:
            frappe.throw("Part is required")

    # 🔷 Fetch Demand
    def fetch_demand(self):
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

    # 🔷 Fetch Stock
    def fetch_current_stock(self):
        stock = frappe.db.get_value(
            "Part Inventory",
            {"part": self.part},
            "current_stock"
        )

        self.current_stock = stock or 0

    # 🔥 NEW: Fetch Capacity from Master
    def fetch_capacity_from_master(self):

        master = frappe.get_doc(
            "Part Production Master",
            {"part": self.part}
        )

        if not master.capacityshift:
            frappe.throw("Production per Shift not defined in Part Production Master")

        self.capacity_per_shift = math.floor(master.capacityshift)
        #self.bottleneck_stage = master.bottleneck_operation

    # 🔷 Required Qty
    def calculate_required_qty(self):
        self.required_qty = max(
            (self.demand_qty or 0) - (self.current_stock or 0),
            0
        )

    # 🔷 Required Shifts
    def calculate_required_shifts(self):

        if self.capacity_per_shift:
            self.required_shifts = math.ceil(self.required_qty / self.capacity_per_shift)
        else:
            self.required_shifts = 0

    # 🔥 FINAL: Generate Shift Plan
    def generate_shift_plan(self):

        self.part_production_plan_shift_detail = []

        if not self.required_qty or not self.capacity_per_shift:
            return

        remaining_qty = self.required_qty

        shifts = frappe.get_all(
            "Shift Configuration",
            fields=["name", "sequence"],
            order_by="sequence"
        )

        if not shifts:
            frappe.throw("No Shift Configuration found")

        i = 0

        while remaining_qty > 0:

            shift = shifts[i % len(shifts)]

            qty = min(self.capacity_per_shift, remaining_qty)

            self.append("part_production_plan_shift_detail", {
                "shift": shift.name,
                "planned_qty": int(math.floor(qty))
            })

            remaining_qty -= qty
            i += 1