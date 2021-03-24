async function createNewUser(event) {
    let form = document.querySelector("#form-register-user");
    let formData = new FormData(form);

    let response = await sendRequest("POST", `${HOST}/api/users/`, formData, "");
    
    if (!response.ok) {
      let data = await response.json();
      let alert = createAlert("Registration failed!", data);
      document.body.prepend(alert);

    } else {
      window.location.replace("verify-email.html?email=" + formData.get("email"));
    }  
  }

document.querySelector("#btn-create-account").addEventListener("click", async (event) => await createNewUser(event));