from flask import Flask, render_template, request, redirect, url_for, jsonify
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

@app.route('/gconnect', methods=['POST'])
def login():
    code = request.data
    flow = flow_from_clientsecrets('client_secrets.json', scope='', redirect_uri='postmessage')
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
    
    login_session['username'] = data['name']
    login_session['firstname'] = data['given_name']
    login_session['picture'] = data['picture']

    return login_session['username']

@app.route('/disconnect')
def disconnect():
    access_token = login_session.get('access_token')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    

    if '200' == '200':
        del login_session['username']
        del login_session['picture']

    return redirect("/catalog", code=302)

@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).order_by(asc(Category.name))
    catalogItems = session.query(CatalogItem).order_by(desc(CatalogItem.id)).all()
    return render_template('latestitems.html', items = catalogItems, categories=categories)


@app.route('/catalog/<category_name>/items/')
def categoryItems(category_name):
    ## 'categories' is used to populate the full category list, and is used on the parent template
    ## 'category' is used to search for the individual item
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(friendlyURL=category_name).one()
    category_id = category.id
    catalogItems = session.query(CatalogItem).filter_by(category_id=category_id).order_by(desc(CatalogItem.id)).all()
    return render_template('items.html', items = catalogItems, categories=categories, category=category)

@app.route('/catalog/<category_name>/<item_name>/')
def itemDescription(category_name, item_name):
    category = session.query(Category).filter_by(friendlyURL=category_name).one()
    category_id = category.id
    item = session.query(CatalogItem).filter_by(category_id=category_id, friendlyTitle=item_name).one()
    return render_template('viewItem.html', item=item)

@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.name))
        category = session.query(Category).filter_by(friendlyURL=category_name).one()
        category_id = category.id
        item = session.query(CatalogItem).filter_by(category_id=category_id, friendlyTitle=item_name).one()
        return render_template('editItem.html', item=item, categories=categories)
    else:
        return 'sup'

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

