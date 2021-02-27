# SecFit

SecFit (Secure Fitness) is a hybrid mobile application for fitness logging.

## Deploy with Docker

### Prerequisites:

Docker

Git

Windows hosts must use Education or more advanced versions to run Docker \
Download: https://innsida.ntnu.no/wiki/-/wiki/English/Microsoft+Windows+10

### Install:

$ git clone https://gitlab.stud.idi.ntnu.no/kyleo/secfit.git \
$ cd secfit/

### Run:

$ docker-compose up --build \
Hosts the application on http://localhost:9090 with default settings


## Technology
- **deployment** Docker
- **web** Nginx
- **database** Postgre SQL
- **backend** Django 3 with Django REST framework
- **application** 
    - **browser** - HTML5/CSS/JS, Bootstrap v5 (no jQuery dependency)
    - **mobile** Apache Cordova (uses same website)
- **authentication** JWT


## Code and structure

.gitlab-ci.yml - gitlab ci
requirements.txt - Python requirements
package.json - Some node.js requirements, this is needed for cordova

- **secfit/** django project folder containing the project modules
  - **<application_name>/** - generic structure of a django application
    - **admins.py** - file contaning definitions to connect models to the django admin panel
    - **urls.py** - contains mapping between urls and views
    - **models.py** - contains data models
    - **permissions.py** - contains custom permissions that govern access
    - **serializers.py** - contains serializer definitions for sending data between backend and frontend
    - **parsers.py** - contains custom parsers for parsing the body of HTTP requests
    - **tests/** - contains tests for the module. [View Testing in Django](https://docs.djangoproject.com/en/2.1/topics/testing/) for more.
    - **views.py** - Controller in MVC. Methods for rendering and accepting user data
    - **forms.py**  -  definitions of forms. Used to render html forms and verify user input
    - **settings.py** - Contains important settings at the application and/or project level
    - **Procfile** - Procfile for backend heroku deployment
  - **media/** - directory for file uploads (need to commit it for heroku)
  - **comments/** - application handling user comments and reactions
  - **secfit/** - The projects main module containing project-level settings.
  - **users/** - application handling users and requests
  - **workouts/** - application handling exercises and workouts
  - **manage.py** - entry point for running the project.
  - **seed.json** - contains seed data for the project to get it up and running quickly (coming soon)



## Local setup
It's recommended to have a look at: https://www.djangoproject.com/start/
Just as important is the Django REST guide: https://www.django-rest-framework.org/

Create a virtualenv https://docs.python-guide.org/dev/virtualenvs/


### Django

Installation with examples for Ubuntu. Windows and OSX is mostly the same

Fork the project and clone it to your machine.

#### Setup and activation of virtualenv (env that prevents python packages from being installed globaly on the machine)
Naviagate into the project folder, and create your own virtual environment


#### Install python requirements

`pip install -r requirements.txt`


#### Migrate database

`python manage.py migrate`


#### Create superuser

Create a local admin user by entering the following command:

`python manage.py createsuperuser`

Only username and password is required


#### Start the app

`python manage.py runserver`


#### Add initial data

You can add initial data either by going to the url the app is running on locally and adding `/admin` to the url.

Add some categories and you should be all set.

Or by entering 

`python manage.py loaddata seed.json`

### Cordova
Cordova CLI guide: https://cordova.apache.org/docs/en/latest/guide/cli/
If you want to run this as a mobile application
- Navigate to the frontend directory
- For android, do `cordova run android`
- For ios, do `cordova run ios`
- For browser, do `cordova run browser`

It's possible you will need to add the platforms you want to run and build.
The following documentation can be used to run the application in an Android emulator: \
https://cordova.apache.org/docs/en/latest/guide/platforms/android/index.html

## Continuous integration
WARNING: Do not perform penetration testing on Heroku applications

Continuous integration will build the code pushed to master and push it to your heroku app so you get a live version of your latest code by just pushing your code to GitLab.

1. Fork the project at GitLab
2. Create a heroku account and an app for both the frontend and the backend.
3. Select buildpacks for the two apps. The backend uses Python while the frontend uses node.js.
   * Settings > Buildpacks > Add buildpack
4. Set the project in the .gitlab-cs.yml file by replacing `<Your-herokuproject-name>` with the name of the Heroku app you created
`- dpl --provider=heroku --app=<Your-herokuproject-name> --api-key=$HEROKU_STAGING_API_KEY`
5. Set varibles at GitLab
   * settings > ci > Environment Variables
   * `HEROKU_STAGING_API_KEY` = heroku > Account Settings > API Key
6. Add heroku database for the backend
   * Resources > Add ons > search for postgres > add first option
7. Set variables for the backend on Heroku. Settings > Config vars > Reveal vars
   * `DATABASE_URL` = Should be set by default. If not here is where you can find it: Resources > postgress > settings > view credentials > URI
   * `IS_HEROKU` = `IS_HEROKU`
   * `PROCFILE` = `backend/secfit/Procfile`
8. Set variables for the frontend on heroku. Settings > Config vars > Reveal vars. Insert the URL for your backend app.
   * `BACKEND_HOST` = `http://<SECFIT_BACKEND>.herokuapp.com`
   * `PROCFILE` = `frontend/Procfile`
9. Push the repository to both of the heroku applications https://devcenter.heroku.com/articles/git 
   * git push git push `<backend-repository>` HEAD:master
   * git push git push `<frontend-repository>` HEAD:master
10. On GitLab go to CI / CD in the repository menu and select `Run Pipeline` if it has not already started. When both stages complete the app should be available on heroku. Staging will fail from timeout as Heroku does not give the propper response to end the job. But the log should state that the app was deployed.
11. Setup the applications database.
   * Install heroku CLI by following: https://devcenter.heroku.com/articles/heroku-cli
   * Log in to the Heroku CLI by entering `heroku login`. This opens a webbrowser and you accept the login request.
   * Migrate database by entering
   `heroku run python manage.py migrate -a <heroku-app-name>`. `Heroku run` will run the folowing command on your heroku instance. Remember to replace `<heroku-app-name>` with your app name
   * and create an admin account by running
   `heroku run python manage.py createsuperuser -a <heroku-app-name>`.
   * seed database `heroku run python manage.py loaddata seed.json -a <heroku-app-name>`
12. On the frontend app, add a config variable for `BACKEND_HOST` = `BACKEND_HOST`

You will also need the heroku multi-procfile buildpack: https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-multi-procfile.
In general, for this application to work (beyond locally), you will need to set the BACKEND_HOST to the URL of the REST API backend.

### Reset Database
`heroku pg:reset DATABASE_URL -a <heroku-app-name>`

