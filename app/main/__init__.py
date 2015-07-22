from flask import Blueprint,abort,render_template
main = Blueprint("main",__name__)

from . import views,errors
from ..models import Permission,User

@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)
