frontInit();
async function frontInit() {
	let user = null;
	let token = localStorage.getItem("token");
	if (token) {
		let url = "/api/user/auth";
		let request = new Request(url, {
			headers: { "Authorization": `Bearer ${token}` },
		});
		let res = await fetch(request);
		let resData = await res.json();
		user = resData.data;
	}

	let mask = document.querySelector("div.mask");
	let title = document.querySelector(".navigation h2");
	let signLink = document.querySelector(".navigation div.sign");
	let closeBtns = document.querySelectorAll("div.close");
	let signinLink = document.querySelector(".signup-main div.signin");
	let signupLink = document.querySelector(".signin-main div.signup");
	let signinDialog = document.querySelector("div.signin-dialog");
	let signupDialog = document.querySelector("div.signup-dialog");
	if (user) {
		signLink.innerText = "登出系統";
		signLink.addEventListener("click", function () {
			localStorage.clear();
			location.href = "/";
		});
	} else {
		signLink.innerText = "登入/註冊";
		signLink.addEventListener("click", function () {
			mask.style.display = "block";
			signinDialog.style.display = "block";
		});
	}
	for (let closeBtn of closeBtns) {
		closeBtn.addEventListener("click", function () {
			mask.style.display = "none";
			signinDialog.style.display = "none";
			signupDialog.style.display = "none";
		});
	}
	signinLink.addEventListener("click", function () {
		signinDialog.style.display = "block";
		signupDialog.style.display = "none";
	});
	signupLink.addEventListener("click", function () {
		signinDialog.style.display = "none";
		signupDialog.style.display = "block";
	});
	window.addEventListener("keydown", function (event) {
		if (event.key == "Escape") {
			mask.style.display = "none";
			signinDialog.style.display = "none";
			signupDialog.style.display = "none";
		}
	});
	title.addEventListener("click", function () {
		window.location.href = "/";
	});

	let signupForm = document.querySelector(".signup-main form");
	let signinForm = document.querySelector(".signin-main form");
	signupForm.addEventListener("submit", async function (event) {
		event.preventDefault();
		let submitter = signupForm.querySelector("[type='submit']");
		let formData = new FormData(this, submitter);
		let body = {};
		for (const [key, value] of formData) {
			body[key] = value;
		}
		let url = "/api/user";
		let request = new Request(url, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body),
		});
		let res = await fetch(request);
		let resData = await res.json();
		if (resData.error) {
			let p = signupForm.querySelector("p.message");
			p.setAttribute("style", "display: block");
			p.innerText = resData.message;
		}
		if (resData.ok) {
			let p = signupForm.querySelector("p.message");
			p.setAttribute("style", "display: block");
			p.innerText = "恭喜您，註冊成功！";
		}
	});
	signinForm.addEventListener("submit", async function (event) {
		event.preventDefault();
		let submitter = signinForm.querySelector("[type='submit']");
		let formData = new FormData(this, submitter);
		let body = {};
		for (const [key, value] of formData) {
			body[key] = value;
		}
		let url = "/api/user/auth";
		let request = new Request(url, {
			method: "PUT",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body),
		});
		let res = await fetch(request);
		let resData = await res.json();
		if (resData.error) {
			let p = signinForm.querySelector("p.message");
			p.innerText = resData.message;
			p.setAttribute("style", "display:block");
		} else {
			localStorage.setItem("token", resData.token);
			location.href = "/";
		}
	});



	let list = document.querySelector(".list");
	let leftBtn = document.querySelector("button.left");
	let rightBtn = document.querySelector("button.right");
	leftBtn.addEventListener("click", function () {
		list.scrollBy({ left: -300, behavior: "smooth" });
	});
	rightBtn.addEventListener("click", function () {
		list.scrollBy({ left: 300, behavior: "smooth" });
	});
}


let keyword = "";
let loading = false;
let nextPage = null;
let loadedPage = [];
loadInit();
async function loadInit() {
	let list = document.querySelector("div.list");
	if (list.children.length == 1) {
		let res = await fetch("/api/mrts");
		let rawData = await res.json();
		let mrts = rawData.data;
		let protoItem = list.firstElementChild;
		let searchBtn = document.querySelector(".slogan button");
		for (let mrt of mrts) {
			let item = protoItem.cloneNode(true);
			item.style.display = "block";
			item.innerText = mrt;
			let searchField = document.querySelector(".slogan input");
			item.addEventListener("click", function () {
				searchField.value = item.innerText;
				searchBtn.click();
			});
			list.appendChild(item);
		}
	}
	let attractions = document.querySelector("div.attractions");
	while (attractions.children.length > 1) {
		attractions.removeChild(attractions.lastElementChild);
	}
	nextPage = 0;
	loadedPage.length = 0;
	loadOne();
}
async function loadOne() {
	if (nextPage == null || loadedPage.includes(nextPage) || loading) {
		return;
	}
	loading = true;
	loadedPage.push(nextPage);
	let res = await fetch(`./api/attractions?page=${nextPage}&keyword=${keyword}`);
	let rawData = await res.json();
	let pageData = rawData.data;
	let protoAttraction = document.querySelector("div.attraction");
	let attractions = document.querySelector("div.attractions");
	for (let data of pageData) {
		let attraction = protoAttraction.cloneNode(true);
		attraction.style.display = "block";
		let container = attraction.querySelector(".container");
		container.addEventListener("click", () => {
			window.location.href = `/attraction/${data.id}`;
		});
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
	nextPage = rawData.nextPage;
	loading = false;
}


let footerObserver = new IntersectionObserver(async (entries) => {
	if (entries[0].intersectionRatio <= 0 || nextPage == null || loadedPage.includes(nextPage) || loading) {
		return;
	}
	loadOne();
});
footerObserver.observe(document.querySelector("div.footer"));


let searchBtn = document.querySelector(".slogan button");
let searchField = document.querySelector(".slogan input");
searchBtn.addEventListener("click", function () {
	if (loading) {
		return;
	}
	keyword = searchField.value;
	loadInit();
});
searchField.addEventListener("keydown", function (event) {
	if (event.key == "Enter") {
		event.preventDefault();
		searchBtn.click();
	}
});

