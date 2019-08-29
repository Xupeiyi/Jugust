from flask import url_for

from .models import Notification
from . import db

def push_follow_notification(follower, receiver):
	message = '用户 <a href="%s">%s</a> 关注了你。' % \
					   (url_for('users.user', username=follower.username), 
					   	follower.username) 
	notification = Notification(message=message, receiver=receiver)
	db.session.add(notification)
	db.session.commit()


def push_comment_notification(id, receiver, page=1):
	message = '<a href="%s">这篇文章</a>有一条新评论。'% \
						(url_for('posts.show_post', id=id, page=page))
	notification = Notification(message=message, receiver=receiver)
	db.session.add(notification)
	db.session.commit()


def push_collect_notification(collector, id, receiver):
	message = '用户<a href="%s">%s</a>收藏了你的<a href="%s">文章</a>。' % \
					  (url_for('users.user', username=collector.username),
					   collector.username,
					   url_for('posts.show_post', id=id))
	notification = Notification(message=message, receiver=receiver)
	db.session.add(notification)
	db.session.commit()



	