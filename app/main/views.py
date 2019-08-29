from flask import render_template, redirect, url_for, abort,flash, request,\
	current_app, make_response
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Permission, Role, User, Post, Comment, Notification
from ..utils import admin_required, permission_required, redirect_back
from ..notifications import push_follow_notification

@main.route('/', methods=['GET', 'POST'])
def index():
	page = request.args.get('page', 1, type=int)
	show_what = ''
	if current_user.is_authenticated:
		show_what = request.cookies.get('show_what', '')
	if show_what == 'show_followed':
		query = current_user.followed_posts
	elif show_what == 'show_collected':
		query = current_user.collected_posts
	else:
		query = Post.query
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['JUGUST_POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('index.html',  posts=posts,
								 show_what=show_what, pagination=pagination)


@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_what', '', max_age=30*24*60*60)
	return resp


@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_what', 'show_followed', max_age=30*24*60*60)
	return resp


@main.route('/collected')
@login_required
def show_collected():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_what','show_collected', max_age=30*24*60*60)
	return resp



@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['JUGUST_COMMENTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	return render_template('moderate.html', comments=comments,
								 pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('.moderate',
								 page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('.moderate', 
								 page=request.args.get('page', 1, type=int)))


@main.route('/notifications')
@login_required
def show_notifications():
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['JUGUST_NOTIFICATION_PER_PAGE']
	notifications = Notification.query.with_parent(current_user)
	filter_rule = request.args.get('filter')
	if filter_rule == 'unread':
		notifications = notifications.filter_by(is_read=False)

	pagination = notifications.order_by(Notification.timestamp.desc())\
								.paginate(page, per_page)
	notifications = pagination.items
	return render_template('notifications.html', pagination=pagination, 
																						notifications=notifications)

@main.route('/notification/read/<int:notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
	notification = Notification.query.get_or_404(notification_id)
	if current_user != notification.receiver:
		abort(403)

	notification.is_read = True
	db.session.commit()
	flash('消息已归档。', 'success')
	return redirect_back()


@main.route('/notifications/read/all', methods=['POST'])
@login_required
def read_all_notifications():
	for notification in current_user.notifications:
		notification.is_read = True
	db.session.commit()
	flash('所有消息已归档。', 'success')
	return redirect_back()


@main.route('/search')
def search():
	q  = request.args.get('q', '').strip()
	if q == '':
		flash('输入标题，内容或用户的关键字。', 'warning')
		return redirect(url_for('.index'))

	category = request.args.get('category', 'post')
	page = request.args.get('page', 1, type=int)
	if category == 'user':
		pagination = User.query.whooshee_search(q).paginate(page, 
										current_app.config['JUGUST_FOLLOWERS_PER_PAGE'])
	else:
		pagination = Post.query.whooshee_search(q).paginate(page, 
												current_app.config['JUGUST_POSTS_PER_PAGE'])
	results = pagination.items
	return render_template('search.html', q=q, results=results, 
	pagination = pagination, category=category)




