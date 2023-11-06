import pickle
import numpy as np
import os


def changeBool(value):
    if value:
        return 1
    else:
        return 0

def make_prediction(homeData,awayData,siteType):
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    scoresFile = dir.replace('utils', 'models') + '/scores.pkl'
    probFile = dir.replace('utils', 'models') + '/prob.pkl'
    
    scoresModel = pickle.load(open(scoresFile, 'rb'))
    probModel = pickle.load(open(probFile, 'rb'))

    siteType = changeBool(siteType)

    X = np.array([[homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],siteType]])

    y_pred = scoresModel.predict(X)
    y_pred.tolist()
    y_prob = probModel.predict_proba(X)
    y_prob.tolist()
    

    if siteType == 1:
        X2 = np.array([[awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],siteType]])

        y_pred_2 = scoresModel.predict(X2)
        y_pred_2.tolist()
        y_prob_2 = probModel.predict_proba(X2)
        y_prob_2.tolist()

        homeScore = round((y_pred[0][0] + y_pred_2[0][1])/2,1)
        awayScore = round((y_pred[0][1] + y_pred_2[0][0])/2,1)
        prob = round((y_prob[0][1]+y_prob_2[0][0])/2,4)
    
    else:
        homeScore = round(y_pred[0][0],1)
        awayScore = round(y_pred[0][1],1)
        prob = round(y_prob[0][1],4)

    return homeScore,awayScore,prob 

def make_prediction_cover(homeData,awayData,siteType,line):
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    coverFile = dir.replace('utils', 'models') + '/cover.pkl'
    
    coverModel = pickle.load(open(coverFile, 'rb'))

    siteType = changeBool(siteType)

    X = np.array([[homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],siteType,line]])

    y_prob = coverModel.predict_proba(X)
    y_prob.tolist()
    y = coverModel.predict(X)[0]

    return y_prob[0][1],y


# homeTeamData = {"average": {
#         "offRating": 118.80000000000001,
#         "defRating": 95.65,
#         "TempoRating": 72.15
#     }
# }
# awayTeamData = {"average": {
#         "offRating": 112.15,
#         "defRating": 92.95,
#         "TempoRating": 69.65
#     }
# }

# print(make_prediction(homeTeamData,awayTeamData,True))
