let cancelWorkoutButton;
let okWorkoutButton;
let deleteWorkoutButton;
let editWorkoutButton;
let postCommentButton;

async function retrieveWorkout(id) {  
    let workoutData = null;
    let response = await sendRequest("GET", `${HOST}/api/workouts/${id}/`);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not retrieve workout data!", data);
        document.body.prepend(alert);
    } else {
        workoutData = await response.json();
        let form = document.querySelector("#form-workout");
        let formData = new FormData(form);

        for (let key of formData.keys()) {
            let selector = `input[name="${key}"], textarea[name="${key}"]`;
            let input = form.querySelector(selector);
            let newVal = workoutData[key];
            if (key == "date") {
                // Creating a valid datetime-local string with the correct local time
                let date = new Date(newVal);
                date = new Date(date.getTime() - (date.getTimezoneOffset() * 60 * 1000)).toISOString(); // get ISO format for local time
                newVal = date.substring(0, newVal.length - 1);    // remove Z (since this is a local time, not UTC)
            }
            if (key != "files") {
                input.value = newVal;
            }
        }

        let input = form.querySelector("select:disabled");
        input.value = workoutData["visibility"];
        // files
        let filesDiv = document.querySelector("#uploaded-files");
        for (let file of workoutData.files) {
            let a = document.createElement("a");
            a.href = file.file;
            let pathArray = file.file.split("/");
            a.text = pathArray[pathArray.length - 1];
            a.className = "me-2";
            filesDiv.appendChild(a);
        }

        // create exercises

        // fetch exercise types
        let exerciseTypeResponse = await sendRequest("GET", `${HOST}/api/exercises/`);
        let exerciseTypes = await exerciseTypeResponse.json();

        //TODO: This should be in its own method.
        for (let i = 0; i < workoutData.exercise_instances.length; i++) {
            let templateExercise = document.querySelector("#template-exercise");
            let divExerciseContainer = templateExercise.content.firstElementChild.cloneNode(true);

            let exerciseTypeLabel = divExerciseContainer.querySelector('.exercise-type');
            exerciseTypeLabel.for = `inputExerciseType${i}`;
    
            let exerciseTypeSelect = divExerciseContainer.querySelector("select");            
            exerciseTypeSelect.id = `inputExerciseType${i}`;
            exerciseTypeSelect.disabled = true;
            
            let splitUrl = workoutData.exercise_instances[i].exercise.split("/");
            let currentExerciseTypeId = splitUrl[splitUrl.length - 2];
            let currentExerciseType = "";

            for (let j = 0; j < exerciseTypes.count; j++) {
                let option = document.createElement("option");
                option.value = exerciseTypes.results[j].id;
                if (currentExerciseTypeId == exerciseTypes.results[j].id) {
                    currentExerciseType = exerciseTypes.results[j];
                }
                option.innerText = exerciseTypes.results[j].name;
                exerciseTypeSelect.append(option);
            }
            
            exerciseTypeSelect.value = currentExerciseType.id;

            let exerciseSetLabel = divExerciseContainer.querySelector('.exercise-sets');
            exerciseSetLabel.for = `inputSets${i}`;

            let exerciseSetInput = divExerciseContainer.querySelector("input[name='sets']");
            exerciseSetInput.id = `inputSets${i}`;
            exerciseSetInput.value = workoutData.exercise_instances[i].sets;
            exerciseSetInput.readOnly = true;

            let exerciseNumberLabel = divExerciseContainer.querySelector('.exercise-number');
            exerciseNumberLabel.for = "for", `inputNumber${i}`;
            exerciseNumberLabel.innerText = currentExerciseType.unit;

            let exerciseNumberInput = divExerciseContainer.querySelector("input[name='number']");
            exerciseNumberInput.id = `inputNumber${i}`;
            exerciseNumberInput.value = workoutData.exercise_instances[i].number;
            exerciseNumberInput.readOnly = true;

            let exercisesDiv = document.querySelector("#div-exercises");
            exercisesDiv.appendChild(divExerciseContainer);
        }
    }
    return workoutData;     
}

function handleCancelDuringWorkoutEdit() {
    location.reload();
}

