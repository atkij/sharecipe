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
})();
