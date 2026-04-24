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
    let total_cycle_time = 0;


    (frm.doc.operations || []).forEach(row => {

        row.output = 0;
        // row.is_bottleneck = 0;

        if (row.cycle_time && row.cycle_time > 0) {

            let raw_output = available_minutes / row.cycle_time;
            row.output = Math.floor(raw_output);
            total_cycle_time += row.cycle_time;

        }
    });

    // 🔥 Mark bottleneck
    // (frm.doc.operations || []).forEach(row => {
    //     if (row.operation === bottleneck) {
    //         row.is_bottleneck = 1;
    //     }
    // });

    // 🔥 Set parent fields
  let outputs = [];

(frm.doc.operations || []).forEach(row => {
    if (row.output && row.output > 0) {
        outputs.push(row.output);
    }
});

let capacity = 0;

if (outputs.length > 0) {
    capacity = Math.min(...outputs);
}

    frm.set_value("capacityshift", capacity);

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