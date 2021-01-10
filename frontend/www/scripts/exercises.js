async function fetchExerciseTypes(request) {
    let response = await sendRequest("GET", `${HOST}/api/exercises/`);

    if (response.ok) {
        let data = await response.json();

        let exercises = data.results;
        let container = document.getElementById('div-content');
        let exerciseTemplate = document.querySelector("#template-exercise");
        exercises.forEach(exercise => {
            const exerciseAnchor = exerciseTemplate.content.firstElementChild.cloneNode(true);
            exerciseAnchor.href = `exercise.html?id=${exercise.id}`;

            const h5 = exerciseAnchor.querySelector("h5");
            h5.textContent = exercise.name;

            const p = exerciseAnchor.querySelector("p");
            p.textContent = exercise.description;   

            container.appendChild(exerciseAnchor);
        });
    }

    return response;
}

function createExercise() {
    window.location.replace("exercise.html");
}

window.addEventListener("DOMContentLoaded", async () => {
    let createButton = document.querySelector("#btn-create-exercise");
    createButton.addEventListener("click", createExercise);

    let response = await fetchExerciseTypes();
    
    if (!response.ok) {
        let data = await response.json();
        let alert = createAlert("Could not retrieve exercise types!", data);
        document.body.prepend(alert);
    }
});
