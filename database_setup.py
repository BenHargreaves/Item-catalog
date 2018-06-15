from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    friendlyURL = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'ID': self.id
        }

class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    friendlyTitle = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'category': self.category.name,
            'categoryID': self.category_id,
            'user': self.user.name,
            'userID': self.user_id
        }

    @property
    def categorySerialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'description': self.description,
            'ItemID': self.id,
            'user': self.user.name,
            'userID': self.user_id
        }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)