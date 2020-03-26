function init() {
	$("#checkboxRead").click(function() {
	    if ($("#checkboxRead").prop('checked'))
	        $("#btnRegister").attr('disabled', false);
	    else
	        $("#btnRegister").attr('disabled', true);
    });
	$("#btnRegister").click(submit);
}

function submit() {
	let email = $("#inputEmail").val().trim();
	let pass1 = $("#inputPassword").val();
	let pass2 = $("#inputPasswordAgain").val();
	let nickname = $("#inputNickname").val().trim();
	if (email === "") {
		alert("Please enter your E-Mail.");
		return false;
	}
	if (pass1 === "") {
		alert("Please enter your password.");
		return false;
	}
	if (pass2 === "") {
		alert("Please enter your password again.");
		return false;
	}
	if (nickname === "") {
		alert("Please enter your nickname.");
		return false;
	}
	if (pass1 !== pass2) {
		alert("The two passes of passwords are different.");
		return false;
	}
	$.post("register", {
		"email" : email,
		"password": pass1,
		"nickname": nickname,
	},
	function(data) {
		if(data['error'] === 0) {
			alert("A mail has been sent to your E-Mail address. Please read this mail to finish the registration.");
			top.location="index";
		} else {
			alert(data['errorMessage'])
		}
	});
	return false;
}

$(document).ready(init);
