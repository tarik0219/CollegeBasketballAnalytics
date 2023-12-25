from flask import Blueprint, render_template
from utilscbb.db import get_db
from utilscbb.constants import dbFileName

home = Blueprint('home', __name__)

@home.route('/')
def home_index():
    query, teamsTable = get_db(dbFileName)
    data = teamsTable.all()
    data.sort(key=lambda x: x["ranks"]["rank"], reverse=False)
    return render_template('index.html', data=data)