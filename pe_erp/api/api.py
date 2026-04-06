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
@frappe.whitelist()
def get_total_demand(part, date):
    demand = frappe.db.sql("""
        SELECT SUM(dp.quantity)
        FROM `tabCustomer Demand Schedule` cds
        JOIN `tabDemand Parts` dp 
            ON dp.parent = cds.name
        WHERE cds.schedule_date = %s
        AND dp.part = %s
    """, (date, part))

    return demand[0][0] if demand and demand[0][0] else 0

@frappe.whitelist()
def get_current_stock(part):
    stock = frappe.db.get_value(
        "Part Inventory",
        {"part": part},
        "available_qty"
    )

    return stock or 0
@frappe.whitelist()
def get_plan_inputs(part, date):

    # 🔷 Get Demand
    demand = frappe.db.sql("""
        SELECT SUM(dp.quantity)
        FROM `tabCustomer Demand Schedule` cds
        JOIN `tabDemand Parts` dp ON dp.parent = cds.name
        WHERE cds.schedule_date = %s
        AND dp.part = %s
        AND cds.docstatus < 2
    """, (date, part))

    demand_qty = demand[0][0] if demand and demand[0][0] else 0

    # 🔷 Get Stock
    stock = frappe.db.get_value(
        "Part Inventory",
        {"part": part},
        "current_stock"
    ) or 0

    return {
        "demand": demand_qty,
        "stock": stock
    }
@frappe.whitelist()
def get_planned_qty(plan, shift):

    doc = frappe.get_doc("Part Production Plan", plan)

    for row in doc.part_production_plan_shift_detail:
        if row.shift == shift:
            return row.planned_qty

    return 0