async function verifyToken() {
    let form = document.querySelector("#form-2fa");
    let formData = new FormData(form);
    let body = {"totp_code": formData.get("totp_code")};

    // Send TOTP-token to verify token and enable 2fa
    let response = await sendRequest("POST", `${HOST}/api/users/two_factor/enable/`, body)
    let data = await response.json();
    if (response.ok) {
        let alert = createAlert("Enabled two factor authentication!", data);
        document.body.prepend(alert);
    } else {
        let alert = createAlert("Something went wrong!", data);
        document.body.prepend(alert);
    }
};

document.querySelector("#btn-verify-token").addEventListener("click", async () => await verifyToken());