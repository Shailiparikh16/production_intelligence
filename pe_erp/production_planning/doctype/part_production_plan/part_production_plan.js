// Copyright (c) 2026, Shaili Parikh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Part Production Plan", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Part Production Plan', {

    part: function(frm) {
        fetch_all_data(frm);
    },

    date: function(frm) {
        fetch_all_data(frm);
    },

    demand_qty: function(frm) {
        calculate_required(frm);
    },

    current_stock: function(frm) {
        calculate_required(frm);
    },

    refresh: function(frm) {
        fetch_all_data(frm);
    }
});


// 🔥 SINGLE API CALL (BEST PRACTICE)
function fetch_all_data(frm) {

    if (!(frm.doc.part && frm.doc.date)) return;

    frappe.call({
        method: "pe_erp.api.api.get_plan_inputs",
        args: {
            part: frm.doc.part,
            date: frm.doc.date
        },
        freeze: true,  // 🔥 UX improvement
        callback: function(r) {

            if (!r.message) return;

            let data = r.message;

            frm.set_value("demand_qty", data.demand || 0);
            frm.set_value("current_stock", data.stock || 0);

            calculate_required(frm);
        }
    });
}


// 🔷 Calculate Required Qty
function calculate_required(frm) {

    let demand = flt(frm.doc.demand_qty);
    let stock = flt(frm.doc.current_stock);

    let required = demand - stock;

    frm.set_value("required_qty", required > 0 ? required : 0);
}