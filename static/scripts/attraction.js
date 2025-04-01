frontInit();
async function frontInit() {
	let title = document.querySelector(".navigation h2");
	title.addEventListener("click", function () {
		window.location.href = "/";
	});

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

	let signLink = document.querySelector(".navigation div.sign");
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
	let mask = document.querySelector("div.mask");
	let signinLink = document.querySelector(".signup-main div.signin");
	let signupLink = document.querySelector(".signin-main div.signup");
	let signinDialog = document.querySelector("div.signin-dialog");
	let signupDialog = document.querySelector("div.signup-dialog");
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

	let signupForm = document.querySelector(".signup-main form");
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

	let signinForm = document.querySelector(".signin-main form");
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
			let message = signinForm.querySelector("p.message");
			message.innerText = resData.message;
			message.setAttribute("style", "display: block");
		} else {
			localStorage.setItem("token", resData.token);
			location.href = "/";
		}
	});
}

load();
async function load() {
	let id = location.pathname.slice(12);
	let res = await fetch(`/api/attraction/${id}`);
	let rawData = await res.json();
	let data = rawData.data;
	let images = data.images;
	let slideShow = document.querySelector(".picture");
	let protoImg = slideShow.querySelector("img");
	let circles = slideShow.querySelector(".circles");
	let protoCir = slideShow.querySelector(".circle");
	let count = 0;
	for (let url of images) {
		let img = protoImg.cloneNode(true);
		img.setAttribute("src", url);
		slideShow.appendChild(img);
		let cir = protoCir.cloneNode(true);
		cir.setAttribute("id", count);
		cir.addEventListener("click", (event) => {
			let id = Number(event.target.id);
			for (let i = 0; i < circles.children.length; i++) {
				circles.children[i].setAttribute("class", "circle");
				slideShow.children[i + 3].setAttribute("style", "display: none");
			}
			circles.children[id].setAttribute("class", "circle black");
			slideShow.children[id + 3].setAttribute("style", "display: block");;
		});
		circles.appendChild(cir);
		count++;
	}
	protoImg.remove();
	protoCir.remove();
	let imgs = slideShow.querySelectorAll("img");
	imgs[0].setAttribute("style", "display: block");
	let cirs = slideShow.querySelectorAll(".circle");
	cirs[0].setAttribute("class", "circle black");
	let right = slideShow.querySelector(".right-arrow");
	right.addEventListener("click", () => {
		let now = slideShow.querySelector(`img[style="display: block"]`);
		now.setAttribute("style", "display: none");
		let next = now.nextElementSibling;
		if (next == null) {
			next = imgs[0];
		}
		next.setAttribute("style", "display: block");
		let cirNow = circles.querySelector(`div[class="circle black"]`);
		cirNow.setAttribute("class", "circle");
		let cirNext = cirNow.nextElementSibling;
		if (cirNext == null) {
			cirNext = cirs[0];
		}
		cirNext.setAttribute("class", "circle black");
	});
	let left = slideShow.querySelector(".left-arrow");
	left.addEventListener("click", () => {
		let now = slideShow.querySelector(`img[style="display: block"]`);
		now.setAttribute("style", "display: none");
		let prev = now.previousElementSibling;
		if (prev.tagName == "DIV") {
			prev = imgs[imgs.length - 1];
		}
		prev.setAttribute("style", "display: block");
		let cirNow = circles.querySelector(`div[class="circle black"]`);
		cirNow.setAttribute("class", "circle");
		let cirPrev = cirNow.previousElementSibling;
		if (cirPrev == null) {
			cirPrev = cirs[cirs.length - 1];
		}
		cirPrev.setAttribute("class", "circle black");
	});

	let name = document.querySelector(".profile>h3");
	name.innerText = data.name;
	let subtitle = document.querySelector(".profile>p");
	subtitle.innerText = `${data.category} at ${data.mrt}`;
	let description = document.querySelector(".info p:nth-child(1)");
	description.innerText = data.description;
	let address = document.querySelector(".info p:nth-child(3)");
	address.innerText = data.address;
	let transport = document.querySelector(".info p:nth-child(5)");
	transport.innerText = data.transport;

	let price = document.querySelector(".price p:last-child");
	let radioFirst = document.querySelector("#morning");
	radioFirst.addEventListener("click", () => {
		price.innerText = "新台幣 2000 元";
	});
	let radioSecond = document.querySelector("#afternoon");
	radioSecond.addEventListener("click", () => {
		price.innerText = "新台幣 2500 元";
	});

	let form = document.querySelector(`[class="booking"]`);
	form.addEventListener("submit", (event) => {
		event.preventDefault();
	});
}