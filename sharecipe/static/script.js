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
})();
