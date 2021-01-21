async function displayCurrentRoster() {
    let templateFilledAthlete = document.querySelector("#template-filled-athlete");
    let templateEmptyAthlete = document.querySelector("#template-empty-athlete");
    let controls = document.querySelector("#controls");

    let currentUser = await getCurrentUser();
    for (let athleteUrl of currentUser.athletes) {
        let response = await sendRequest("GET", athleteUrl);
        let athlete = await response.json();

        createFilledRow(templateFilledAthlete, athlete.username, controls, false);
    }
    
    let status = "p";   // pending
    let category = "sent";  
    let response = await sendRequest("GET", `${HOST}/api/offers/?status=${status}&category=${category}`);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not retrieve offers!", data);
        document.body.prepend(alert);
    } else {
        let offers = await response.json();

        for (let offer of offers.results) {
            let response = await sendRequest("GET", offer.recipient);
            let recipient = await response.json();
            createFilledRow(templateFilledAthlete, `${recipient.username} (pending)`, controls, true);
        }
    }

    let emptyClone = templateEmptyAthlete.content.cloneNode(true);
    let emptyDiv = emptyClone.querySelector("div");
    let emptyButton = emptyDiv.querySelector("button");
    emptyButton.addEventListener("click", addAthleteRow);
    controls.appendChild(emptyDiv);
}

function createFilledRow(templateFilledAthlete, inputValue, controls, disabled) {
    let filledClone = templateFilledAthlete.content.cloneNode(true);
    let filledDiv = filledClone.querySelector("div");
    let filledInput = filledDiv.querySelector("input");
    let filledButton = filledDiv.querySelector("button");
    filledInput.value = inputValue;
    filledInput.disabled = disabled;
    if (!disabled) {
        filledButton.addEventListener("click", removeAthleteRow);
    }
    else {
        filledButton.disabled = true;
    }
    controls.appendChild(filledDiv);
}

async function displayFiles() {
    let user = await getCurrentUser();

    let templateAthlete = document.querySelector("#template-athlete-tab");
    let templateFiles = document.querySelector("#template-files");
    let templateFile = document.querySelector("#template-file");
    let listTab = document.querySelector("#list-tab");
    let navTabContent = document.querySelector("#nav-tabContent");

    for (let fileUrl of user.athlete_files) {
        let response = await sendRequest("GET", fileUrl);
        let file = await response.json();

        response = await sendRequest("GET", file.athlete);
        let athlete = await response.json();

        let tabPanel = document.querySelector(`#tab-contents-${athlete.username}`)
        if (!tabPanel) {
            tabPanel = createTabContents(templateAthlete, athlete, listTab, templateFiles, navTabContent);
        } 

        let divFiles = tabPanel.querySelector(".uploaded-files");
        let aFile = createFileLink(templateFile, file.file);

        divFiles.appendChild(aFile);
    }

    for (let athleteUrl of user.athletes) {
        let response = await sendRequest("GET", athleteUrl);
        let athlete = await response.json();

        let tabPanel = document.querySelector(`#tab-contents-${athlete.username}`)
        if (!tabPanel) {
            tabPanel = createTabContents(templateAthlete, athlete, listTab, templateFiles, navTabContent);
        }
        let uploadBtn = document.querySelector(`#btn-upload-${athlete.username}`);
        uploadBtn.disabled = false;
        uploadBtn.addEventListener("click", async (event) => await uploadFiles(event, athlete));

        let fileInput = tabPanel.querySelector(".form-control");
        fileInput.disabled = false;
    }

    if (user.athlete_files.length == 0 && user.athletes.length == 0) {
        let p = document.createElement("p");
        p.innerText = "There are currently no athletes or uploaded files.";
        document.querySelector("#list-files-div").append(p);
    }
}

