from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user,  logout_user,  login_required,  \
	current_user
from . import auth
from .. import db, mail
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm,  ChangePasswordForm, \
	PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if (not current_user.confirmed 
				and request.endpoint
				and request.blueprint != 'auth'
				and request.endpoint != 'static'
				and request.endpoint != 'main.server_shutdown'):
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed/')
def unconfirmed():
	if (current_user.is_anonymous or current_user.confirmed):
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			next = request.args.get('next')
			if next is None or not next.startswith('/'):
				next = url_for('main.index')
			return redirect(next)
		flash('用户名或密码无效。', 'danger')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('用户已退出。', 'info')
	return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data.lower(),
					  username=form.username.data,
					  password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm Your Account',
			'auth/email/confirm', user=user, token=token)

		flash('一封确认邮件已经发送至你的电子邮箱。', 'info')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>/')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		db.session.commit()
		flash('账户已确认！可以开始使用Jugust博客啦。', 'success')
	else:
		flash('确认链接无效或已过期。', 'danger')
	return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account',
				  'auth/email/confirm', user=current_user, token=token)
	flash('一封新的确认邮件已经发送至你的电子邮箱。', 'info')
	return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash('密码修改成功。', 'success')
			return redirect(url_for('main.index'))
		else:
			flash('密码无效。', 'danger')
	return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user:
			token = user.generate_reset_token()
			send_email(user.email, '重置密码',
						  'auth/email/reset_password',
						  user=user, token=token)
		flash('已向你的带电子邮箱发送了一封帮助你重置密码的邮件。', 'info')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>/', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		if User.reset_password(token, form.password.data):
			db.session.commit()
			flash('密码已更新。', 'success')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data.lower()
			token = current_user.generate_email_change_token(new_email)
			send_email(new_email, '确认你的电子邮箱',
						 'auth/email/change_email',
						 user=current_user, token=token)
			flash('已向你的新邮箱发送了一封用于确认的邮件。 ', 'info')
			return redirect(url_for('main.index'))
		else:
			flash('电子邮箱或密码无效。' ,'danger')
	return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>/')
@login_required
def change_email(token):
	if current_user.change_email(token):
		db.session.commit()
		flash('电子邮箱已更新。', 'success')
	else:
		flash('请求无效。', 'danger')
	return redirect(url_for('main.index'))
	
