from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.schema import ForeignKeyConstraint, PrimaryKeyConstraint

db = SQLAlchemy()

class Parent(db.Model):
    
    """An inddividual family"""
    __tablename__ = "parents"
    
    id = db.Column( db.Integer,primary_key=True)
    
    parentname = db.Column(
        db.Text,
        nullable=False,
    )
    
    relation = db.Column(
        db.Text,
        nullable=False,
    )
    
    parent_back_image = db.Column(
        db.Text,
        default="/static/images/default_parent_background.png",
    )
    face_image = db.Column(
        db.Text,
        default="/static/images/blank_parent_icon.png",
    )
    assignment = db.relationship('Assigned')
    
class Child(db.Model):
    """An individual child"""
    
    __tablename__ = "children"
    
    id = db.Column(db.Integer,primary_key=True)
    
    childname = db.Column(
        db.Text,
        nullable=False,
        unique=True 
    )
    
    child_color = db.Column(db.Text, nullable=False)
    
    child_back_image = db.Column(
        db.Text,
        default="/static/images/default_kid_background.png",
    )
    face_image = db.Column(
        db.Text,
        default="/static/images/blank_parent_icon.png",
    )
    assigned_tasks = db.relationship('Assigned')
    
    
    
class Chore(db.Model):
    """An individual chore"""
    
    __tablename__ = "chores"
    
    id = db.Column(db.Integer,primary_key=True)
    
    title = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    description = db.Column(
        db.Text,
        nullable=True,
        unique=True,
    )
    payrate = db.Column(db.Integer, nullable=False,)
    
    assignment = db.relationship('Assigned')
    
    
    
    
class Assigned(db.Model):
    """Connect a child,chores and a day"""
    
    __tablename__ = "assigned"
   
    # assigned_child = db.Column(db.Integer)
    # assigned_chore = db.Column(db.Integer)    
    # parent_assigned = db.Column(db.Integer)
    # assigned_day = db.Column(db.Integer)
    
    
    assigned_child = db.Column(db.Integer,db.ForeignKey('children.id'))
    
    assigned_chore = db.Column(db.Integer,db.ForeignKey('chores.id'))
    
    parent_assigned = db.Column(db.Integer,db.ForeignKey('parents.id'))
    
    assigned_day = db.Column(db.Integer, nullable=False,)  
    
    done = db.Column(db.Boolean, nullable=False, default=False)
    
    __table_args__ = (
        PrimaryKeyConstraint("assigned_child", "assigned_chore", "parent_assigned", "assigned_day"),
    )
    
    # child = db.relationship('Child', backref=backref('assigned_tasks',ondelete="cascade"))
    
    # chore = db.relationship('Chore', backref=backref('assigned_children',ondelete="cascade"))
    
    # parent = db.relationship('Parent', backref=backref('assigned_children',ondelete="cascade"))


MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6
    
    

def connect_db(app):
    """Connect this database to provided Flask app"""
    db.app=app
    db.init_app(app)