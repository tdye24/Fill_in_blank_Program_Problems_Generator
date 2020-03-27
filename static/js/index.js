$(document).ready(init);

function init() {
    checkLogin();
    setupUI();
}

function checkLogin() {
    $.post("user", {
        "action" : "checklogin"
    }, function(data) {
        let isLogin = data.isLogin;
        if (isLogin) {
            $("#login-form-wrap").html($("#template-gotodashboard").html());
        }
    });
}

function setupUI() {
    $("#signIn").click(login);

    $("#inputUsername").focusin(usernameFocusIn);
    $("#inputPassword").focusin(passwordFocusIn);

    if ($.cookie("username")) {
        $("#inputUsername").val($.cookie("username"));
		$("#inputRememberMe").prop("checked", true);
    }
    $("#forgetPasswordModal").find("#okButton").click(doForgetPassword);
}

function usernameFocusIn() {
    $("#username").removeClass("warning");
    $("#username").removeClass("error");
    $("#helpUsername").addClass("hide");
    $("#helpUsername").text("");
}

function passwordFocusIn() {
    $("#password").removeClass("warning");
    $("#password").removeClass("error");
    $("#helpPassword").addClass("hide");
    $("#helpPassword").text("");
}

function login() {
    let username = $("#inputUsername").val();
    let password = $("#inputPassword").val();
    let rememberMe = $("#inputRememberMe").is(':checked');
    if (username === "") {
        $("#username").addClass("warning");
        $("#helpUsername").removeClass("hide");
        $("#helpUsername").text("Please enter your username.");
        return false;
    }
    if (password === "") {
        $("#password").addClass("warning");
        $("#helpPassword").removeClass("hide");
        $("#helpPassword").text("Please enter your password.");
        return false;
    }
    $.post("user", {
        "action" : "login",
        "username" : username,
        "password" : password
    },
    function(data) {
        let json_data = eval(data);
        if (json_data["error"] === 0) {
            if (rememberMe) {
                $.cookie("username", username, { expires: 30 });
            } else {
                $.cookie("username", null);
            }
        } else if (json_data["error"] == 1) {
            $("#username").addClass("error");
            $("#helpUsername").removeClass("hide");
            $("#helpUsername").text(json_data["errorMessage"]);
        } else if (json_data["error"] == 2) {
            $("#password").addClass("error");
            $("#helpPassword").removeClass("hide");
            $("#helpPassword").text(json_data["errorMessage"]);
        } else {
            alert(json_data["errorMessage"]);
        }
    });
    return false;
}

function doForgetPassword()
{
        $.post("user.php", {
            action  : "resetpassword",
            email   : $("#forgetPasswordModal").find("#email").val()
        },
        function(jdata)
        {
            var data = eval(jdata);
            if (data["error"] != 0) {
                alert(data["errorMessage"]);
                return;
            }
            alert("A mail has been sent to your E-Mail address. Please read this mail to reset your password.");
        });
}