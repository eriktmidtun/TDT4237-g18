async function loginWithTwoFactor() {
    let form = document.querySelector("#form-login-totp");
    const urlParams = new URLSearchParams(window.location.search);
    const remember_me = urlParams.get("remember_me")
    const totp_token = urlParams.get("totp_token")
    let formData = new FormData(form);
    let body = {"totp_token": totp_token, "totp_code": formData.get("totp_code")};
    // Send TOTP-token to verify token and enable 2fa
    let response = await sendRequest("POST", `${HOST}/api/users/two_factor/login/`, body)
    let data = await response.json();
    if (response.ok) {
        setCookie("access", data.access, 86400, "/");
        setCookie("refresh", data.refresh, 86400, "/");
        sessionStorage.setItem("username", formData.get("username"));
        if (remember_me === "true") {
            let response = await sendRequest("GET", `${HOST}/api/remember_me/`);
            if(response.ok) {
                let data = await response.json();
                // Remember_me lasts for 30 days
                setCookie("remember_me", data.remember_me, 2592000, "/");
            }
        }
        window.location.replace("workouts.html");

    } else {
        let alert = createAlert("Wrong code!", data);
        document.body.prepend(alert);
    }
}

document.querySelector("#btn-login-totp").addEventListener("click", async () => await loginWithTwoFactor());

window.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('totp_token')) {
        window.location.replace("login.html");
    } 
});
