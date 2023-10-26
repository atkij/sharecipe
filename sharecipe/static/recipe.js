(function() {
	function new_input(list, textarea, sep="\n", value="") {
		let item = document.createElement("li");
		let input = document.createElement("textarea");

		input.value = value;
		input.rows = 1;

		item.appendChild(input);
		list.appendChild(item);

		registerTextarea(input);

		input.addEventListener("keydown", function(e) {
			let key = e.code || e.key;
			if (key == "Enter" && input.value.endsWith(sep.slice(0, -1))) {
				e.preventDefault();
				
				input.value = input.value.slice(0, input.value.length - sep.length + 1);
				
				let newItem = new_input(list, method, sep);
				list.insertBefore(newItem, item.nextSibling);
				item.nextSibling.firstChild.focus();
				
				input.style.height = 0;
				input.style.height = input.scrollHeight + "px";
			} else if ((key == "Backspace" || key == "Delete") && input.value == "") {
				e.preventDefault();
				if (item.previousSibling != null && key == "Backspace") {
					item.previousSibling.firstChild.focus();
				} else {
					item.nextSibling.firstChild.setSelectionRange(0, 0);
					item.nextSibling.firstChild.focus();
				}

				item.remove();
			}
			
		});

		input.addEventListener("input", function() {	
			if (item.nextSibling == null) {
				new_input(list, method, sep);
			}

			textarea.value = "";
			for (let item of list.childNodes) {
				if (item.firstChild.value.trim() != "") {
					textarea.value += item.firstChild.value + sep;
				}
			}
			textarea.value = textarea.value.slice(0, -1);
		});

		return item;
	}

	// automatically add input fields for each ingredient
	let ingredients = document.getElementById("ingredients");
	ingredients.style.display = "none";

	let ulList = document.createElement("ul");
	ingredients.parentNode.appendChild(ulList);
	
	if (ingredients.value.trim() != "") {
		for (let val of ingredients.value.trim().split("\n")) {
			new_input(ulList, ingredients, "\n", val);
		}
	}

	new_input(ulList, ingredients, "\n");

	// automatically add textarea fields for each instruction
	let method = document.getElementById("method");
	method.style.display = "none";

	let olList = document.createElement("ol");
	method.parentNode.appendChild(olList);

	if (method.value.trim() != "") {
		for (let val of method.value.trim().split("\n\n")) {
			new_input(olList, method, "\n\n", val);
		}
	}

	new_input(olList, method, "\n\n");
})();
