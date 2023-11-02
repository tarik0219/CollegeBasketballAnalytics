from flask import Blueprint, render_template
from utils.db import query, teamsTable

home = Blueprint('home', __name__)

@home.route('/')
def home_index():
    data = teamsTable.all()
    data.sort(key=lambda x: x["ranks"]["rank"], reverse=False)
    return render_template('index.html', data=data)