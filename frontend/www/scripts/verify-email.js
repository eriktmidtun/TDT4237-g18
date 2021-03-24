window.addEventListener("DOMContentLoaded", async () => {
    const showTextContainer = document.querySelector("#showText")
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('token')) {
        const token = urlParams.get('token');
        showTextContainer.innerText = "Checking email verification token"
        let response = await sendRequest("GET", `${HOST}/api/users/verify/?token=${token}`);
        if (!response.ok) {
            let data = await response.json();
            let alert = createAlert("Could not verify email verification token!", data);
            document.body.prepend(alert);
            showTextContainer.innerText = "Email could not be validated"
        } else {
            showTextContainer.innerText = "Email successfully verified. You can now log in!"
        }
    } else if (urlParams.has('email')) {
        const emailTextContainer = document.querySelector("#email")
        showTextContainer.innerText = "Email verification link is sent to"
        emailTextContainer.innerText = urlParams.get('email');
    } else {
        window.location.replace("login.html");
    }
});