function handleEditWorkoutButtonClick() {
    let addExerciseButton = document.querySelector("#btn-add-exercise");
    let removeExerciseButton = document.querySelector("#btn-remove-exercise");
    
    setReadOnly(false, "#form-workout");
    document.querySelector("#inputOwner").readOnly = true;  // owner field should still be readonly 

    editWorkoutButton.className += " hide";
    okWorkoutButton.className = okWorkoutButton.className.replace(" hide", "");
    cancelWorkoutButton.className = cancelWorkoutButton.className.replace(" hide", "");
    deleteWorkoutButton.className = deleteWorkoutButton.className.replace(" hide", "");
    addExerciseButton.className = addExerciseButton.className.replace(" hide", "");
    removeExerciseButton.className = removeExerciseButton.className.replace(" hide", "");

    cancelWorkoutButton.addEventListener("click", handleCancelDuringWorkoutEdit);

}

async function deleteWorkout(id) {
    let response = await sendRequest("DELETE", `${HOST}/api/workouts/${id}/`);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert(`Could not delete workout ${id}!`, data);
        document.body.prepend(alert);
    } else {
        window.location.replace("workouts.html");
    }
}

async function updateWorkout(id) {
    let submitForm = generateWorkoutForm();

    let response = await sendRequest("PUT", `${HOST}/api/workouts/${id}/`, submitForm, "");
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not update workout!", data);
        document.body.prepend(alert);
    } else {
        location.reload();
    }
}

function generateWorkoutForm() {
    let form = document.querySelector("#form-workout");

    let formData = new FormData(form);
    let submitForm = new FormData();

    submitForm.append("name", formData.get('name'));
    let date = new Date(formData.get('date')).toISOString();
    submitForm.append("date", date);
    submitForm.append("notes", formData.get("notes"));
    submitForm.append("visibility", formData.get("visibility"));

    // adding exercise instances
    let exerciseInstances = [];
    let exerciseInstancesTypes = formData.getAll("type");
    let exerciseInstancesSets = formData.getAll("sets");
    let exerciseInstancesNumbers = formData.getAll("number");
    for (let i = 0; i < exerciseInstancesTypes.length; i++) {
        exerciseInstances.push({
            exercise: `${HOST}/api/exercises/${exerciseInstancesTypes[i]}/`,
            number: exerciseInstancesNumbers[i],
            sets: exerciseInstancesSets[i]
        });
    }

    submitForm.append("exercise_instances", JSON.stringify(exerciseInstances));
    // adding files
    for (let file of formData.getAll("files")) {
        submitForm.append("files", file);
    }
    return submitForm;
}

async function createWorkout() {
    let submitForm = generateWorkoutForm();

    let response = await sendRequest("POST", `${HOST}/api/workouts/`, submitForm, "");

    if (response.ok) {
        window.location.replace("workouts.html");
    } else {
        let data = await response.json();
        let alert = createAlert("Could not create new workout!", data);
        document.body.prepend(alert);
    }
}

function handleCancelDuringWorkoutCreate() {
    window.location.replace("workouts.html");
}

async function createBlankExercise() {
    let form = document.querySelector("#form-workout");

    let exerciseTypeResponse = await sendRequest("GET", `${HOST}/api/exercises/`);
    let exerciseTypes = await exerciseTypeResponse.json();

    let exerciseTemplate = document.querySelector("#template-exercise");
    let divExerciseContainer = exerciseTemplate.content.firstElementChild.cloneNode(true);
    let exerciseTypeSelect = divExerciseContainer.querySelector("select");
    
    for (let i = 0; i < exerciseTypes.count; i++) {
        let option = document.createElement("option");
        option.value = exerciseTypes.results[i].id;
        option.innerText = exerciseTypes.results[i].name;
        exerciseTypeSelect.append(option);
    }

    let currentExerciseType = exerciseTypes.results[0];
    exerciseTypeSelect.value = currentExerciseType.name;
    
    let divExercises = document.querySelector("#div-exercises");
    divExercises.appendChild(divExerciseContainer);
}

function removeExercise(event) {
    let divExerciseContainers = document.querySelectorAll(".div-exercise-container");
    if (divExerciseContainers && divExerciseContainers.length > 0) {
        divExerciseContainers[divExerciseContainers.length - 1].remove();
    }
}

