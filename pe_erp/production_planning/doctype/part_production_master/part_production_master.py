# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class PartProductionMaster(Document):

    def validate(self):
        self.fetch_part_name()
        self.calculate_operations()

    # 🔷 Fetch Part Name
    def fetch_part_name(self):
        if self.part:
            self.part_name = frappe.db.get_value(
                "Parts Master",
                self.part,
                "part_name"
            )

    # 🔷 Main Logic
    def calculate_operations(self):

        available_minutes = 8 * 60  # 1 shift (you can make dynamic later)

        min_output = None
        bottleneck_op = None

        for row in self.operations:

            # Reset defaults
            row.output = 0
            row.is_bottleneck = 0

            if not row.cycle_time or row.cycle_time <= 0:
                continue

            # 🔥 Efficiency (default 100%)
            efficiency = (row.efficiency or 100) / 100

            # 🔥 Calculate output
            effective_minutes = available_minutes * efficiency
            output = effective_minutes / row.cycle_time

            row.output = round(output, 2)

            # 🔥 Find bottleneck (minimum output)
            if min_output is None or output < min_output:
                min_output = output
                bottleneck_op = row.operation

        # 🔥 Assign parent values
        if min_output is not None:
            self.capacityshift = round(min_output, 2)
            self.bottleneck_operation = bottleneck_op
        else:
            self.capacityshift = 0
            self.bottleneck_operation = None

        # 🔥 Mark bottleneck row
        for row in self.operations:
            if row.operation == bottleneck_op:
                row.is_bottleneck = 1

        # 🔥 Total operations
        self.total_operations = len(self.operations)
