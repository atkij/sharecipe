function registerModal(modal) {
	let closers = modal.getElementsByClassName("modal-close");
	for (let i = 0; i < closers.length; i++) {
		closers[i].addEventListener("click", function(e) {
			e.preventDefault();
			modal.classList.add("hidden");
		});
	}
}

function registerModalOpener(button) {
	button.addEventListener("click", function(e) {
		e.preventDefault();
		let modalId = button.getAttribute("data-modal");
		if (modalId !== null) {
			let modal = document.getElementById(modalId);
			modal.classList.remove("hidden");
		}
	});
}

function registerTabView(tabView) {
	let tabs = tabView.getElementsByClassName("tab-button");
	for (let i = 0; i < tabs.length; i++) {
		tabs[i].addEventListener("click", function(e) {
			e.preventDefault();
			for (let j = 0; j < tabs.length; j++) {
				tabs[j].classList.remove("active");
			}
			tabs[i].classList.add("active");
		});
	}
}

function registerTextarea(textarea) {
	textarea.style.resize = "none";
	textarea.style.height = textarea.scrollHeight + "px";
	textarea.style.overflowY = "hidden";
	textarea.addEventListener("input", function() {
		textarea.style.height = 0;
		textarea.style.height = textarea.scrollHeight + "px";
	});
}

function registerShareBtn(btn) {
	const data = {
		title: btn.getAttribute("data-tite"),
		text: btn.getAttribute("data-text"),
		url: btn.getAttribute("data-url"),
	}

	btn.addEventListener("click", function() {
		if (navigator.share) {
			navigator.share(data);
		} else {
			console.log("Unable to share resource.");
		}
	});
}

function Slideshow(slideshow) {
	this.slideshow = slideshow;
	this.slides = this.slideshow.getElementsByClassName("slide");
	this.next = this.slideshow.getElementsByClassName("next")[0];
	this.prev = this.slideshow.getElementsByClassName("previous")[0];
	this.slideIndex = 0;

	this.showSlide = () => {
		for (let i = 0; i < this.slides.length; i++) {
			this.slides[i].style.display = "none";
		}

		this.slides[this.slideIndex].style.display = "block";
		this.loadImage(this.slideIndex + 1);
	}

	this.loadImage = (num) => {
		if (num < 0 || num >= this.slides.length) {
			return;
		}

		let image = this.slides[num].getElementsByTagName("img")[0];
		image.setAttribute("src", image.getAttribute("data-src"))
	}

	this.next.addEventListener("click", (e) => {
		e.preventDefault();
		this.slideIndex += 1;
		if (this.slideIndex >= this.slides.length) {
			this.slideIndex -= 1;
		} else {
			this.showSlide();
		}
	});

	this.prev.addEventListener("click", (e) => {
		e.preventDefault();
		this.slideIndex -= 1;
		if (this.slideIndex < 0) {
			this.slideIndex += 1;
		} else {
			this.showSlide();
		}
	});

	this.loadImage(0);
	this.showSlide();
}

function registerSlideshow(slideshow) {
	new Slideshow(slideshow);
}

(function() {
	let modalOpeners = document.getElementsByClassName("modal-open");
	for (let i = 0; i < modalOpeners.length; i++) {
		registerModalOpener(modalOpeners[i]);
	}

	let modals = document.getElementsByClassName("modal");
	for (let i = 0; i < modals.length; i++) {
		registerModal(modals[i]);
	}

	let tabViews = document.getElementsByClassName("tab-view");
	for (let i = 0; i < tabViews.length; i++) {
		registerTabView(tabViews[i]);
	}

	let textareas = document.getElementsByTagName("textarea");
	for (let i = 0; i < textareas.length; i++) {
		registerTextarea(textareas[i]);
	}

	let slideshows = document.getElementsByClassName("slideshow");
	for (let i = 0; i < slideshows.length; i++) {
		registerSlideshow(slideshows[i]);
	}

	let shareBtns = document.getElementsByClassName("share");
	for (let i = 0; i < shareBtns.length; i++) {
		registerShareBtn(shareBtns[i]);
	}
})();
