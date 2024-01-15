from flask import Blueprint, render_template
from utilscbb.api import get_all_team_data

home = Blueprint('home', __name__)

@home.route('/')
def home_index():
    data = get_all_team_data()
    data.sort(key=lambda x: x["ranks"]["rank"], reverse=False)
    return render_template('index.html', data=data)