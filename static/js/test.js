const priviledges = [
    {codename: "CanViewCalendar", description: "Calendar description here."},
    {codename: "CanViewCustomers", description: "Customers description here."},
    {codename: "CanViewProducts", description: "Products description here."},
];

const checkIfAuthorized = (privs, code) => {
    const res = privs.find( ({ codename }) => codename === code );

    if (res === undefined) {
        return false;
    };

    return true;
};

const results = checkIfAuthorized(priviledges, "CanViewSalesPerson");

console.log(results);
