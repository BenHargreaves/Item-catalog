from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import CatalogItem, Base, Category, User

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name = "Benji", email='ben@emailtest.com', picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

Category1 = Category(name='Snowboarding', friendlyURL='snowboarding')
session.add(Category1)
session.commit()

Category2 = Category(name='Basketball', friendlyURL='basketball')
session.add(Category2)
session.commit()

Category3 = Category(name='Baseball', friendlyURL='baseball')
session.add(Category3)
session.commit()

Category4 = Category(name='Beach Sport', friendlyURL='beachsport')
session.add(Category4)
session.commit()

Category5 = Category(name='Cycling', friendlyURL='cycling')
session.add(Category5)
session.commit()

Category6 = Category(name='Weightlifting', friendlyURL='weightlifting')
session.add(Category6)
session.commit()

Category7 = Category(name='Track and Field', friendlyURL='trackandfield')
session.add(Category7)
session.commit()

Category8 = Category(name='Indoor Sport', friendlyURL='indoorsport')
session.add(Category8)
session.commit()

Item1 = CatalogItem(title = 'Snowboard', friendlyTitle='snowboard', description = 'A Snowboard! Woohoo!', category_id = 1, user_id = 1)
session.add(Item1)
session.commit()

Item2 = CatalogItem(title = 'Basketball', friendlyTitle='basketball', description = 'Now with turbo bounce tech! Cross your friends into the shadow realm.', category_id = 2, user_id = 1)
session.add(Item2)
session.commit()

Item3 = CatalogItem(title = 'Baseball Bat',friendlyTitle='baseballbat', description = 'Heeeeeere Batter Batter Batter....SWING!', category_id = 3, user_id = 1)
session.add(Item3)
session.commit()

Item9 = CatalogItem(title = 'Baseball Glove',friendlyTitle='baseballglove', description = 'Catch this!', category_id = 3, user_id = 1)
session.add(Item9)
session.commit()

Item4 = CatalogItem(title = 'Spikeball kit',friendlyTitle='spikeballkit', description = 'Bro that def hit the rim. RE-DO!', category_id = 4, user_id = 1)
session.add(Item4)
session.commit()

Item5 = CatalogItem(title = 'Bike',friendlyTitle='bike', description = '8 Speeds, 1 rider, 2 cool', category_id = 5, user_id = 1)
session.add(Item5)
session.commit()

Item6 = CatalogItem(title = 'Squat Rack',friendlyTitle='squatrack', description = 'Never skip leg day', category_id = 6, user_id = 1)
session.add(Item6)
session.commit()

Item7 = CatalogItem(title = 'Javelin', friendlyTitle='javelin', description = 'This baby can really fly!', category_id = 7, user_id = 1)
session.add(Item7)
session.commit()

Item8 = CatalogItem(title = 'Table Tennis set', friendlyTitle='tabletennisset', description = 'Please read safety manual before playing', category_id = 8, user_id = 1)
session.add(Item8)
session.commit()

print "Success!"


