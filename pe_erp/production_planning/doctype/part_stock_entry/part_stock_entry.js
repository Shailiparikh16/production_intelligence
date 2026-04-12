// Copyright (c) 2026, Shaili Parikh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Part Stock Entry", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('Part Stock Entry', {
//     entry_type: function(frm) {

//         if (frm.doc.entry_type === "INWARD (Production)") {
//             frm.set_df_property("source_warehouse", "reqd", 0);
//             frm.set_df_property("target_warehouse", "reqd", 1);
//         }

//         else if (frm.doc.entry_type === "OUTWARD (Dispatch)") {
//             frm.set_df_property("source_warehouse", "reqd", 1);
//             frm.set_df_property("target_warehouse", "reqd", 0);
//         }

//         else if (frm.doc.entry_type === "TRANSFER") {
//             frm.set_df_property("source_warehouse", "reqd", 1);
//             frm.set_df_property("target_warehouse", "reqd", 1);
//         }
//     }
// });