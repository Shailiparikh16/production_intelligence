# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProductionDailyLog(Document):

    def validate(self):
        self.validate_inputs()
        self.fetch_planned_qty()
        self.calculate_backlog()

    # 🔷 Validate
    def validate_inputs(self):
        if not self.part:
            frappe.throw("Part is required")

        if not self.date:
            frappe.throw("Date is required")

        if (self.produced_qty or 0) < 0:
            frappe.throw("Produced Qty cannot be negative")

        if (self.dispatched_qty or 0) < 0:
            frappe.throw("Dispatched Qty cannot be negative")

    # 🔷 Fetch Planned Qty from Production Plan
    def fetch_planned_qty(self):

        if not self.production_plan or not self.shift:
            return

        plan = frappe.get_doc("Part Production Plan", self.production_plan)

        for row in plan.part_production_plan_shift_detail:
            if row.shift == self.shift:
                self.planned_qty = row.planned_qty
                return

        # If not found
        self.planned_qty = 0

    # 🔷 Calculate Backlog
    def calculate_backlog(self):

        planned = self.planned_qty or 0
        dispatched = self.dispatched_qty or 0

        backlog = planned - dispatched

        self.backlog_qty = backlog if backlog > 0 else 0
