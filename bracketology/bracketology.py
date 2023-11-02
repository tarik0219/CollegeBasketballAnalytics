from flask import Blueprint, render_template
from utils.connectDB import connectDB



bracket = Blueprint('bracket', __name__)



@bracket.route('/bracketology')
def bracketology():
    container = connectDB('seed')
    data = list(container.read_all_items())
    data.sort(key=lambda x: (x["seed"] * -1,x["at_large_prob"]), reverse=True)
    return render_template('bracketology.html', data = data)