from flask import Blueprint, render_template
import warnings
from utilscbb.constants import year, quadBool
from utilscbb.schedule import call_schedule_api

# Ignore all warnings
warnings.filterwarnings("ignore")


schedule = Blueprint('schedule', __name__)



@schedule.route('/schedule/<id>' , methods=['GET','POST'])
def post_schedule(id):
    data = call_schedule_api(id, year, quadBool)
    return render_template('schedule.html', data = data)


