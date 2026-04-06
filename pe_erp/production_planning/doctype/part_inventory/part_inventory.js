// Copyright (c) 2026, Shaili Parikh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Part Inventory", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('Part Inventory', {

//     current_stock: function(frm) {
//         calculate_available_qty(frm);
//     },

//     reserved_qty: function(frm) {
//         calculate_available_qty(frm);
//     },

//     refresh: function(frm) {
//         calculate_available_qty(frm);
//     }
// });

// function calculate_available_qty(frm) {
//     let current = frm.doc.current_stock || 0;
//     let reserved = frm.doc.reserved_qty || 0;

//     let available = current - reserved;

//     frm.set_value("available_qty", available);
// }
frappe.ui.form.on('Part Inventory', {
    refresh: function(frm) {
        frm.reload_doc();  // 🔥 auto reload on open/refresh
    }
});