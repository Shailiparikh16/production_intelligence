// Copyright (c) 2026, Shaili Parikh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Production Daily Log", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Production Daily Log', {

    production_plan: function(frm) {
        fetch_planned_qty(frm);
    },

    shift: function(frm) {
        fetch_planned_qty(frm);
    },

    dispatched_qty: function(frm) {
        calculate_backlog(frm);
    },

    refresh: function(frm) {
        calculate_backlog(frm);
    }
});


// 🔷 Fetch Planned Qty (Realtime)
function fetch_planned_qty(frm) {

    if (!(frm.doc.production_plan && frm.doc.shift)) return;

    frappe.call({
        method: "pe_erp.api.api.get_planned_qty",
        args: {
            plan: frm.doc.production_plan,
            shift: frm.doc.shift
        },
        callback: function(r) {

            if (r.message !== undefined) {
                frm.set_value("planned_qty", r.message);

                calculate_backlog(frm);
            }
        }
    });
}


// 🔷 Backlog Calculation (Realtime)
function calculate_backlog(frm) {

    let planned = frm.doc.planned_qty || 0;
    let dispatched = frm.doc.dispatched_qty || 0;

    let backlog = planned - dispatched;

    frm.set_value("backlog_qty", backlog > 0 ? backlog : 0);
}
frappe.ui.form.on('Production Daily Log', {

    setup: function(frm) {

        frm.set_query("production_plan", function() {
            return {
                filters: {
                    part: frm.doc.part   // ⚠️ your field name (rename to 'part' ideally)
                }
            };
        });
    }
});
frappe.ui.form.on('Production Daily Log', {

    production_plan: function(frm) {

        if (!frm.doc.production_plan) return;

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Part Production Plan",
                filters: { name: frm.doc.production_plan },
                fieldname: ["bottleneck_stage"]
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("division", r.message.bottleneck_stage);
                }
            }
        });
    }
});