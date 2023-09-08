(function() {
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


	let modalOpeners = document.getElementsByClassName("modal-open");
	for (let i = 0; i < modalOpeners.length; i++) {
		registerModalOpener(modalOpeners[i]);
	}

	let modals = document.getElementsByClassName("modal");
	for (let i = 0; i < modals.length; i++) {
		registerModal(modals[i]);
	}

	function resizeTextarea() {
		this.style.height = 0;
		this.style.height = this.scrollHeight + "px";
	}

	let textareas = document.getElementsByTagName("textarea");
	for (let i = 0; i < textareas.length; i++) {
		textareas[i].style.resize = "none";
		textareas[i].style.height = textareas[i].scrollHeight + "px";
		textareas[i].style.overflowY = "hidden";
		textareas[i].addEventListener("input", resizeTextarea);
	}
})();
