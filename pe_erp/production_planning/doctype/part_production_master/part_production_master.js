frappe.ui.form.on('Part Production Master', {

    onload: function(frm) {
        calculate_outputs(frm);
    }
});


frappe.ui.form.on('Part Operations', {

    cycle_time: debounce(function(frm) {
        calculate_outputs(frm);
    }, 300),

    efficiency: debounce(function(frm) {
        calculate_outputs(frm);
    }, 300),

    operation: function(frm) {
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

    // 🔷 Get shift hours dynamically (fallback = 8)
    let working_hours = frm.doc.working_hours || 7.5;
    let available_minutes = working_hours * 60;

    let min_output = null;
    let bottleneck = null;

    (frm.doc.operations || []).forEach(row => {

        row.output = 0;
        row.is_bottleneck = 0;

        if (row.cycle_time && row.cycle_time > 0) {

            let efficiency = (row.efficiency || 100) / 100;

            let effective_minutes = available_minutes * efficiency;

            let raw_output = effective_minutes / row.cycle_time;

            row.output = parseFloat(raw_output.toFixed(2));

            // 🔥 Compare using RAW (not rounded)
            if (min_output === null || raw_output < min_output) {
                min_output = raw_output;
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

    // 🔥 Set parent fields
    frm.set_value("capacityshift", min_output ? parseFloat(min_output.toFixed(2)) : 0);
    frm.set_value("bottleneck_operation", bottleneck || "");
    frm.set_value("total_operations", (frm.doc.operations || []).length);

    frm.refresh_field("operations");
}


// 🔥 Debounce utility (prevents lag)
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
frappe.ui.form.on('Part Production Master', {

    part: function(frm) {
        if (frm.doc.part) {
            frappe.db.get_value(
                "Parts Master",
                frm.doc.part,
                "part_name"
            ).then(r => {
                if (r.message) {
                    frm.set_value("part_name", r.message.part_name);
                }
            });
        }
    }
});