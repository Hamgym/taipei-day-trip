frontInit();
function frontInit() {
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
}


let keyword = "";
let loading = false;
let nextPage = null;
let loadedPage = [];
loadInit();
async function loadInit() {
	let list = document.querySelector("div.list-item");
	if (list.children.length == 1) {
		let res = await fetch("./api/mrts");
		let rawData = await res.json();
		let mrts = rawData.data;
		let protoDiv = list.firstElementChild;
		let searchBtn = document.querySelector(".slogan button");
		for (let mrt of mrts) {
			let div = protoDiv.cloneNode(true);
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
	let attractions = document.querySelector("div.attractions");
	while (attractions.children.length > 1) {
		attractions.removeChild(attractions.lastElementChild);
	}
	nextPage = 0;
	loadedPage.length = 0;
	await loadOne();
}
async function loadOne() {
	if (nextPage == null || loadedPage.includes(nextPage) || loading) {
		return;
	}
	loading = true;
	loadedPage.push(nextPage);
	let res = await fetch(`./api/attractions?page=${nextPage}&keyword=${keyword}`);
	let rawData = await res.json();
	let data_page = rawData.data;
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
	loading = false;
	nextPage = rawData.nextPage;
}


let footerObserver = new IntersectionObserver(async (entries) => {
	if (entries[0].intersectionRatio <= 0 || nextPage == null || loadedPage.includes(nextPage) || loading) {
		return;
	} else {
		await loadOne();
	}
});
footerObserver.observe(document.querySelector("div.footer"));


let searchBtn = document.querySelector(".slogan button");
let searchField = document.querySelector(".slogan input");
searchBtn.addEventListener("click", async function () {
	if (loading) {
		return;
	}
	keyword = searchField.value;
	await loadInit();
});
searchField.addEventListener("keydown", function (event) {
	if (event.key == "Enter") {
		event.preventDefault();
	}
});

