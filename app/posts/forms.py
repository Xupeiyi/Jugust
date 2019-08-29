from flask_wtf import FlaskForm
from wtforms import (
	StringField, 
	TextAreaField, 
	BooleanField,
	SelectField, 
	SubmitField
)
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User


class PostForm(FlaskForm):
	title = StringField('标题', validators=[DataRequired()])
	body = PageDownField("内容", validators=[DataRequired()])
	submit = SubmitField('提交')


class CommentForm(FlaskForm):
	body = PageDownField('', validators=[DataRequired()])
	submit = SubmitField('提交')
			