import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilscbb import make_prediction

if __name__ == "__main__":
    homeTeamData = {"average": {
            "offRating": 118.80000000000001,
            "defRating": 95.65,
            "TempoRating": 72.15
        }
    }
    awayTeamData = {"average": {
            "offRating": 112.15,
            "defRating": 92.95,
            "TempoRating": 69.65
        }
    }

    print(make_prediction(homeTeamData,awayTeamData,True))