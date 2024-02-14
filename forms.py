from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField,SelectField
from wtforms.validators import DataRequired,InputRequired


class AddParentForm(FlaskForm):
    """Register a family"""

    parentname = StringField('Parent Name',validators=[DataRequired()])
    relation = StringField('Relation to a child',validators=[DataRequired()])
    
    

class ChildAddForm(FlaskForm):
    """Form for adding a child"""
    
    childname = StringField('Child name',validators=[DataRequired()])
    color_choices = [
        ('#f33033cc', 'Red'),
        ('#ba7f5c', 'Green'),
        ('#456dd4cc', 'Blue'),
        ('#df83c5cc','Pink'),
        ('#ccd445cc','Yellow'),
    ]
    
    color = SelectField('Choose a background color for chores', choices=color_choices, validators=[InputRequired()])
   
    
    
    
class ChoreAddForm(FlaskForm):
    """Form for adding a chore"""
    title = StringField('Title',validators=[DataRequired()])
    description = TextAreaField('Description')
    payrate = IntegerField('Payrate',validators=[DataRequired()],render_kw={"size": "5"})
    
    
    
class ChooseChoreToAssignForm(FlaskForm):
    """Form to choose a chore to assign"""
    chore_to_assign = SelectField('Chore to assign', validators=[InputRequired()])
    assigned_by = SelectField('Assigned by', validators=[InputRequired()])