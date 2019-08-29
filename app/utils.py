from functools import wraps
from flask import abort, request, redirect
from flask_login import current_user
from .models import Permission
from urllib.parse import urlparse, urljoin

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not current_user.can(permission):
				abort(403)
			return f(*args, **kwargs)
		return decorated_function
	return decorator

def admin_required(f):
	return permission_required(Permission.ADMIN)(f)


def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and \
		ref_url.netloc == test_url.netloc

def redirect_back(default='index', **kwargs):
	for target in request.args.get('next'), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return redirect(target)
	return redirect(url_for(default, **kwargs))
