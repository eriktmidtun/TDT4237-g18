async function send_change_password() {
    let form = document.querySelector("#form-change-password");
    let formData = new FormData(form);
    const urlParams = new URLSearchParams(window.location.search);
    let body = { "token": urlParams.get('token'), "password": formData.get("password"), "password1": formData.get("password1") };
    let response = await sendRequest("POST", `${HOST}/api/users/set-new-password/`, body)
    if (response.ok) {
        form.style.display = "none"
        let showText = document.querySelector("#showText");
        showText.innerText = "Password Successfully changed! You can now log in with your new password."
    } else {
        let data = await response.json();
        let alert = createAlert("Error", data);
        document.body.prepend(alert);
    }
};

document.querySelector("#btn-change-password").addEventListener("click", async () => await send_change_password());


window.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('token')) {
        window.location.replace("login.html");
    }
});