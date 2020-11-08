from flask import render_template
from  . import profile_blue

@profile_blue.route('/user_index')
def user_index():
    return render_template('news/user.html')