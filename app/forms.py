from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class PostForm(Form):
    title = StringField('Title:', validators=[DataRequired()])
    category = SelectField(u'Post Categories', coerce=int, choices=[(1,'Networking'), (2,'Virtualization'), (3,'Python'), (4,'Security')])
    body = TextAreaField('Body:', validators=[DataRequired()])
    submit = SubmitField('Submit')




