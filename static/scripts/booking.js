let initialized = frontInit();
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
		if (user == null) {
			location.href = "/";
		} else {
			// document.body.style.display = "block";
		}
	} else {
		location.href = "/";
	}

	let booking = document.querySelector(".navigation a");
	booking.addEventListener("click", async function () {
		if (user) {
			location.href = "/booking";
		} else {
			document.querySelector(".sign").click();
		}
	});

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
	return user;
}


initialized.then(load);
async function load(user) {
	let token = localStorage.getItem("token");
	let url = "/api/booking";
	let request = new Request(url, {
		headers: { "Authorization": `Bearer ${token}` },
	});
	let res = await fetch(request);
	let resData = await res.json();
	let data = resData.data;
	if (data == null) {
		document.querySelector(".headline span").innerText = user.name;
		document.querySelector(".headline").setAttribute("class", "headline toggle");
		document.querySelector(".hidden").style.display = "block";
		document.querySelector(".section").style.display = "none";
		document.querySelector(".contact").style.display = "none";
		document.querySelector(".payment").style.display = "none";
		document.querySelector(".confirm").style.display = "none";
		document.body.style.display = "block";
		return;
	}
	else {
		let attraction = data.attraction;
		document.querySelector(".headline span").innerText = user.name;
		document.querySelector(".info .name").innerText = `台北一日遊：${attraction.name}`;
		document.querySelector(".address span").innerText = attraction.address;
		document.querySelector(".section>img").setAttribute("src", attraction.image);
		document.querySelector(".date>span").innerText = data.date;
		if (data.time == "afternoon") {
			document.querySelector(".time>span").innerText = "下午 2 點到晚上 9 點";
		}
		document.querySelector(".cost>span").innerText = `新台幣 ${data.price} 元`;
		document.querySelector("#name").value = user.name;
		document.querySelector("#email").value = user.email;
		document.querySelector("p.total").innerText = `總價：新台幣 ${data.price} 元`;

		let cancel = document.querySelector(".delete");
		cancel.addEventListener("click", async function () {
			let token = localStorage.getItem("token");
			let url = "/api/booking";
			let request = new Request(url, {
				method: "DELETE",
				headers: { "Authorization": `Bearer ${token}` },
			});
			let res = await fetch(request);
			let resData = await res.json();
			if (resData.ok) {
				location.href = "/booking";
			}
		});

		document.body.style.display = "block";
	}



	let APP_ID = 159832;
	let APP_KEY = "app_UvdIL5m7fo6H6vJ4emZ74Z5LKL46xjeXtknFjGcV0D3PL2A0MGkq5VkAusgU";
	TPDirect.setupSDK(APP_ID, APP_KEY, 'sandbox');

	let fields = {
		number: {
			element: '#card-number',
			placeholder: '**** **** **** ****'
		},
		expirationDate: {
			element: document.getElementById('card-expiration-date'),
			placeholder: 'MM / YY'
		},
		ccv: {
			element: '#card-ccv',
			placeholder: 'CCV'
		}
	}
	let styles = {
		'input': {
			'font-family': '"Noto Sans TC", sans-serif',
			'font-weight': '500',
			'font-size': '16px',
			'color': 'gray'
		},
		'.valid': {
			'color': 'black'
		},
		'.invalid': {
			'color': 'red'
		},
	}
	let config = {
		fields: fields,
		styles: styles,
	}
	TPDirect.card.setup(config);

	let payBtn = document.querySelector(".confirm button");
	payBtn.addEventListener("click", function () {
		TPDirect.card.getPrime(async (result) => {
			if (result.status !== 0) {
				alert(`發生錯誤，請再次檢查付款資訊 (status: ${result.status})`);
				return;
			}
			document.querySelector(".mask").style.display = "block";
			document.querySelector(".loading").style.display = "block";
			let body = {
				"prime": result.card.prime,
				"order": {
					"price": data.price,
					"trip": {
						"attraction": {
							"id": data.attraction.id,
							"name": data.attraction.name,
							"address": data.attraction.address,
							"image": data.attraction.image
						},
						"date": data.date,
						"time": data.time
					},
					"contact": {
						"name": document.querySelector("#name").value,
						"email": document.querySelector("#email").value,
						"phone": document.querySelector("#phone").value
					}
				}
			};
			let url = "/api/orders";
			let request = new Request(url, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Authorization": `Bearer ${token}`,
				},
				body: JSON.stringify(body),
			});
			let res = await fetch(request);
			let resData = await res.json();
			location.href = `/thankyou?number=${resData.data.number}`;
		});
	});
}