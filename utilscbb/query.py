


def get_schedule_query():
    stringQuery = """
        query ($teamID: String!, $year: Int!, $netRank: Boolean!) {
          scheduleData(teamID: $teamID, year: $year, netRank: $netRank) {
            teamID
    year
    games {
      opponentName
      opponentScore
      score
      completed
      quad
      scorePrediction
      time
      venue
      winProbability
      opponentId
      neutralSite
      gameType
      gameId
      date
      dateString
      opponentScorePrediction
      result
      opponentData {
        TempoRating
        defRating
        conference
        offRating
        ranks {
          rank
          net_rank
        }
        teamName
      }
    }
    teamData {
      defRating
      offRating
      TempoRating
      teamName
      ranks {
        rank
      }
      conference
    }
    quadRecords {
      quad1 {
        losses
        wins
      }
      quad3 {
        losses
        wins
      }
      quad4 {
        losses
        wins
      }
      quad2 {
        losses
        wins
      }
    }
    records {
      projectedWin
      confLoss
      confProjectedLoss
      confProjectedWin
      confWin
      loss
      projectedLoss
      win
    }
                }
        }
        """
    return stringQuery