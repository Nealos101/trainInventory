trainweb.co.uk - A web-based inventory management system for tracking model railroad collections. The main frameworks in use are FastAPI, SQLModel, and Jinja2 HTML templates.

trainweb.co.uk was created as an assessment project as part of the author's studies with QA Ltd and will become a passion project once graded, aiming to see a continuation of iterations and features introduced in future.
The application domain is registered to Neal Kamper and the app itself is free at the point of use (currently) until maintenance costs become too high or if the application faces abuse.


* * * * * * * * * * * * * * * * KEY FEATURES * * * * * * * * * * * * * * *

- User authentication and permission validation with OAuth 2.0, sessions are managed with JWT tokens.

- Per iteration one, users can manage records via:
	- Create (by anyone)
	- Read (specific scope limitations against permissions apply)
	- Update (specific scope limitations against permissions apply
	- Delete (only admins)

- Per iteration 1.0, users can manage their Inventory records:
	- Create
	- Read
	- Update
	** Delete is currently not supported in iteration 1.0, but is planned for future iterations.

- Dynamic form rendering, including dropdown selectors and enums.

- Secured backend with FastAPI.

- PostgreSQL and/or SQLite database support.


* * * * * * * * * * * * * * * * MAIN TECHNOLOGIES AND DEPENDANCIES * * * * * * * * * * * * * * *

Development is managed on GitHub via https://github.com/Nealos101/trainInventory

- Python 3.10+
- FastAPI
- SQLModel
- Jinja2
- Pydantic
- Uvicorn
- Passlib / JWT / OAuth2
- PostgreSQL or SQLite (configurable)
- Render.com (for deployments)
- paAdmin 4 for DB Management


* * * * * * * * * * * * * * * * DATABASE SCHEMA * * * * * * * * * * * * * * *

Tables:
- owners
- inventory
-- Enums
- permissions


* * * * * * * * * * * * * * * * LOCAL INSTALLATION INSTRUCTIONS * * * * * * * * * * * * * * *

1. Clone the repository from GitHub into local machine.

2. Navigate to the local directory.
	Project root = trainInventory

3. Create a virtual environment (recommended):
	Author used Conda to manage environments and install dependencies.

4. Install dependencies from requirements.txt


* * * * * * * * * * * * * * * * ENVIRONMENT CONFIGS * * * * * * * * * * * * * * *

App requires an .env file in the local root directory, covering the following variables:

secretKey={your secret key}
algorithm=HS256
accessTokenExpireMinutes={insecure apps have long expireMinutes}
refreshTokenExpireDays={insecure apps have long expireDays}
databaseUrl={currently setup for PostgreSQL}


* * * * * * * * * * * * * * * * STARTING THE APP * * * * * * * * * * * * * * *

Using Conda with the installed dependencies, should be able to use the following in terminal:

	fastapi dev main.py
	*** Windows terminals have a problem with the quitting shortcut. Reconfigure terminal or use task manager to shut down python instances if you need to stop the app.


* * * * * * * * * * * * * * * * USING THE APP * * * * * * * * * * * * * * *

When starting the app, FastAPI will provide the URL for the local machine to open in your favourite browser. This will open the app like it does in prod (www.trainweb.co.uk).

As a basic user:

- Either click Account tab or click Register button.
- Click Register, fill in the form and proceed.
- Login.
- Manage details from Account, manage Inventory from Inventory page.
- No user can have an Inventory unless logged in and has the basic permission.
- No user can reset their password in iteration 1.0. An admin has to do it. Later iterations will hopefully introduce this function.

As an admin:

- Follow the basic user steps above to generate an account.
- You need another admin to turn on your admin permission.
- All iteration 1.0 admin actions are available in Account page. Inventory admin actions will come later.
- You are not allowed to manage your own or any other admin's configurations. Only the basic update (in the user panel) are allowed for yourself. Later iterations may change this.
- Supporting users with resetting their password is a key requirement of an admin. Helpful information on how to achieve this can be found in the admin panel.
- Abuse of the admin functions in production will not be tolerated.