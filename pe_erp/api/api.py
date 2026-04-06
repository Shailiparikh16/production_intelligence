import frappe

@frappe.whitelist()
def get_part_basic_details(part):
    doc = frappe.get_doc("Parts Master", part)

    return {
        "part_name": doc.part_name,
        "uom": doc.uom,
        "standard_rate": doc.standard_rate,
        "part_type": doc.part_type
    }