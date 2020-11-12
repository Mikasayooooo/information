from . import admin_blue
from flask import render_template,jsonify,g


@admin_blue.route('/admin_login')
def admin_login():
    return render_template('admin/login.html')