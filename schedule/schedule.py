from flask import Blueprint, render_template
import warnings
from utilscbb.constants import year, quadBool
from utilscbb.appsync import get_schedule_data

# Ignore all warnings
warnings.filterwarnings("ignore")


schedule = Blueprint('schedule', __name__)



@schedule.route('/schedule/<id>' , methods=['GET','POST'])
def post_schedule(id):
    data = get_schedule_data(id, year, quadBool)['scheduleData']
    return render_template('schedule.html', data = data)


