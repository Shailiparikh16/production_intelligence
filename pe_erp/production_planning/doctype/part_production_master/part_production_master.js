frappe.ui.form.on('Part Production Master', {

    refresh: function(frm) {
        calculate_outputs(frm);
    },

    onload: function(frm) {
        calculate_outputs(frm);
    }
});


frappe.ui.form.on('Part Operations', {

    cycle_time: function(frm, cdt, cdn) {
        calculate_outputs(frm);
    },

    efficiency: function(frm, cdt, cdn) {   // 🔥 NEW
        calculate_outputs(frm);
    },

    operation: function(frm, cdt, cdn) {
        calculate_outputs(frm);
    },

    operations_add: function(frm) {
        calculate_outputs(frm);
    },

    operations_remove: function(frm) {
        calculate_outputs(frm);
    }
});


// 🔥 MAIN FUNCTION
function calculate_outputs(frm) {

    let available_minutes = 8 * 60;  // can make dynamic later
    let min_output = null;
    let bottleneck = null;

    (frm.doc.operations || []).forEach(row => {

        // reset
        row.output = 0;
        row.is_bottleneck = 0;

        if (row.cycle_time && row.cycle_time > 0) {

            // 🔥 Efficiency (default 100%)
            let efficiency = (row.efficiency || 100) / 100;

            // 🔥 Effective time
            let effective_minutes = available_minutes * efficiency;

            // 🔥 Output
            let output = effective_minutes / row.cycle_time;

            row.output = parseFloat(output.toFixed(2));

            // 🔥 Find bottleneck
            if (min_output === null || row.output < min_output) {
                min_output = row.output;
                bottleneck = row.operation;
            }
        }
    });

    // 🔥 Mark bottleneck
    (frm.doc.operations || []).forEach(row => {
        if (row.operation === bottleneck) {
            row.is_bottleneck = 1;
        }
    });

    // 🔥 Set parent values
    frm.set_value("capacityshift", min_output ? parseFloat(min_output.toFixed(2)) : 0);
    frm.set_value("bottleneck_operation", bottleneck || "");

    // 🔥 Total operations
    frm.set_value("total_operations", (frm.doc.operations || []).length);

    frm.refresh_field("operations");
}