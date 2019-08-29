from flask import render_template, redirect, url_for, flash, request,\
	current_app, make_response
from flask_login import login_required, current_user
from . import users
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Notification
from ..utils import admin_required, permission_required, redirect_back
from ..notifications import push_follow_notification


@users.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['JUGUST_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('/users/user.html', user=user, posts=posts,
						pagination=pagination)

@users.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user._get_current_object())
		db.session.commit()
		flash('档案已更新。', 'success')
		return redirect(url_for('users.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('/users/edit_profile.html', form=form)


@users.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('档案已更新。', 'success')
		return redirect(url_for('users.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('/edit_profile.html', form=form, user=user)



@users.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户无效。', 'danger')
		return redirect(url_for('main.index'))

	if current_user.is_following(user):
		flash('你已经关注该用户。', 'info')
		return redirect_back()

	current_user.follow(user)
	db.session.commit()
	flash('你关注了用户%s。' %username, 'success')
	push_follow_notification(follower=current_user, receiver=user)
	return redirect_back()


@users.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户无效。', 'danger')
		return redirect(url_for('main.index'))
	if not current_user.is_following(user):
		flash('你没有关注该用户。', 'info')
		return redirect_back()
	current_user.unfollow(user)
	db.session.commit()
	flash('你取消了对%s的关注。' % username, 'success')
	return redirect_back()


@users.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户无效。', 'danger')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(
		page, per_page=current_app.config['JUGUST_FOLLOWERS_PER_PAGE'],
		error_out=False)
	follows = [{'user': item.follower, 'timestamp': item.timestamp} 
				 for item in pagination.items]
	return render_template('/users/followers.html', user=user, title="粉丝",
								 endpoint='users.followers', pagination=pagination,
								 follows=follows)


@users.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户无效', 'danger')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(
		page, per_page=current_app.config['JUGUST_FOLLOWERS_PER_PAGE'],
		error_out=False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp}
				 for item in pagination.items]
	return render_template('/users/followers.html', user=user, title="关注",
								 endpoint='users.followed_by', pagination=pagination,
								 follows=follows)
