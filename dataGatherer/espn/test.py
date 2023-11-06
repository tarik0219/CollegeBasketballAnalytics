from get_games import get_games, add_odds, add_team_data, add_prediction, add_scores
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")


# games = get_games("20230403")
# games = add_odds(games)
# games = add_team_data(games)
# games = add_prediction(games)
add_scores("20230403",'games.csv')