const calculateTotal = (price, tax) => {
    return price + tax;
};

// BUG: Calling a function that doesn't exist
console.log(calculate_Total(100, 10));