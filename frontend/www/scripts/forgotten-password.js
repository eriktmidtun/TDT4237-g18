async function send_reset_password_email() {
    let form = document.querySelector("#form-reset-password");
    let formData = new FormData(form);
    let body = {"email": formData.get("email")};

    let response = await sendRequest("POST", `${HOST}/api/users/password-reset/`, body)
    if (response.ok) {
        form.style.display = "none"
        let showText = document.querySelector("#showText");
        let titleText = document.querySelector("#title");
        showText.innerText = "If there's an active account linked to this email, we'll send over instructions to reset your password. "
        titleText.innerText = formData.get("email")
        titleText.classList.add("text-primary")
    } else {
        let data = await response.json();
        let alert = createAlert("Email not valid", data);
        document.body.prepend(alert);
    }
};

document.querySelector("#btn-reset-password").addEventListener("click", async () => await send_reset_password_email());