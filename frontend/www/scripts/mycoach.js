async function displayCurrentCoach() {
    let user = await getCurrentUser();
    let coach = null;

    if (user.coach) {
        response = await sendRequest("GET", user.coach);
        if (!response.ok) {
            let data = await response.json();
            let alert = createAlert("Could not retrieve coach!", data);
            document.body.prepend(alert);
        }
        let coach = await response.json();
        let input = document.querySelector("#input-coach");

        input.value = coach.username;
    } else {
        console.log("NO USER.COACH")
    }
}

async function displayOffers() {
    let user = await getCurrentUser();

    let templateOffer = document.querySelector("#template-offer");
    let listOffers = document.querySelector("#list-offers");

    let status = "p";   // pending
    let category = "received";  
    let response = await sendRequest("GET", `${HOST}/api/offers/?status=${status}&category=${category}`);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not retrieve offers!", data);
        document.body.prepend(alert);
    } else {
        let offers = await response.json();
        for (let offer of offers.results) {
            let cloneOffer = templateOffer.content.cloneNode(true);
            let li = cloneOffer.querySelector("li");
            let span = li.querySelector("span");
            span.textContent = `${offer.owner} wants to be your coach`;
            
            let buttons = li.querySelectorAll("button");
            let acceptButton = buttons[0];
            let declineButton = buttons[1];

            //acceptButton.id = `btn-accept-${offer.id}`;
            acceptButton.addEventListener("click", async (event) => await acceptOffer(event, offer.url, offer.owner));

            //declineButton.id = `btn-decline-${offer.id}`;
            declineButton.addEventListener("click", async (event) => await declineOffer(event, offer.url));

            listOffers.appendChild(li);
        }
        if (offers.results.length == 0) {
            let offersDiv = document.querySelector("#offers-div");
            let p = document.createElement("p");
            p.innerText = "You currently have no offers.";
            offersDiv.append(p);
        }
    }
}

async function acceptOffer(event, offerUrl, ownerUsername) {
    let button = event.currentTarget;
    let body = {"status": "d"};

    let response = await sendRequest("PATCH", offerUrl, body);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not accept offer!", data);
        document.body.prepend(alert);
    } else {
        let response = await sendRequest("GET", `${HOST}/api/users/${ownerUsername}/`);
        let owner = await response.json();
        let user = await getCurrentUser();

        let body = {'coach': owner.url};
        response = await sendRequest("PATCH", user.url, body);

        if (!response.ok) {
            let data = await response.json();
            let alert = createAlert("Could not update coach!", data);
            document.body.prepend(alert);
        } else {
            location.reload();
            return false;
        }
    }

}

async function declineOffer(event, offerUrl) {
    let button = event.currentTarget;
    let body = {'status': 'd'};

    let response = await sendRequest("PATCH", offerUrl, body);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not decline offer!", data);
        document.body.prepend(alert);
    } else {
        location.reload();
        return false;
    }
}

async function displayFiles() {
    let user = await getCurrentUser();

    let templateOwner = document.querySelector("#template-owner-tab");
    let templateFiles = document.querySelector("#template-files");
    let templateFile = document.querySelector("#template-file")
    let listTab = document.querySelector("#list-tab");
    let navTabContent = document.querySelector("#nav-tabContent");

    for (let fileUrl of user.coach_files) {
        let response = await sendRequest("GET", fileUrl);
        let file = await response.json();
        let divFiles = null;

        if (!document.querySelector(`#list-${file.owner}-list`)) {
            let cloneOwner = templateOwner.content.cloneNode(true);
            let a = cloneOwner.querySelector("a");
            a.id = `list-${file.owner}-list`;
            a.href = `#list-${file.owner}`;
            a.text = file.owner;
            listTab.appendChild(a);

            let cloneFiles = templateFiles.content.cloneNode(true);
            divFiles = cloneFiles.querySelector("div");
            divFiles.id = `list-${file.owner}`;
            navTabContent.appendChild(divFiles);
        } else {
            divFiles = document.querySelector(`#list-${file.owner}`);
        }

        let cloneFile = templateFile.content.cloneNode(true);
        let aFile = cloneFile.querySelector("a");
        aFile.href = file.file;
        let pathArray = file.file.split("/");
        aFile.text = pathArray[pathArray.length - 1];

        divFiles.appendChild(aFile);
    }

    if (listTab.childElementCount > 0) {
        listTab.firstElementChild.click();
    }

    if (user.coach_files.length == 0) {
        let p = document.createElement("p");
        p.innerText = "There are currently no files uploaded for this user.";
        document.querySelector("#list-files-div").append(p);
    }
}

async function getReceivedRequests() {
    let response = await sendRequest("GET", `${HOST}/api/athlete-requests/`)
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not retrieve athlete request!", data);
        document.body.prepend(alert);
    } else {
        let data = await response.json();
        let athleteRequests = data.results;
        for (let athleteRequest of athleteRequests) {
            if (athleteRequest.recipient == sessionStorage.getItem("username")) {
                let div = document.querySelector("#div-received-athlete-requests");
                let template = document.querySelector("#template-athlete-request");

                let clone = template.content.firstElementChild.cloneNode(true);
                let button = clone.querySelector("button");
                button.textContent = `${athleteRequest.owner} wants to be your coach!`

                div.appendChild(clone);
            }
        }
    }
}

function editCoach(event) {
    let buttonEditCoach = event.currentTarget;
    let buttonSetCoach = document.querySelector("#button-set-coach");
    let buttonCancelCoach = document.querySelector("#button-cancel-coach");

    setReadOnly(false, "#form-coach");

    buttonEditCoach.className += " hide";
    buttonSetCoach.className = buttonSetCoach.className.replace(" hide", "");
    buttonCancelCoach.className = buttonCancelCoach.className.replace(" hide", "");
}

function cancelCoach() {
    location.reload();
    return false;
}

async function setCoach() {
    // get current user
    let user = await getCurrentUser();
    let newCoach = document.querySelector("#input-coach").value;
    let body = {};
    if (!newCoach) {
        body['coach'] = null;
    } else {
        let response = await sendRequest("GET", `${HOST}/api/users/${newCoach}/`)
        if (!response.ok) {
            let data = await response.json();
            let alert = createAlert(`Could not retrieve user ${newCoach}`, data);
            document.body.prepend(alert);
        }
        let newCoachObject = await response.json();
        body['coach'] = newCoachObject.url;
    }

    if ('coach' in body) {
        let response = await sendRequest("PATCH", user.url, body);
        if (!response.ok) {
            let data = await response.json();
            let alert = createAlert("Could not update coach!", data);
            document.body.prepend(alert);
        } else {
            location.reload();
            return false;
        }
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    await displayCurrentCoach();
    await displayOffers();
    await displayFiles();

    let buttonSetCoach = document.querySelector("#button-set-coach");
    let buttonEditCoach = document.querySelector("#button-edit-coach");
    let buttonCancelCoach = document.querySelector("#button-cancel-coach");
    
    buttonSetCoach.addEventListener("click", async (event) => await setCoach(event));
    buttonEditCoach.addEventListener("click", editCoach);
    buttonCancelCoach.addEventListener("click", cancelCoach);
});