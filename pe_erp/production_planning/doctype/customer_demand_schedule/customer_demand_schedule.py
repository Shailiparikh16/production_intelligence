# Copyright (c) 2026, Shaili Parikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import formatdate
import re


class CustomerDemandSchedule(Document):

    # 🔷 Auto Name
    def autoname(self):

        if not self.customer or not self.schedule_date:
            frappe.throw("Customer and Schedule Date are required")

        # 🔥 Clean customer name (no spaces/special chars)
        customer_clean = re.sub(r'[^A-Za-z0-9]', '', self.customer).upper()

        # 🔥 Format date
        date_str = formatdate(self.schedule_date, "yyyyMMdd")

        # 🔥 Final Name
        self.name = frappe.model.naming.make_autoname(
            f"{customer_clean}-{date_str}-.###"
        )

    # 🔷 Validation (prevent duplicates)
    def validate(self):

        exists = frappe.db.exists(
            "Customer Demand Schedule",
            {
                "customer": self.customer,
                "schedule_date": self.schedule_date,
                "name": ["!=", self.name]
            }
        )

        if exists:
            frappe.throw("Demand Schedule already exists for this Customer and Date")