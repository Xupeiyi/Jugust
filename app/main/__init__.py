from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from flask_login import current_user
from ..models import Permission, Notification


@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)


@main.app_context_processor
def make_template_context():
	if current_user.is_authenticated:
		notification_count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
	else:
		notification_count = None
	return dict(notification_count=notification_count)