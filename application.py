from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Flask session renamed login_session to avoid conflict with DB session
from flask import session as login_session
from flask import make_response

import httplib2
import json
import requests

from database_setup import CatalogItem, Base, Category, User


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Use Google oAuth to create and authenticate user
@app.route('/gconnect', methods=['POST'])
def login():
    code = request.data
    flow = flow_from_clientsecrets(
        'client_secrets.json', scope='', redirect_uri='postmessage')
    auth_uri = flow.step1_get_authorize_url()
    credentials = flow.step2_exchange(code)

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Load Google user info request into current login session
    login_session['username'] = data['name']
    login_session['firstname'] = data['given_name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Checks if user already exists, else creates a new user
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])

    return login_session['username']


# disconnect user from current login session
@app.route('/disconnect')
def disconnect():
    access_token = login_session.get('access_token')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # If token successfully revoked, delete login session user info
    if '200' == '200':
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['user_id']

    return redirect("/catalog", code=302)


# Home page, default route. Most redirects end back here after
# form posts/user login etc..
# The 'Latest items' page shows most recently added items for all categories,
# and is only visible on this route
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).order_by(asc(Category.name))
    catalogItems = session.query(CatalogItem).order_by(
        desc(CatalogItem.id)).all()
    return render_template(
        'latestitems.html', items=catalogItems, categories=categories)


# List of items for a selected category
@app.route('/catalog/<category_name>/items/')
def categoryItems(category_name):
    # 'categories' is used to populate the full category list
    # 'category' is used to search for the individual items of a category
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(
        friendlyURL=category_name).one()
    category_id = category.id
    catalogItems = session.query(CatalogItem).filter_by(
        category_id=category_id).order_by(desc(CatalogItem.id)).all()
    return render_template('items.html',
                           items=catalogItems,
                           categories=categories, category=category)


# View a single item in detail and provide links to edit / delete if authorized
@app.route('/catalog/<category_name>/<item_name>/')
def itemDescription(category_name, item_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(
        friendlyURL=category_name).one()
    category_id = category.id
    item = session.query(CatalogItem).filter_by(
        category_id=category_id, friendlyTitle=item_name).one()
    return render_template('viewItem.html', item=item, categories=categories)


# Create New Category
@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    # If current user not in login session redirect to homepage
    if 'username' not in login_session:
        flash('You are not logged in!')
        return redirect('/catalog')

    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newCategory.html', categories=categories)
    else:
        newCategory = Category()
        if request.form['name']:
            newCategory.name = request.form['name']
            # FriendlyURL is used for an items route.
            # Without this, items with spaces would cause routing errors.
            friendlyURL = request.form['name'].lower()
            friendlyURL = friendlyURL.replace(' ', '')
            newCategory.friendlyURL = friendlyURL
        session.add(newCategory)
        session.commit()
        flash("New Category Added!")
        return redirect(url_for('catalog'))


# Create new Item
@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        flash('You are not logged in!')
        return redirect('/catalog')

    categories = session.query(Category).order_by(asc(Category.name))

    if request.method == 'GET':
        return render_template('newItem.html', categories=categories)
    else:
        newItem = CatalogItem()
        if request.form['title']:
            newItem.title = request.form['title']
            # FriendlyTitle is used for an items route URL.
            # Removes spaces and transforms to lowercase
            friendlyTitle = request.form['title'].lower()
            friendlyTitle = friendlyTitle.replace(' ', '')
            newItem.friendlyTitle = friendlyTitle
        if request.form['description']:
            newItem.description = request.form['description']
        if request.form['category']:
            category = session.query(Category).filter_by(
                name=request.form['category']).one()
            newItem.category_id = category.id
        newItem.user_id = login_session['user_id']
        session.add(newItem)
        session.commit()
        flash('Item successfully added!')
        return redirect(url_for('catalog'))


# Delete an Item
@app.route(
    '/catalog/<category_name>/<item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(item_name, category_name):
    if 'username' not in login_session:
        flash('You are not logged in!')
        return redirect('/catalog')

    category = session.query(Category).filter_by(
        friendlyURL=category_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    category_id = category.id
    item = session.query(CatalogItem).filter_by(
        category_id=category_id, friendlyTitle=item_name).one()

    if request.method == 'GET':
        if item.user_id != login_session['user_id']:
            # Displays alert that user is not authorized to perform this action
            flash('You are not authorized to delete this item.')
            return redirect(url_for('catalog'))
        return render_template(
            'deleteItem.html', item=item, categories=categories)
    else:
        session.delete(item)
        session.commit()
        flash('Item successfully deleted')
        return redirect(url_for('catalog'))


# Edit an item
@app.route(
    '/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        flash('You are not logged in!')
        return redirect('/catalog')

    category = session.query(Category).filter_by(
        friendlyURL=category_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    category_id = category.id
    item = session.query(CatalogItem).filter_by(
        category_id=category_id, friendlyTitle=item_name).one()

    if request.method == 'GET':
        if item.user_id != login_session['user_id']:
            flash("""
                You are not authorized to edit this item.
                Please create your own items in order to delete.
                """)
            return redirect('catalog')
        return render_template(
            'editItem.html', item=item, categories=categories)
    else:
        if request.form['title']:
            # If Title edited, also update friendlyTitle to keep URL consistent
            item.title = request.form['title']
            friendlyTitle = request.form['title'].lower()
            friendlyTitle = friendlyTitle.replace(' ', '')
            item.friendlyTitle = friendlyTitle
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            newCategory = session.query(Category).filter_by(
                name=request.form['category']).one()
            item.category_id = newCategory.id
        session.add(item)
        session.commit()
        flash('Item successfully edited')
        return redirect(url_for('catalog'))


# Return all items as JSON object, grouped by category
@app.route('/catalog/all/JSON')
def itemsByCategoryJSON():
    category = session.query(Category).all()
    catalogItems = [c.serialize for c in category]
    for ci in catalogItems:
        items = session.query(CatalogItem).filter_by(
            category_id=ci['ID']).all()
        if items != []:
            ci['items'] = [i.categorySerialize for i in items]
    return jsonify(allitems=catalogItems)


# Return all items of category <item_category> specified in request
@app.route('/catalog/<item_category>/JSON')
def itemsFilteredCategoryJSON(item_category):
    category = session.query(Category).filter_by(
        friendlyURL=item_category).one()
    items = session.query(CatalogItem).filter_by(category_id=category.id).all()
    return jsonify(items=[i.categorySerialize for i in items])


# Return all items as JSON objects, unfiltered
@app.route('/catalog/JSON')
def allItemsJSON():
    items = session.query(CatalogItem).all()
    return jsonify(catalogItems=[i.serialize for i in items])


# Helper functions to create and return user details
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Check if user already exists. Else return null
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
