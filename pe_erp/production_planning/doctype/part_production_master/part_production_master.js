// Copyright (c) 2026, Shaili Parikh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Part Production Master", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Part Production Master', {

    refresh: function(frm) {
        frm.clear_intro();
        if (frm.doc.total_cycle_time) {
            frm.set_intro(
                `Total Cycle Time: ${frm.doc.total_cycle_time} mins`,
                "blue"
            );
        }
    },

    foundry_cycle_time: function(frm) {
        calculate_total(frm);
    },

    machining_cycle_time: function(frm) {
        calculate_total(frm);
    },

    dispatch_cycle_time: function(frm) {
        calculate_total(frm);
    },

    part: function(frm) {
        if (frm.doc.part) {
            frappe.call({
                method: "pe_erp.api.api.get_part_basic_details",
                args: { part: frm.doc.part },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(
                            `Selected Part: ${r.message.part_name}`
                        );
                    }
                }
            });
        }
    }
});

function calculate_total(frm) {
    let total =
        (frm.doc.foundry_cycle_time || 0) +
        (frm.doc.machining_cycle_time || 0) +
        (frm.doc.dispatch_cycle_time || 0);

    frm.set_value("total_cycle_time", total);
}