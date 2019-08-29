from flask import render_template, redirect, request, url_for, flash, \
	current_app
from flask_login import login_required,  current_user
from . import posts
from .. import db
from ..models import Permission, User, Post, Comment
from .forms import PostForm, CommentForm
from ..utils import admin_required, permission_required, redirect_back
from ..notifications import push_collect_notification, push_follow_notification,\
													push_comment_notification
	
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
		flash('文章已创建！', 'success')
		return redirect(url_for('posts.show_post', id=post.id)) 
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
		flash('评论已发布！', 'success')
		if current_user != post.author:
			push_comment_notification(id=post.id, receiver=post.author)
		return redirect_back()

	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (post.comments.count() - 1) // \
				 current_app.config['JUGUST_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
		page, per_page=current_app.config['JUGUST_COMMENTS_PER_PAGE'],
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
		flash('文章已更新！', 'success')
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
    flash('文章已删除！', 'success')
    return redirect(url_for('main.index'))



@posts.route('/collect/<int:id>', methods=['POST'])
@login_required
def collect(id):
	post = Post.query.get_or_404(id)
	if current_user.is_collecting(post):
		flash('你已经收藏了此文章。', 'info')
		return redirect_back()
	current_user.collect(post)
	flash('文章已收藏！', 'success')

	if current_user !=post.author:
		push_collect_notification(collector=current_user, id=id, receiver=post.author)

	return redirect_back()


@posts.route('/uncollect/<int:id>', methods=['POST'])
@login_required
def uncollect(id):
	post = Post.query.get_or_404(id)
	if not current_user.is_collecting(post):
		flash('你还没有收藏此文章！', 'info')
		return redirect(url_for('posts.show_post', id=id))
	current_user.uncollect(post)
	flash('收藏已取消！', 'info')
	return redirect_back()

