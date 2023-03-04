let form = document.querySelector("#form");
let orderForm = document.querySelector("#orderForm");
let sellcompletebtn = document.querySelector("#sellcompletebtn");
let newinvoiceid = document.querySelector("#newinvoiceid");
newinvoiceid.innerText = newinvoiceid.innerText.toUpperCase();

class addCart {
	constructor(productname, productid, price, quantity, unittotal) {
		this.productname = productname;
		this.productid = productid;
		this.price = price;
		this.quantity = quantity;
		this.unittotal = unittotal;
	}
}

class orderComplete {
	constructor(subtotal, discount, total) {
		this.subtotal = subtotal;
		this.discount = discount;
		this.total = total;
	}
}

class customerDetail {
	constructor(
		customer_id,
		customer_name,
		payment_status,
		note,
		transactionid
	) {
		this.customer_id = customer_id;
		this.customer_name = customer_name;
		this.payment_status = payment_status;
		this.transactionid = transactionid;
		this.note = note;
	}
}
// ADD FORM TO TABLE
// UI ELEMENT
class UI {
	static addBookList(product) {
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

	static clearForm() {
		let productid = document.querySelector("#productid"),
			price = document.querySelector("#productprice"),
			quantity = document.querySelector("#quantity");

		localStorage.removeItem("currentproduct");
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
				target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.textContent.trim()
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

	let countprice = document.querySelector("#countprice");

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

	countprice.innerText = `${numberToWords
		.toWords(parseFloat(totalammountel.value))
		.toUpperCase()} Taka Only.`;
};

// FETCH THE PRODUCT ID AND PRICE
let searchcontainer = document.querySelector(".dselect-wrapper .form-select");
searchcontainer.addEventListener("focusout", (e) => {
	//  GET ALL THE ELEMENTS FORM DOM
	let productid = document.querySelector("#productid");
	let productprice = document.querySelector("#productprice");
	let getproductidfromselecttag = document.querySelectorAll(
		"#selectproduct option"
	);
	let productname = e.target.innerText.trim();

	getproductidfromselecttag.forEach((e) => {
		// console.log(e.value);
		if (productname == e.innerText) {
			let getproductid = e.value;

			fetch(`${window.origin}/api/newsell/${getproductid}/price/get/`, {
				method: "POST",
			}).then((response) => {
				if (response.status !== 200) {
					console.log(
						`Something went wrong! Reload the page. Status: ${response.status}`
					);
					return;
				}

				response.json().then((data) => {
					let displaystock = document.querySelector("#displaystock");
					displaystock.innerText = data.stock;
					localStorage.setItem("currentproduct", productname);
					productid.value = data.productid;
					if (productid.value == "Out of stock") {
						productid.classList.add("text-danger");
						alert(`${data.name}, is Out of stock`);
					} else {
						productid.classList.remove("text-danger");
					}
					productprice.value = data.price;
				});
			});
		}
	});
});

form.addEventListener("submit", (e) => {
	e.preventDefault();

	// GETTING ALL THE ELEMENTS
	let productname = localStorage.getItem("currentproduct"),
		productid = document.querySelector("#productid").value,
		price = document.querySelector("#productprice").value,
		quantity = document.querySelector("#quantity").value;

	// ADD NEW PRODUCT
	let addNewProduct = new addCart(
		productname,
		productid,
		price,
		quantity,
		price * quantity
	);
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
	// Store.removeProduct(e.target);
});

// COMPLETE ORDER PROCESS
orderForm.addEventListener("submit", (e) => {
	e.preventDefault();
	let productname = document.querySelector("#productname").value,
		productid = document.querySelector("#productid").value,
		price = document.querySelector("#price").value,
		quantity = document.querySelector("#quantity").value;

	let addNewProduct = new addCart(
		productname,
		productid,
		price,
		quantity,
		price * quantity
	);

	Store.addProduct(addNewProduct);
});

// SUBMIT ALL DATA TO DATABASE
sellcompletebtn.addEventListener("click", () => {
	let pub_date_calander = document.getElementById("sell-datetime");
	localStorage.setItem("pub_date", JSON.stringify(pub_date_calander.value));

	allproduct = Store.getProducts();
	let customerEl = document.querySelector("#selectcustomer"),
		customer_id = customerEl.value,
		customer_name = customerEl.innerText;

	let payment_status = document.querySelector("#payment_status").value;
	let note = document.querySelector("#note").value;
	let trnx_id = document.querySelector("#trnx_id").value;

	let customer = new customerDetail(
		customer_id,
		customer_name,
		payment_status,
		note,
		trnx_id
	);

	let cashier = new orderComplete(
		subtotal.value,
		discount.value,
		totalammount.value
	);

	let sell = {
		products: allproduct,
		cashier: cashier,
		customer: customer,
		invoiceid: newinvoiceid.innerText,
		pub_date: localStorage.getItem("pub_date"),
	};

	localStorage.setItem("cashier", JSON.stringify(cashier));
	localStorage.setItem("sell", JSON.stringify(sell));
	localStorage.setItem("customer", JSON.stringify(customer));

	let getsell = localStorage.getItem("sell");

	sellcompletebtn.disabled = true;
	sellcompletebtn.innerHTML = "Loading...";

	fetch(`${window.origin}/dashboard/newsell/submit/`, {
		method: "POST",
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
		},
		cache: "no-cache",
		body: JSON.stringify(getsell),
	})
		.then((response) => {
			if (response.status === 400) {
				alert("No products added yet");
				return;
			}

			if (response.status !== 200) {
				alert(
					`Something went wrong! Reload the page. Status: ${response.status}`
				);
				return;
			}

			response.json().then((data) => {
				console.log(data.invoice_id);
				window.location.href = `${window.origin}/dashboard/sell/${data.invoice_id}/print/`;
			});
		})
		.catch((error) => {
			alert("An error occurred while submitting the sell:", error);
		});

	// fetch(`${window.origin}/dashboard/newsell/submit/`, {
	// 	method: "POST",
	// 	credentials: "include",
	// 	headers: {
	// 		"Content-Type": "application/json",
	// 	},
	// 	cache: "no-cache",
	// 	body: JSON.stringify(getsell),
	// }).then((response) => {
	// 	if (response.status !== 200) {
	// 		console.log(
	// 			`Something went wrong! Reload the page. Status: ${response.status}`
	// 		);
	// 		return;
	// 	}

	// 	response.json().then((data) => {
	// 		window.location.href = `${window.origin}/dashboard/todaysell/`;
	// 	});
	// });
});

document.addEventListener("DOMContentLoaded", () => {
	let date = moment().format("YYYY-MM-DDTHH:mm");
	let pub_date_calander = document.getElementById("sell-datetime");
	pub_date_calander.value = date;
	localStorage.setItem("pub_date", JSON.stringify(pub_date_calander.value));

	localStorage.removeItem("products");
	localStorage.removeItem("sell");
	localStorage.removeItem("cashier");
	localStorage.removeItem("customer");
	Store.displayBooks();
});
