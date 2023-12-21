from flask import Flask, redirect, url_for, render_template, request,send_from_directory
from flask_bootstrap import Bootstrap
from home.home import home
from datetime import datetime, timedelta
from scores.scores import bs
from schedule.schedule import schedule
from conference.conference import conference
from predict.predict import predict
# from boxscores.boxscores import boxscore
# from history.history import history
# from bracketology.bracketology import bracket
from donate.donate import donate
from about.about import about
from disclaimer.disclaimer import  disclaimer




app = Flask(__name__, static_folder='static')   
Bootstrap(app)

app.config['SECRET_KEY'] = 'secret'

app.register_blueprint(home, url_prefix='/')
app.register_blueprint(bs)
app.register_blueprint(schedule)
app.register_blueprint(conference)
app.register_blueprint(predict)
# app.register_blueprint(boxscore)
# app.register_blueprint(history)
# app.register_blueprint(bracket)
app.register_blueprint(donate)
app.register_blueprint(about)
app.register_blueprint(disclaimer)

@app.context_processor
def inject_now():
    if (datetime.utcnow() - timedelta(hours = 9)).date() < datetime.strptime("20231106", '%Y%m%d').date():
        date = "2023-11-06"
    elif (datetime.utcnow() - timedelta(hours = 9)).date() > datetime.strptime("20240403", '%Y%m%d').date():
        date = "2024-04-03"
    else:
        date = (datetime.utcnow() - timedelta(hours = 9)).strftime('%Y-%m-%d')
    return {'now': date}

@app.route('/ads.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

if __name__ == '__main__':
    app.run() 