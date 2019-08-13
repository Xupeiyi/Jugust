from flask import render_template, redirect, request, url_for, flash, \
	current_app
from flask_login import login_required,  current_user
from . import posts
from .. import db
from ..models import Permission, User, Post, Comment
from .forms import PostForm, CommentForm
from ..decorators import admin_required, permission_required

	
@posts.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if current_user.can(Permission.WRITE) and form.validate_on_submit():
		post = Post(title=form.title.data,
							 body=form.body.data,
							 author=current_user._get_current_object() )
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('main.index')) 
	return render_template('/posts/create_post.html', form=form)


@posts.route('/<int:id>', methods=['GET', 'POST'])
def show_post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
							 			post=post,
						   				author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.', 'success')
		return redirect(url_for('posts.show_post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (post.comments.count() - 1) // \
				 current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	return render_template('/posts/show_post.html', post=post, form=form,
								comments=comments, pagination=pagination)


@posts.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Post.query.get_or_404(id)
	if (current_user != post.author and
			   not current_user.can(Permission.ADMIN)):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		db.session.add(post)
		db.session.commit()
		flash('The post has been updated!', 'success')
		return redirect(url_for('posts.show_post', id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	return render_template('/posts/edit_post.html', form=form)


@posts.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.index'))


@posts.route('/quick_follow/<int:id>/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def quick_follow(id, username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.', 'danger')
		return redirect(url_for('posts.show_post', id=id))
	if current_user.is_following(user):
		flash('You are already following this user.', 'info')
		return redirect(url_for('posts.show_post', id=id))
	current_user.follow(user)
	db.session.commit()
	flash('You are now following %s.' %username, 'success')
	return redirect(url_for('posts.show_post', id=id))


@posts.route('/quick_unfollow/<int:id>/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def quick_unfollow(id, username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.', 'danger')
		return redirect(url_for('posts.show_post', id=id))
	if not current_user.is_following(user):
		flash('You are not following this user.', 'info')
		return redirect(url_for('posts.show_post', id=id))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following %s anymore.' % username, 'success')
	return redirect(url_for('posts.show_post', id=id))


@posts.route('/collect/<int:id>', methods=['POST'])
@login_required
def collect(id):
	post = Post.query.get_or_404(id)
	if current_user.is_collecting(post):
		flash('You have already collected that post!', 'info')
		return redirect(url_for('posts.show_post', id=id))
	current_user.collect(post)
	flash('Post collected!', 'success')
	return redirect(url_for('posts.show_post', id=id))


@posts.route('/uncollect/<int:id>', methods=['POST'])
@login_required
def uncollect(id):
	post = Post.query.get_or_404(id)
	if not current_user.is_collecting(post):
		flash('You have not collected that post yet!', 'info')
		return redirect(url_for('posts.show_post', id=id))
	current_user.uncollect(post)
	flash('Post uncollected!', 'info')
	return redirect(url_for('posts.show_post', id=id))

