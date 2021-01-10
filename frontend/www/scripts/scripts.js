function makeNavLinkActive(id) {
  let link = document.getElementById(id);
  link.classList.add("active");
  link.setAttribute("aria-current", "page");
}

function isUserAuthenticated() {
  return (getCookieValue("access") != null) || (getCookieValue("refresh") != null);
}

function updateNavBar() {
  let nav = document.querySelector("nav");

  // Emphasize link to current page
  if (window.location.pathname == "/" || window.location.pathname == "/index.html") {
    makeNavLinkActive("nav-index");
  } else if (window.location.pathname == "/workouts.html") {
    makeNavLinkActive("nav-workouts");
  } else if (window.location.pathname == "/exercises.html") {
    makeNavLinkActive("nav-exercises");
  } else if (window.location.pathname == "/mycoach.html") {
    makeNavLinkActive("nav-mycoach")
  } else if (window.location.pathname == "/myathletes.html") {
    makeNavLinkActive("nav-myathletes");
  }

  if (isUserAuthenticated()) {
    document.getElementById("btn-logout").classList.remove("hide");

    document.querySelector('a[href="logout.html"').classList.remove("hide");
    document.querySelector('a[href="workouts.html"').classList.remove("hide");
    document.querySelector('a[href="mycoach.html"').classList.remove("hide");
    document.querySelector('a[href="exercises.html"').classList.remove("hide");
    document.querySelector('a[href="myathletes.html"').classList.remove("hide");
  } else {
    document.getElementById("btn-login-nav").classList.remove("hide");
    document.getElementById("btn-register").classList.remove("hide");
  }

}


function setCookie(name, value, maxage, path="") {
  document.cookie = `${name}=${value}; max-age=${maxage}; path=${path}`;
}

function deleteCookie(name) {
  setCookie(name, "", 0, "/");
}

function getCookieValue(name) {
  let cookieValue = null;
  let cookieByName = document.cookie.split("; ").find(row => row.startsWith(name));

  if (cookieByName) {
    cookieValue = cookieByName.split("=")[1];
  }

  return cookieValue;
}

async function sendRequest(method, url, body, contentType="application/json; charset=UTF-8") {
  if (body && contentType.includes("json")) {
    body = JSON.stringify(body);
  }

  let myHeaders = new Headers();

  if (contentType) myHeaders.set("Content-Type", contentType);
  if (getCookieValue("access")) myHeaders.set("Authorization", "Bearer " + getCookieValue("access"));
  let myInit = {headers: myHeaders, method: method, body: body};
  let myRequest = new Request(url, myInit);

  let response = await fetch(myRequest);
  if (response.status == 401 && getCookieValue("refresh")) {
    // access token not accepted. getting refresh token
    myHeaders = new Headers({"Content-Type": "application/json; charset=UTF-8"});
    let tokenBody = JSON.stringify({"refresh": getCookieValue("refresh")});
    myInit = {headers: myHeaders, method: "POST", body: tokenBody};
    myRequest = new Request(`${HOST}/api/token/refresh/`, myInit);
    response = await fetch(myRequest);

    if (response.ok) {
      // refresh successful, received new access token
      let data = await response.json();
      setCookie("access", data.access, 86400, "/");

        let myHeaders = new Headers({"Authorization": "Bearer " + getCookieValue("access"),
                               "Content-Type": contentType});
        let myInit = {headers: myHeaders, method: method, body: body};
        let myRequest = new Request(url, myInit);
        response = await fetch(myRequest);

        if (!response.ok) window.location.replace("logout.html");
    }
  }

  return response;
}

function setReadOnly(readOnly, selector) {
  let form = document.querySelector(selector);
  let formData = new FormData(form);

  for (let key of formData.keys()) {
      let selector = `input[name="${key}"], textarea[name="${key}"]`;
      for (let input of form.querySelectorAll(selector)) {

      if (!readOnly && input.hasAttribute("readonly"))
      {
        input.readOnly = false;
      }
      else if (readOnly && !input.hasAttribute("readonly")) {
        input.readOnly = true;
      }
    }

    selector = `input[type="file"], select[name="${key}`;
    for (let input of form.querySelectorAll(selector)) {
      if ((!readOnly && input.hasAttribute("disabled")))
      {
        input.disabled = false;
      }
      else if (readOnly && !input.hasAttribute("disabled")) {
        input.disabled = true;
      } 
    }
  }

  for (let input of document.querySelectorAll("input:disabled, select:disabled")) {
    if ((!readOnly && input.hasAttribute("disabled")) ||
        (readOnly && !input.hasAttribute("disabled"))) {
        input.disabled = !input.disabled;
    } 
  }
}

async function getCurrentUser() {
  let user = null;
  let response = await sendRequest("GET", `${HOST}/api/users/?user=current`)
  if (!response.ok) {
      console.log("COULD NOT RETRIEVE CURRENTLY LOGGED IN USER");
  } else {
      let data = await response.json();
      user = data.results[0];
  }

  return user;
}

function createAlert(header, data) {
  let alertDiv = document.createElement("div");
  alertDiv.className = "alert alert-warning alert-dismissible fade show"
  alertDiv.setAttribute("role", "alert");
  
  let strong = document.createElement("strong");
  strong.innerText = header;
  alertDiv.appendChild(strong);

  let button = document.createElement("button");
  button.type = "button";
  button.className = "btn-close";
  button.setAttribute("data-bs-dismiss", "alert");
  button.setAttribute("aria-label", "Close");
  alertDiv.appendChild(button);

  let ul = document.createElement("ul");
  if ("detail" in data) {
    let li = document.createElement("li");
    li.innerText = data["detail"];
    ul.appendChild(li);
  } else {
    for (let key in data) {
      let li = document.createElement("li");
      li.innerText = key;

      let innerUl = document.createElement("ul");
      for (let message of data[key]) {
        let innerLi = document.createElement("li");
        innerLi.innerText = message;
        innerUl.appendChild(innerLi);
      }
      li.appendChild(innerUl);
      ul.appendChild(li);
    }
  }
  alertDiv.appendChild(ul);

  return alertDiv;

}

window.addEventListener("DOMContentLoaded", updateNavBar);

