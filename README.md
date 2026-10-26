# CollegeBasketballAnalytics

A Flask web app for men's college basketball: team rankings, live scores, box
scores, schedules, conference standings, NCAA tournament bracketology, and
machine-learning game predictions, all in one place.

> *"Tradition since 2020."* The site is built for recruiters, friends, and
> basketball fans who want to predict games and project how their favorite
> teams will finish the season.

## Features

| Page | Route | What it does |
| --- | --- | --- |
| **Home / Rankings** | `/` | Every Division I team ranked by the model, with conference, offensive and defensive efficiency, and tempo. |
| **Scores** | `/scores/<date>/<filter>` | Daily scoreboard (all games, Top 25, or by conference) with live game state, last play, model predictions, and the spread. |
| **Box Scores** | `/boxscore/<gameId>/<date>` | Player-level box scores pulled from ESPN. |
| **Team Schedule** | `/schedule/<teamId>` | Full schedule with results, predicted scores and win probabilities for remaining games, projected record, NET-based quad records, and ATS record. |
| **Conferences** | `/conference`, `/conference/<conf>` | Conferences ranked by average team strength, plus projected conference standings. |
| **Predict a Game** | `/predict` | Pick any two teams (home/away or neutral site) and get a predicted final score and win probability. |
| **Daily Odds** | `/dailyOdds` | Compares the model's win probability with moneylines across sportsbooks and flags games where the model sees value. |
| **Bracketology** | `/bracketology`, `/bracket` | Projected NCAA tournament field and seeds, with bids per conference. |
| **About / Donate / Disclaimer** | `/about`, `/donate`, `/disclaimer` | Site info and a "buy me a coffee" link. |

## How it works

This repo is the **front end**. It handles routing and rendering only: each
page is a Flask [blueprint](https://flask.palletsprojects.com/en/latest/blueprints/)
with Jinja templates in [templates/](templates/) and team logos and styling in
[static/](static/).

The data and the prediction model live in a separate backend API (see
`CBB_AP_API_URL` in [constants/constants.py](constants/constants.py)). The
app calls it through [utilscbb/api.py](utilscbb/api.py) for:

- team ratings and rankings (`/teamData`)
- scores, schedules, and conference standings
- game predictions (`/predict`, `/predictList`), which return predicted
  scores and a win probability
- sportsbook odds and bracketology projections

Box scores come straight from ESPN's public API
([utilscbb/espn.py](utilscbb/espn.py)).

```
├── app.py            # Flask app; registers all blueprints
├── home/             # Rankings page
├── scores/           # Daily scoreboard
├── boxscores/        # Game box scores
├── schedule/         # Team schedules and projections
├── conference/       # Conference rankings and standings
├── predict/          # Head-to-head game predictor
├── dailyOdds/        # Model vs. sportsbook odds
├── bracketology/     # Tournament projections
├── about/ donate/ disclaimer/
├── utilscbb/         # API, ESPN, and AppSync clients
├── constants/        # API URLs, season year, conference list
├── templates/        # Jinja HTML templates
└── static/           # CSS, images, team logos
```

## History

- **2020**: The project started as a personal college basketball prediction
  site built around a proprietary machine-learning model.
- **November 2023**: This repo was created for the 2023–24 season. Early
  work brought over the data-gathering scripts and trained models, moved
  hosting off Azure to PythonAnywhere, added team data from Bart Torvik (barttorvik.com),
  team records, and Top 25 scores, and set up caching for betting-line data.
- **December 2023**: Added NET rankings and quad records, plus ESPN box
  scores. The app was then refactored so that the data collection and
  prediction model moved into a separate backend API. This repo became a
  lightweight front end that calls that API.
- **January 2024**: The biggest month for features. Added conference
  projections, live "last play" on the scoreboard, mobile-friendly schedules,
  against-the-spread (ATS) records, a new logo and team images, the donate
  page, **Daily Odds**, and **Bracketology**.
- **February–April 2024**: Polished the app through March Madness: quad
  records for remaining games, mobile layout fixes, and season-end date
  handling (the app pins its date to the 2023–24 season window,
  Nov 6, 2023 – Apr 8, 2024).
- **September 2024**: Work started on moving the home page and scores to
  read from DynamoDB (on the `dynamo` branch).

## Getting started

### Requirements

- Python 3.8+
- Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

### Run

```bash
python app.py
```

The app runs at <http://127.0.0.1:5000>. For production, use gunicorn:

```bash
gunicorn app:app
```

### Configuration

- [constants/constants.py](constants/constants.py) sets the backend API URL,
  the season `YEAR`, and the conference list.
- The season date window lives in `inject_now()` in [app.py](app.py). Update
  it for a new season.
- `config/config.py` is git-ignored. It holds the `apiKey` used by the
  optional AWS AppSync client ([utilscbb/appsync.py](utilscbb/appsync.py)).

## Disclaimer

Predictions and odds comparisons are for entertainment and informational
purposes only. See the in-app [disclaimer](templates/disclaimer.html).

## License

See [LICENSE](LICENSE).
