class NavBar extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.innerHTML = `
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold ms-5 me-3" href="#">SecFit</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse ms-1" id="navbarNavAltMarkup">
            <div class="navbar-nav me-auto">
                <a class="nav-link" id="nav-index" href="index.html">Home</a>
                <a class="nav-link hide" id="nav-workouts" href="workouts.html">Workouts</a>
                <a class="nav-link hide" id="nav-exercises" href="exercises.html">Exercises</a>
                <a class="nav-link hide" id="nav-mycoach" href="mycoach.html">Coach</a>
                <a class="nav-link hide" id="nav-myathletes" href="myathletes.html">Athletes</a>
                <hr>
            </div>
            <div class="my-2 my-lg-0 me-5">
                <a role="button" class="btn btn-primary hide" id="btn-register" href="register.html">Register</a>
                <a role="button" class="btn btn-secondary hide" id="btn-login-nav" href="login.html">Log in</a>
                <a role="button" class="btn btn-secondary hide" id="btn-logout" href="logout.html">Log out</a>
            </div>
            </div>
        </div>
        </nav>
        `;

        
    }
}

customElements.define('navbar-el', NavBar);