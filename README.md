# Item-catalog
Simple item catalog application to store, view and edit data filtered by a 'category'.

## Dependancies and modules
- Python 2.7
- Flask 1.12
- SQLAlchemy / ORM
- sqlite
- oAuth2Client
- httplib2 Module (Python)
- JSON Module (Python)
- Requests Module (Python)
- Bootstrap 4.1
- jQuery 3.3.1
- popper.js 1.14


## Installation and setup
- Fork and Clone Repo
- Run the Database_setup.py file first - this creates the Model and SQLite DB
```
python database_setup.py
```
(If run correctly, you should now see 2 new files, database_setup.pyc and itemcatalog.db)
- Next, run the ItemSeeder.py file to load in some sample data to itemcatalog.db
```
python itemseeder.py
```
(your terminal console should display a 'success' message on completion)

-Log in to App using the Google Sign in button first to initialize the first User (UserID 1)

Every item in the seeder code has a UserID of '1' by default. This user will not exist however until the first user has logged in successfully.
There is no way to edit / delete items through the UI unless you are logged in, but if you try to navigate to the JSON endpoints or Edit / Delete URLs before
the first usere has logged in, you may recieve a error.


## JSON endpoint Usage
There are currently 3 url endpoints which will return JSON objects. These URLs are not visible through the UI.

1. 
```
'/catalog/all/JSON' 
```
Returns a list of all items in the catalog, grouped by category

2. 
```
'/catalog/<item_category>/JSON' 
```
Returns a list of items which are in the category specified in the <item_category> part of the URL. eg;
 '/catalog/snowbaording/JSON' will return a list of all items grouped under the 'snowboarding' category.
For categories with multiple words, simply remove the spaces eg;
'/catalog/indoorsports/JSON' will return items in the 'Indoor Sports' category

3. 
```
'/catalog/JSON'
```
Returns all items in all categories, unfiltered.
