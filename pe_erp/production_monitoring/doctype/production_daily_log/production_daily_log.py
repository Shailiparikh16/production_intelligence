# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProductionDailyLog(Document):

    def validate(self):
        self.validate_inputs()
        self.fetch_planned_qty()
        self.calculate_backlog()
        self.validate_shift_in_plan()

    # 🔷 1. Validate Inputs
    def validate_inputs(self):

        if not self.part:
            frappe.throw("Part is required")

        if not self.date:
            frappe.throw("Date is required")

        if not self.shift:
            frappe.throw("Shift is required")

        if (self.produced_qty or 0) < 0:
            frappe.throw("Produced Qty cannot be negative")

        if (self.dispatched_qty or 0) < 0:
            frappe.throw("Dispatched Qty cannot be negative")

    # 🔷 2. Fetch Planned Qty from Production Plan
    def fetch_planned_qty(self):

        if not self.production_plan or not self.shift:
            self.planned_qty = 0
            return

        try:
            plan = frappe.get_doc("Part Production Plan", self.production_plan)

            logs_count = frappe.db.count(
                "Production Daily Log",
                {
                    "production_plan": self.production_plan,
                    "part": self.part,
                    "date": self.date,
                    "name": ["!=", self.name]
                }
            )

            plan_rows = sorted(plan.part_production_plan_shift_detail, key=lambda x: x.idx)

            if logs_count < len(plan_rows):
                self.planned_qty = int(plan_rows[logs_count].planned_qty)
            else:
                frappe.throw("All planned shifts are already completed for this Production Plan")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Production Daily Log Error")
            raise

    # 🔷 3. Get Previous Shift Backlog (CRITICAL LOGIC)
    def get_previous_backlog(self):

        if not self.part or not self.date or not self.shift:
            return 0

        try:
            current_shift_doc = frappe.get_doc("Shift Configuration", self.shift)
            current_sequence = getattr(current_shift_doc, "sequence", None)

            if current_sequence is None:
                return 0

            logs = frappe.get_all(
                "Production Daily Log",
                filters={
                    "part": self.part,
                    "date": self.date,
                    "name": ["!=", self.name]
                },
                fields=["backlog_qty", "shift"]
            )

            total_previous_backlog = 0

            for log in logs:

                try:
                    shift_doc = frappe.get_doc("Shift Configuration", log.shift)
                    seq = getattr(shift_doc, "sequence", None)

                    if seq is not None and seq < current_sequence:
                        total_previous_backlog += (log.backlog_qty or 0)

                except Exception:
                    continue

            return total_previous_backlog

        except Exception:
            return 0

    # 🔷 4. Calculate Backlog
    def calculate_backlog(self):

        planned = self.planned_qty or 0
        produced = self.produced_qty or 0

        # 🔥 NEW: carry forward backlog
        previous_backlog = self.get_previous_backlog()

        # store for UI/debug
        self.previous_backlog = previous_backlog

        # 🔥 effective plan
        effective_plan = planned + previous_backlog

        # 🔥 backlog based on production (NOT dispatch)
        backlog = effective_plan - produced

        self.backlog_qty = backlog if backlog > 0 else 0


    # 🔷 5. Validate Shift exists in Production Plan
    def validate_shift_in_plan(self):
        if not self.production_plan or not self.shift:
            return
        
        plan = frappe.get_doc("Part Production Plan", self.production_plan)

        valid_shifts = [row.shift for row in plan.part_production_plan_shift_detail]

        if self.shift not in valid_shifts:
            frappe.throw(f"Shift {self.shift} is not part of the Production Plan")