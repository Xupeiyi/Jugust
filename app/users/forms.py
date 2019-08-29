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
from ..models import Role, User


class EditProfileForm(FlaskForm):
	name = StringField('真实姓名', validators=[Length(0, 64)])
	location = StringField('所在地', validators=[Length(0, 64)])
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
	email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64),
													  Email()])
	username = StringField('用户名', validators=[
		DataRequired(), Length(1, 64),
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
			    '用户名只能包含字母，数字，点或下划线')])
	confirmed = BooleanField('已认证')
	role = SelectField('角色', coerce=int)
	name = StringField('真实姓名', validators=[Length(0, 64)])
	location = StringField('所在地', validators=[Length(0, 64)])
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name)
								 for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if (field.data != self.user.email and
				User.query.filter_by(email=field.data).first()):
			raise ValidationError('电子邮箱已被注册。')

	def validation_username(self, field):
		if (field.data != self.user.username and
				User.query.filter_by(username=field.data).first()):
			raise ValidationError('用户名已被注册。')

