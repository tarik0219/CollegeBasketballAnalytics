import pickle
import numpy as np
import os
import joblib

def changeBool(value):
    if value:
        return 1
    else:
        return 0

def make_prediction(homeData, awayData, siteType):
    if siteType:
        siteType = changeBool(siteType)
        X = np.array([[homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],siteType]])
        X2 = np.array([[awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],siteType]])
        scoresModel = pickle.load(open('models/scores.pkl', 'rb'))
        probModel = pickle.load(open('models/prob.pkl', 'rb'))

        y_pred = scoresModel.predict(X)
        y_pred.tolist()
        y_pred_2 = scoresModel.predict(X2)
        y_pred_2.tolist()
        homeScore = round((y_pred[0][0] + y_pred_2[0][1])/2,1)
        awayScore = round((y_pred[0][1] + y_pred_2[0][0])/2,1)

        y_prob = probModel.predict_proba(X)
        y_prob.tolist()
        y_prob_2 = probModel.predict_proba(X2)
        y_prob_2.tolist()
        prob = round((y_prob[0][1]+y_prob_2[0][0])/2,4)
    
    else:
        siteType = changeBool(siteType)
        X = np.array([[homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],siteType]])
        scoresModel = pickle.load(open('models/scores.pkl', 'rb'))
        probModel = pickle.load(open('models/prob.pkl', 'rb'))

        y_pred = scoresModel.predict(X)
        y_pred.tolist()
        homeScore = round(y_pred[0][0],1)
        awayScore = round(y_pred[0][1],1)

        y_prob = probModel.predict_proba(X)
        y_prob.tolist()
        prob = round(y_prob[0][1],4)

    return homeScore,awayScore,prob 