from flask import Blueprint, render_template


disclaimer = Blueprint('disclaimer', __name__)



@disclaimer.route('/disclaimer')
def disclaimer_inded():
    return render_template("disclaimer.html")
