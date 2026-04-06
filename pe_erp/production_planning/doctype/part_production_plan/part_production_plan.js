// Copyright (c) 2026, Shaili Parikh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Part Production Plan", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Part Production Plan', {

    part: function(frm) {
        if (frm.doc.part) {
            frappe.call({
                method: "pe_erp.api.api.get_part_basic_details",
                args: { part: frm.doc.part },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(`Part: ${r.message.part_name}`);
                    }
                }
            });
        }
    },

    demand_qty: function(frm) {
        calculate_required(frm);
    },

    current_stock: function(frm) {
        calculate_required(frm);
    }
});

function calculate_required(frm) {
    let required = (frm.doc.demand_qty || 0) - (frm.doc.current_stock || 0);
    frm.set_value("required_qty", required > 0 ? required : 0);
}