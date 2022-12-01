let form = document.querySelector("#form");
let orderForm = document.querySelector("#orderForm");
let sellcompletebtn = document.querySelector("#sellcompletebtn");

class addCart {
    constructor(productname, productid, price, quantity) {
        this.productname = productname;
        this.productid = productid;
        this.price = price;
        this.quantity = quantity;
    }
}

class orderComplete {
    constructor(subtotal, discount, total) {
        this.subtotal = subtotal;
        this.discount = discount;
        this.total = total;
    }
}

// ADD FORM TO TABLE
// UI ELEMENT
class UI {
    static addBookList(product) {
        if (
            productname.value &&
            productid.value &&
            price.value &&
            quantity.value
        ) {
            let tbody = document.querySelector("#carttable");
            let tr = document.createElement("tr");

            let unittotal =
                parseFloat(product.price) * parseFloat(product.quantity);

            tr.innerHTML = `
            <td>${product.productname}</td>
            <td>${product.productid}</td>
            <td>${product.price}</td>
            <td>${product.quantity}</td>
            <td class="productprice">${unittotal}</td>
            <td>
                <a href="#" class="btn btn-sm btn-danger deleteproductbtn"> Delete </a>
            </td>`;
            tbody.appendChild(tr);
        }
    }

    static clearForm() {
        productname.value = "";
        productid.value = "";
        price.value = "";
        quantity.value = "";
    }

    // static showalert(message, className) {
    //     let div = document.createElement('div')
    //     div.className = `status alert ${className}`
    //     div.appendChild(document.createTextNode(message));
    //     let container = document.querySelector('.container')
    //     let form = document.querySelector('form')

    //     container.insertBefore(div, form)

    //     setTimeout(() => {
    //         document.querySelector('.alert').remove()
    //     }, 3000)
    // }

    static deleteProductFromCart(target) {
        if (target.hasAttribute("href")) {
            target.parentElement.parentElement.remove();
            Store.removeProduct(
                target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.textContent.trim()
            );
            payment();
            // UI.showalert("Book Deleted ✅", "success")
        }
    }
}

class Store {
    static getProducts() {
        let products;
        if (localStorage.getItem("products") === null) {
            products = [];
        } else {
            products = JSON.parse(localStorage.getItem("products"));
        }

        return products;
    }

    static getCashier() {
        let cashier;
        if (localStorage.getItem("cashier") === null) {
            cashier = [];
        } else {
            cashier = JSON.parse(localStorage.getItem("cashier"));
        }

        return cashier;
    }

    static getSell() {
        let sell;
        if (localStorage.getItem("sell") === null) {
            sell = [];
        } else {
            sell = JSON.parse(localStorage.getItem("sell"));
        }

        return sell;
    }

    static addProduct(product) {
        let products = Store.getProducts();
        products.push(product);

        localStorage.setItem("products", JSON.stringify(products));
    }

    static removeProduct(productid) {
        let products = Store.getProducts();

        products.forEach((product, index) => {
            if (product.productid === productid) {
                products.splice(index, 1);
            }
        });

        localStorage.setItem("products", JSON.stringify(products));
    }

    static subTotal() {
        let allproductprice = document.querySelectorAll(".productprice");
        let result = 0;
        allproductprice.forEach((number) => {
            console.log(`we have ${number.innerHTML}`);
            result += parseFloat(number.innerText);
        });

        return result;
    }

    static totalammount(subtotal, discount) {
        let totalammount = subtotal - discount;

        return totalammount;
    }

    static displayBooks() {
        let products = Store.getProducts();
        let productexist = document.querySelector("#carttable");

        if (localStorage.getItem("products") === null) {
            try {
                products.forEach((product) => {
                    UI.addBookList(product);
                });
            } catch (error) {
                alert(error);
            }
        } else {
            alert("something went wrong. please reload the page");
        }
    }
}

// PAYMENT CALCULATE
const payment = () => {
    let subtotalel = document.querySelector("#subtotal"),
        discountel = document.querySelector("#discount"),
        totalammountel = document.querySelector("#totalammount");

    subtotalvalue = parseFloat(subtotalel.value);
    discountvalue = parseFloat(discountel.value);

    // SUBTOTAL CALCULATE
    let subtotalresult = Store.subTotal();
    let total = Store.totalammount(subtotalresult, discountvalue);
    subtotalel.value = subtotalresult;

    // TOTAL AMMOUNT CALCULATE
    discountel.addEventListener("keyup", () => {
        discountvalue = parseFloat(discountel.value);
        // console.log(discountvalue)
        let total = Store.totalammount(subtotalresult, discountvalue);
        totalammountel.value = total;
    });
    totalammountel.value = total;
};

form.addEventListener("submit", (e) => {
    e.preventDefault();

    // GETTING ALL THE ELEMENTS
    let productname = document.querySelector("#productname").value,
        productid = document.querySelector("#productid").value,
        price = document.querySelector("#price").value,
        quantity = document.querySelector("#quantity").value;

    // ADD NEW PRODUCT
    let addNewProduct = new addCart(productname, productid, price, quantity);
    Store.addProduct(addNewProduct);

    // DISPLAYING PRODUCTS
    UI.addBookList(addNewProduct);
    UI.clearForm();

    // adding item to localstorage
    payment();
});

// REMOVE A PRODUCT WHEN CLICKED DELETE BUTTON
let removebutton = document.querySelector("#carttable");
removebutton.addEventListener("click", (e) => {
    UI.deleteProductFromCart(e.target);
});

// COMPLETE ORDER PROCESS
orderForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let productname = document.querySelector("#productname").value,
        productid = document.querySelector("#productid").value,
        price = document.querySelector("#price").value,
        quantity = document.querySelector("#quantity").value;

    let addNewProduct = new addCart(productname, productid, price, quantity);

    Store.addProduct(addNewProduct);
});

// SUBMIT ALL DATA TO DATABASE
sellcompletebtn.addEventListener("click", () => {
    allproduct = Store.getProducts();

    let cashier = new orderComplete(
        subtotal.value,
        discount.value,
        totalammount.value
    );

    localStorage.setItem("cashier", JSON.stringify(cashier));

    let sell = {
        products: allproduct,
        cashier: cashier,
    };
    localStorage.setItem("sell", JSON.stringify(sell));

    let getsell = localStorage.getItem("sell");

    fetch("https://httpbin.org/post", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(getsell),
    })
        .then((response) => response.json())
        .then((data) => console.log(data.json));
});

document.addEventListener("DOMContentLoaded", () => {
    localStorage.removeItem("products");
    Store.displayBooks();
});
