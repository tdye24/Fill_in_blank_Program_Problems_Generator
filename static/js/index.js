$(document).ready(init);

function init() {
    loadStatistics();
    checkLogin();
    setupUI();
}

function checkLogin()
{
    $.post("user.php", {
        "action" : "checklogin"
    },
    function(data)
    {
        var islogin = data.islogin;
        if (islogin) {
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

function loadStatistics() {
    $.get("problem", {
        action:'getProblemList',
        volume: 1
    },
    function (res) {
        // console.log(res)
        // let data = res['data'];
        // let html = ``;
        // for (let i = 0; i < data.length; i++) {
        //     html += `<tr>
        //                 <th id="problem-number" scope="row" colspan="2" title="${data[i].id}">${data[i].id}</th>
        //                 <td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" id="problem-title" colspan="5" title="${data[i].title}">${data[i].title}</td>
        //                 <td style="overflow: hidden ; text-overflow: ellipsis; white-space: nowrap;" id="average-score" colspan="2" title="${data[i].averageScore}">${data[i].averageScore}</td>
        //                 <td style="overflow: hidden ; text-overflow: ellipsis; white-space: nowrap;" id="average-score" colspan="2" title="${data[i].score}">${data[i].score}</td>
        //              </tr>`
        // }
        // $('#problem-archive-content tbody').html(html)

        // let volume = res['volume'];
        // let volumes = res['volumes'];
        // let paginationHtml = pagination(volume, volumes);
        // $('#pagination').append(paginationHtml);
    });
    $("a[href='#problem-archive-content']").click(function() {
        alert("Request Problem Data!");
    });
    $("a[href='#realtime-judge-status']").click(function () {
        alert("Request Judge Status");
    });
    $("a[href='#authors-ranklist']").click(function () {
        alert("Request Ranklist");
    });
}

function pagination(volume, volumes) {
    let html = ``;
    for(let i=1; i<=volumes; i++) {
        if(i == volume) {
            html += `<a href="getProblemList?volume=${i}">
                        <span style="font-size: large; color: red">
                            ${i}
                        </span>
                      </a>`;
        } else {
            html += `<a href="problem?action=getProblemList&volume=${i}">
                        <span style="font-size: large">
                            ${i}
                        </span>
                      </a>`;
        }

    }
    return html;
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
        } else if (json_data["error"] == 2) {
            $("#password").addClass("error");
            $("#helpPassword").removeClass("hide");
            $("#helpPassword").text(json_data["errorMessage"]);
        } else if (json_data["error"] == 3) {
            $("#username").addClass("error");
            $("#helpUsername").removeClass("hide");
            $("#helpUsername").text(json_data["errorMessage"]);
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