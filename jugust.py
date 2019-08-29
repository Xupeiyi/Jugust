import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()


import sys
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import (
	Permission, 
	Role, 
	Follow,  								
	User, 
	Post, 
	Comment,
	Collect, 
	Notification
)


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User, Follow=Follow, Role=Role,
						  Permission=Permission, Post=Post, Comment=Comment,
						  Collect=Collect, Notification=Notification)



@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
						   help='Run tests under code coverage.')
@click.argument('test_names', nargs=-1)
def test(coverage, test_names):
	"""Run the unit tests."""
	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import subprocess
		os.environ['FLASK_COVERAGE'] = '1'
		sys.exit(subprocess.call(sys.argv))

	import unittest
	if test_names:
		tests = unittest.TestLoader().loadTestsFromNames(test_names)
	else:
		tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	if COV:
		COV.stop()
		COV.save()
		print('Coverage Summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()
