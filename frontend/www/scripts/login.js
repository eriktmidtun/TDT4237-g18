async function login() {
    let form = document.querySelector("#form-login");
    let formData = new FormData(form);
    let body = {"username": formData.get("username"), "password": formData.get("password")};
    // Sets cookie if remember me checked
    let remember_me = document.getElementById("rememberMe").checked;

    // Don't send access token right away;
    // ... Check backend if user has activated 2fa or not.
    // If user has activated 2fa, don't send access tokens
    // Else, send access tokens.
    let response = await sendRequest("POST", `${HOST}/api/token/`, body)
    let data = await response.json();
    if (response.ok) {
        // If 2fa is not verified, set tokens
        if (data.totp_token){
            // If 2fa is verified, let user write in TOTP-token
            window.location.replace("twofactorlogin.html?remember_me="+ remember_me +"&totp_token="+ data.totp_token);
            return;
        } else {
            // access and refresh cookies each have a max age of 24 hours
            setCookie("access", data.access, 86400, "/");
            setCookie("refresh", data.refresh, 86400, "/");
            sessionStorage.setItem("username", formData.get("username"));
            if (remember_me) {
                let response = await sendRequest("GET", `${HOST}/api/remember_me/`);
                if(response.ok) {
                    let data = await response.json();
                    // Remember_me lasts for 30 days
                    setCookie("remember_me", data.remember_me, 2592000, "/");
                }
            }
            window.location.replace("workouts.html");
        }
    } else {
        let alert = createAlert("Login failed!", data);
        document.body.prepend(alert);
    }
};


// Used for login if remember me cookie exists
async function rememberMe() {
    let response = await sendRequest("POST", `${HOST}/api/remember_me/`);
    if (response.ok) {
        let data = await response.json();
        // access and refresh cookies each have a max age of 24 hours
        setCookie("access", data.access, 86400, "/");
        setCookie("refresh", data.refresh, 86400, "/");

        window.location.replace("workouts.html");
    } else {
        let data = await response.json();
        let alert = createAlert("Login failed!", data);
        document.body.prepend(alert);
    }
};

window.onload = function() {
    if (getCookieValue('remember_me')){
        rememberMe();
    }
};

document.querySelector("#btn-login").addEventListener("click", async () => await login());