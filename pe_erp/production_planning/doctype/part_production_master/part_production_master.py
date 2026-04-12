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

    # 🔷 Main Logic (NO SHIFT DEPENDENCY)
    def calculate_operations(self):

        available_minutes = 7.5 * 60  # 450

        min_output = None
        bottleneck_op = None
        total_time = 0  # 🔥 NEW

        for row in self.operations:

            row.output = 0
            row.is_bottleneck = 0

            if not row.cycle_time or row.cycle_time <= 0:
                continue

            # 🔥 Add to total time
            total_time += row.cycle_time

            # 🔥 Output calculation (NO efficiency)
            output = available_minutes / row.cycle_time
            row.output = round(output, 2)

            if min_output is None or output < min_output:
                min_output = output
                bottleneck_op = row.operation

        # 🔥 Assign parent values
        self.capacityshift = round(min_output, 2) if min_output else 0
        self.bottleneck_operation = bottleneck_op

        # 🔥 Mark bottleneck
        for row in self.operations:
            if row.operation == bottleneck_op:
                row.is_bottleneck = 1

        # 🔥 Total operations
        self.total_operations = len(self.operations)

        # 🔥 Total Time To Produce
        self.total_time_to_produce = round(total_time, 2)