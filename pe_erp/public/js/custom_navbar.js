frappe.router.on('change', () => {
    const route = frappe.get_route();

    // If user lands on home
    if (route.length === 1 && route[0] === 'home') {
        frappe.set_route('app', 'pe-erp');
    }
});