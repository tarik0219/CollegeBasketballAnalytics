from flask import Blueprint, render_template


donate = Blueprint('donate', __name__)



@donate.route('/donate')
def donate_index():
    return render_template('donate.html')