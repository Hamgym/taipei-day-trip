let title = document.querySelector(".navigation h2");
title.addEventListener("click", function () {
	window.location.href = "/";
});


let list = document.querySelector(".list-item");
let leftBtn = document.querySelector("button.left");
leftBtn.addEventListener("click", function () {
	list.scrollBy({ left: -200, behavior: "smooth" });
});
let rightBtn = document.querySelector("button.right");
rightBtn.addEventListener("click", function () {
	list.scrollBy({ left: 200, behavior: "smooth" });
});


let mask = document.querySelector("div.mask");
let signLink = document.querySelector(".navigation div.sign");
let signinLink = document.querySelector(".signup-main div.signin");
let signupLink = document.querySelector(".signin-main div.signup");
let signinDialog = document.querySelector("div.signin-dialog");
let signupDialog = document.querySelector("div.signup-dialog");
signLink.addEventListener("click", function () {
	mask.style.display = "block";
	signinDialog.style.display = "block";
});
signinLink.addEventListener("click", function () {
	signinDialog.style.display = "block";
	signupDialog.style.display = "none";
});
signupLink.addEventListener("click", function () {
	signinDialog.style.display = "none";
	signupDialog.style.display = "block";
});
let closeBtns = document.querySelectorAll("div.close");
for (let closeBtn of closeBtns) {
	closeBtn.addEventListener("click", function () {
		mask.style.display = "none";
		signinDialog.style.display = "none";
		signupDialog.style.display = "none";
	});
}
window.addEventListener("keydown", function (event) {
	if (event.key == "Escape") {
		mask.style.display = "none";
		signinDialog.style.display = "none";
		signupDialog.style.display = "none";
	}
});


let nextPage = 0;
let keyword = "";
init();
async function init() {
	let res = await fetch("./api/mrts");
	let data_raw = await res.json();
	let mrts = data_raw.data;
	let list = document.querySelector("div.list-item");
	let div_proto = list.firstElementChild;
	let searchBtn = document.querySelector(".slogan button");
	if (list.children.length == 1) {
		for (let mrt of mrts) {
			let div = div_proto.cloneNode(true);
			div.style.display = "block";
			div.innerText = mrt;
			let searchField = document.querySelector(".slogan input");
			div.addEventListener("click", function () {
				searchField.value = div.innerText;
				searchBtn.click();
			});
			list.appendChild(div);
		}
	}
	nextPage = await loadOne(nextPage, keyword);
}
async function loadOne(page, keyword) {
	let res = await fetch(`./api/attractions?page=${page}&keyword=${keyword}`);
	let data_raw = await res.json();
	let nextPage = data_raw.nextPage;
	let data_page = data_raw.data;
	let proto_attraction = document.querySelector("div.attraction");
	let attractions = document.querySelector("div.attractions");
	for (let data of data_page) {
		let attraction = proto_attraction.cloneNode(true);
		attraction.style.display = "block";
		let name = attraction.querySelector("p.name");
		name.innerText = data.name;
		let category = attraction.querySelector("p.category");
		category.innerText = data.category;
		let image = attraction.querySelector("img");
		image.setAttribute("src", data.images[0]);
		let mrt = attraction.querySelector("p.mrt");
		mrt.innerText = data.mrt;
		attractions.appendChild(attraction);
	}
	return nextPage
}


const intersectionObserver = new IntersectionObserver(async (entries) => {
	if (entries[0].intersectionRatio <= 0 || nextPage == null || nextPage == 0) {
		return;
	}
	nextPage = await loadOne(nextPage, keyword);
});
intersectionObserver.observe(document.querySelector("div.footer"));


let searchBtn = document.querySelector(".slogan button");
let searchField = document.querySelector(".slogan input");
searchBtn.addEventListener("click", async function () {
	nextPage = 0;
	keyword = searchField.value;
	let attractions = document.querySelector("div.attractions");
	while (attractions.children.length > 1) {
		attractions.removeChild(attractions.lastElementChild);
	}
	await init();
});
searchField.addEventListener("keydown", function (event) {
	if (event.key == "Enter") {
		event.preventDefault();
	}
});

