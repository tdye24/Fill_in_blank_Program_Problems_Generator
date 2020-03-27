function init() {
	$("#checkboxRead").click(function() {
	    if ($("#checkboxRead").prop('checked'))
	        $("#signup").removeAttr('disabled')
	    else
	        $("#signup ").attr('disabled', 'disabled')
    });
	$("#signup").click(submit);
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
		$("#inputPassword").val('');
		$("#inputPasswordAgain").val('');
		return false;
	}
	return true;
}

$(document).ready(init);
