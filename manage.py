#!/usr/bin/env python
#coding=utf-8
import os
from app import create_app, db
from app.models import *
from flask.ext.script import Manager, Shell,Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,Comment=Comment,
    		Post=Post, Permission=Permission,Follow=Follow)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
server = Server(host='0.0.0.0', port=80)
manager.add_command('server', server)

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
    	import sys
    	os.environ['FLASK_COVERAGE'] = '1'
    	os.execvp(sys.executable, [sys.executable] + sys.argv) #启动一个新的进程
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
    	COV.stop()
    	COV.save()
    	print 'Coverage Summary:'
    	COV.report()
    	basedir = os.path.abspath(os.path.dirname(__file__))
    	covdir = os.path.join(basedir, 'tmp/coverage')
    	COV.html_report(directory=covdir)
    	print 'HTML version: file:// % s/index.html' % covdir
    	COV.erase()


@manager.command
def profile(length=25,profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Role,User

    upgrade()
    Role.insert_roles()
    User.add_self_follows()


if __name__ == '__main__':
    manager.run()