function addComment(author, text, date, append) {
    /* Taken from https://www.bootdey.com/snippets/view/Simple-Comment-panel#css*/
    let commentList = document.querySelector("#comment-list");
    let listElement = document.createElement("li");
    listElement.className = "media";
    let commentBody = document.createElement("div");
    commentBody.className = "media-body";
    let dateSpan = document.createElement("span");
    dateSpan.className = "text-muted pull-right me-1";
    let smallText = document.createElement("small");
    smallText.className = "text-muted";

    if (date != "Now") {
        let localDate = new Date(date);
        smallText.innerText = localDate.toLocaleString();
    } else {
        smallText.innerText = date;
    }

    dateSpan.appendChild(smallText);
    commentBody.appendChild(dateSpan);
    
    let strong = document.createElement("strong");
    strong.className = "text-success";
    strong.innerText = author;
    commentBody.appendChild(strong);
    let p = document.createElement("p");
    p.innerHTML = text;

    commentBody.appendChild(strong);
    commentBody.appendChild(p);
    listElement.appendChild(commentBody);

    if (append) {
        commentList.append(listElement);
    } else {
        commentList.prepend(listElement);
    }

}

async function createComment(workoutid) {
    let commentArea = document.querySelector("#comment-area");
    let content = commentArea.value;
    let body = {workout: `${HOST}/api/workouts/${workoutid}/`, content: content};

    let response = await sendRequest("POST", `${HOST}/api/comments/`, body);
    if (response.ok) {
        addComment(sessionStorage.getItem("username"), content, "Now", false);
    } else {
        let data = await response.json();
        let alert = createAlert("Failed to create comment!", data);
        document.body.prepend(alert);
    }
}

async function retrieveComments(workoutid) {
    let response = await sendRequest("GET", `${HOST}/api/comments/`);
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not retrieve comments!", data);
        document.body.prepend(alert);
    } else {
        let data = await response.json();
        let comments = data.results;
        for (let comment of comments) {
            let splitArray = comment.workout.split("/");
            if (splitArray[splitArray.length - 2] == workoutid) {
                addComment(comment.owner, comment.content, comment.timestamp, true);
            }
        }
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    cancelWorkoutButton = document.querySelector("#btn-cancel-workout");
    okWorkoutButton = document.querySelector("#btn-ok-workout");
    deleteWorkoutButton = document.querySelector("#btn-delete-workout");
    editWorkoutButton = document.querySelector("#btn-edit-workout");
    let postCommentButton = document.querySelector("#post-comment");
    let divCommentRow = document.querySelector("#div-comment-row");
    let buttonAddExercise = document.querySelector("#btn-add-exercise");
    let buttonRemoveExercise = document.querySelector("#btn-remove-exercise");

    buttonAddExercise.addEventListener("click", createBlankExercise);
    buttonRemoveExercise.addEventListener("click", removeExercise);

    const urlParams = new URLSearchParams(window.location.search);
    let currentUser = await getCurrentUser();

    if (urlParams.has('id')) {
        const id = urlParams.get('id');
        let workoutData = await retrieveWorkout(id);
        await retrieveComments(id);

        if (workoutData["owner"] == currentUser.url) {
            editWorkoutButton.classList.remove("hide");
            editWorkoutButton.addEventListener("click", handleEditWorkoutButtonClick);
            deleteWorkoutButton.addEventListener("click", (async (id) => await deleteWorkout(id)).bind(undefined, id));
            okWorkoutButton.addEventListener("click", (async (id) => await updateWorkout(id)).bind(undefined, id));
            postCommentButton.addEventListener("click", (async (id) => await createComment(id)).bind(undefined, id));
            divCommentRow.className = divCommentRow.className.replace(" hide", "");
        }
    } else {
        await createBlankExercise();
        let ownerInput = document.querySelector("#inputOwner");
        ownerInput.value = currentUser.username;
        setReadOnly(false, "#form-workout");
        ownerInput.readOnly = !ownerInput.readOnly;

        okWorkoutButton.className = okWorkoutButton.className.replace(" hide", "");
        cancelWorkoutButton.className = cancelWorkoutButton.className.replace(" hide", "");
        buttonAddExercise.className = buttonAddExercise.className.replace(" hide", "");
        buttonRemoveExercise.className = buttonRemoveExercise.className.replace(" hide", "");

        okWorkoutButton.addEventListener("click", async () => await createWorkout());
        cancelWorkoutButton.addEventListener("click", handleCancelDuringWorkoutCreate);
        divCommentRow.className += " hide";
    }

});