function createTabContents(templateAthlete, athlete, listTab, templateFiles, navTabContent) {
    let cloneAthlete = templateAthlete.content.cloneNode(true);

    let a = cloneAthlete.querySelector("a");
    a.id = `tab-${athlete.username}`;
    a.href = `#tab-contents-${athlete.username}`;
    a.text = athlete.username;
    listTab.appendChild(a);

    let tabPanel = templateFiles.content.firstElementChild.cloneNode(true);
    tabPanel.id = `tab-contents-${athlete.username}`;

    let uploadBtn = tabPanel.querySelector('input[value="Upload"]');
    uploadBtn.id = `btn-upload-${athlete.username}`;

    navTabContent.appendChild(tabPanel);
    return tabPanel;
}

function createFileLink(templateFile, fileUrl) {
    let cloneFile = templateFile.content.cloneNode(true);
    let aFile = cloneFile.querySelector("a");
    aFile.href = fileUrl;
    let pathArray = fileUrl.split("/");
    aFile.text = pathArray[pathArray.length - 1];
    return aFile;
}

function addAthleteRow(event) {
    let newBlankRow = event.currentTarget.parentElement.cloneNode(true);
    let newInput = newBlankRow.querySelector("input");
    newInput.value = "";
    let controls = document.querySelector("#controls");
    let button = newBlankRow.querySelector("button");
    button.addEventListener("click", addAthleteRow);
    controls.appendChild(newBlankRow);

    event.currentTarget.className = "btn btn-danger btn-remove";
    event.currentTarget.querySelector("i").className = "fas fa-minus";
    event.currentTarget.removeEventListener("click", addAthleteRow);
    event.currentTarget.addEventListener("click", removeAthleteRow);
}

function removeAthleteRow(event) {
    event.currentTarget.parentElement.remove();
}

async function submitRoster() {
    let rosterInputs = document.querySelectorAll('input[name="athlete"]');

    let body = {"athletes": []};
    let currentUser = await getCurrentUser();

    for (let rosterInput of rosterInputs) {
        if (!rosterInput.disabled && rosterInput.value) {
            // get user
            let response = await sendRequest("GET", `${HOST}/api/users/${rosterInput.value}/`);
            if (response.ok) {
                let athlete = await response.json();
                if (athlete.coach == currentUser.url) {
                    body.athletes.push(athlete.id);
                } else {
                    // create offer
                    let body = {'status': 'p', 'recipient': athlete.url};
                    let response = await sendRequest("POST", `${HOST}/api/offers/`, body);
                    if (!response.ok) {
                        let data = await response.json();
                        let alert = createAlert("Could not create offer!", data);
                        document.body.prepend(alert);
                    }
                }
            } else {
                let data = await response.json();
                let alert = createAlert(`Could not retrieve user ${rosterInput.value}!`, data);
                document.body.prepend(alert);
            }
        }
    }
    let response = await sendRequest("PUT", currentUser.url, body);
    location.reload();
}

async function uploadFiles(event, athlete) {
    let form = event.currentTarget.parentElement;
    let inputFormData = new FormData(form);
    let templateFile = document.querySelector("#template-file");

    for (let file of inputFormData.getAll("files")) {
        if (file.size > 0) {
            let submitForm = new FormData();
            submitForm.append("file", file);
            submitForm.append("athlete", athlete.url);

            let response = await sendRequest("POST", `${HOST}/api/athlete-files/`, submitForm, "");
            if (response.ok) {
                let data = await response.json();

                let tabPanel = document.querySelector(`#tab-contents-${athlete.username}`)
                let divFiles = tabPanel.querySelector(".uploaded-files");
                let aFile = createFileLink(templateFile, data["file"]);
                divFiles.appendChild(aFile);
            } else {
                let data = await response.json();
                let alert = createAlert("Could not upload files!", data);
                document.body.prepend(alert);
            }
        }
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    await displayCurrentRoster();
    await displayFiles();
    
    let buttonSubmitRoster = document.querySelector("#button-submit-roster");
    buttonSubmitRoster.addEventListener("click", async () => await submitRoster());
});
