from flask import Blueprint
admin_bp=Blueprint("admin",__name__,url_prefix="/admin")
from .views import *

@admin_bp.before_request
def is_admin_user():
    if request.url.endswith("/admin/login"):
        pass
    else:
        user_id=session.get("user_id")
        is_admin=session.get("is_admin")
        if not user_id or is_admin==False:
            return redirect("/")
