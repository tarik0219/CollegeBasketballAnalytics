import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from schedule.schedule import simulate
from schedule.schedule import calculate_records,check_conference_tournament,check_after_conference_tournament,is_date_in_past,connectDB
from datetime import datetime, timedelta
import pytz
from unittest.mock import patch, Mock
import pytest




def test_check_conference_tournament():
    # Test when conference is not in JSON file
    assert check_conference_tournament("2023-03-13", "Nonexistent Conference") == False
    
    # Test when date is before conference start date
    assert check_conference_tournament("2023-03-01", "ACC") == False
    
    # Test when date is after conference end date
    assert check_conference_tournament("2023-03-19", "Big East") == False
    
    # Test when date is within conference start and end dates
    assert check_conference_tournament("2023-03-11", "Big Ten") == True
    assert check_conference_tournament("2023-03-11", "Pac-12") == True
    
    # Test with invalid date format
    with pytest.raises(ValueError):
        check_conference_tournament("2023-03", "ACC")

def test_check_after_conference_tournament():
    # Test when conference is not in JSON file
    assert check_after_conference_tournament("2023-03-13", "Nonexistent Conference") == False
    
    # Test when date is before conference end date
    assert check_after_conference_tournament("2023-03-13", "ACC") == True
    
    # Test when date is on conference end date
    assert check_after_conference_tournament("2023-03-17", "Big East") == True
    
    # Test when date is after conference end date
    assert check_after_conference_tournament("2023-03-01", "Big Ten") == False
    
    # Test with invalid date format
    with pytest.raises(ValueError):
        check_after_conference_tournament("2023-03", "Pac-12")




def test_is_date_in_past():
    # Test with current date
    now = datetime.now(pytz.timezone("US/Eastern")).date()
    assert is_date_in_past(now.strftime("%Y-%m-%d")) == False
    
    # Test with future date
    future_date = datetime.now(pytz.timezone("US/Eastern")).date() + timedelta(days=7)
    assert is_date_in_past(future_date.strftime("%Y-%m-%d")) == False
    
    # Test with past date
    past_date = datetime.now(pytz.timezone("US/Eastern")).date() - timedelta(days=7)
    assert is_date_in_past(past_date.strftime("%Y-%m-%d")) == True
    
    # Test with invalid date format
    with pytest.raises(ValueError):
        is_date_in_past("2022-13-31")

def test_simulate():
    probs = [(0.7, "CONF"), (0.6, "REG"), (0.8, "CONF")]
    wins, loss, confWin, confLoss = simulate(probs)
    assert wins == 1
    assert loss == 2
    assert confWin == 1
    assert confLoss == 1

def test_calculate_records():
    data = [
        {
            "completetd": True,
            "gameType": "CONF",
            "result": "W",
            "opponentName": "Test",
            "opponentId": "Test"
        },
        {
            "completetd": True,
            "gameType": "CONF",
            "result": "L",
            "opponentName": "Test",
            "opponentId": "Test"
        },
        {
            "completetd": True,
            "gameType": "NON-CONF",
            "result": "W",
            "opponentName": "Test",
            "opponentId": "Test"
        },
        {
            "completetd": True,
            "gameType": "NON-CONF",
            "result": "L"
        },
        {
            "completetd": False,
            "prob": 50,
            "gameType": "NON-CONF",
            "opponentName": "Test",
            "opponentId": "Test"
        },
        {
            "completetd": False,
            "prob": 60,
            "gameType": "CONF",
            "opponentName": "Test",
            "opponentId": "Test"
        }
    ]
    expected_records = {
        "win" : 2,
        "loss": 2,
        "projectedWin":3,
        "projectedLoss":3,
        "confWin" : 1,
        "confLoss": 1,
        "confProjectedWin":2,
        "confProjectedLoss":1,
        "probs":[(50,"NON-CONF","Test","Test"),(60,"CONF","Test","Test")]
    }
    actual_records = calculate_records(data)
    assert actual_records == expected_records
