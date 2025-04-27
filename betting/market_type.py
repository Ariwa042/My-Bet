from django.db import models
from core.models import SPORT_CHOICES

# Market type choices by sport
FOOTBALL_MARKET_CHOICES = [
    ('1x2', 'Win/Draw/Win'),
    ('over_under', 'Over/Under'),
    ('btts', 'Both Teams To Score'),
    ('double_chance', 'Double Chance'),
    ('correct_score', 'Correct Score'),
    ('first_half_over_under', 'First Half Over/Under'),
    ('first_goalscorer', 'First Goalscorer'),
    ('anytime_goalscorer', 'Anytime Goalscorer'),
    ('half_time_result', 'Half Time Result'),
    ('half_time_full_time', 'Half Time/Full Time'),
    ('total_goals', 'Total Goals Over/Under'),
    ('next_goal', 'Next Goal'),
    ('yellow_cards', 'Yellow Cards'),
    ('red_cards', 'Red Cards'),
    ('penalty', 'Penalty'),
    ('player_assists', 'Player Assists'),
]

BASKETBALL_MARKET_CHOICES = [
    ('money_line', 'Money Line'),
    ('point_spread', 'Point Spread'),
    ('over_under', 'Over/Under Points'),
    ('player_points', 'Player Points'),
    ('first_quarter_winner', 'First Quarter Winner'),
]

TENNIS_MARKET_CHOICES = [
    ('match_winner', 'Match Winner'),
    ('set_winner', 'Set Winner'),
    ('correct_score', 'Correct Score'),
    ('total_games', 'Total Games Over/Under'),
    ('player_games', 'Player Games Won'),
]

CRICKET_MARKET_CHOICES = [
    ('match_winner', 'Match Winner'),
    ('innings_runs', 'Innings Runs'),
    ('top_batsman', 'Top Batsman'),
    ('top_bowler', 'Top Bowler'),
    ('total_match_runs', 'Total Match Runs'),
    ('total_match_wickets', 'Total Match Wickets'),
    ('method_of_dismissal', 'Method of Dismissal'),
    ('player_performance', 'Player Performance'),
]

RUGBY_MARKET_CHOICES = [
    ('match_winner', 'Match Winner'),
    ('handicap', 'Handicap'),
    ('total_points', 'Total Points'),
    ('first_try_scorer', 'First Try Scorer'),
    ('anytime_try_scorer', 'Anytime Try Scorer'),
    ('winning_margin', 'Winning Margin'),
    ('half_time_result', 'Half Time Result'),
]

HOCKEY_MARKET_CHOICES = [
    ('match_winner', 'Match Winner'),
    ('puck_line', 'Puck Line'),
    ('total_goals', 'Total Goals'),
    ('period_betting', 'Period Betting'),
    ('team_total_goals', 'Team Total Goals'),
    ('first_goal_scorer', 'First Goal Scorer'),
]

VOLLEYBALL_MARKET_CHOICES = [
    ('match_winner', 'Match Winner'),
    ('set_winner', 'Set Winner'),
    ('total_points', 'Total Points'),
    ('set_score', 'Set Score'),
    ('points_handicap', 'Points Handicap'),
    ('sets_handicap', 'Sets Handicap'),
]

BASEBALL_MARKET_CHOICES = [
    ('money_line', 'Money Line'),
    ('run_line', 'Run Line'),
    ('total_runs', 'Total Runs'),
    ('team_total_runs', 'Team Total Runs'),
    ('first_five_innings', 'First Five Innings'),
    ('innings_runs', 'Innings Runs'),
]

AMERICAN_FOOTBALL_MARKET_CHOICES = [
    ('money_line', 'Money Line'),
    ('point_spread', 'Point Spread'),
    ('total_points', 'Total Points'),
    ('first_touchdown', 'First Touchdown Scorer'),
    ('anytime_touchdown', 'Anytime Touchdown Scorer'),
    ('quarter_betting', 'Quarter Betting'),
    ('half_time_result', 'Half Time Result'),
]

BOXING_MMA_MARKET_CHOICES = [
    ('fight_winner', 'Fight Winner'),
    ('method_of_victory', 'Method of Victory'),
    ('round_betting', 'Round Betting'),
    ('total_rounds', 'Total Rounds'),
    ('fight_to_go_distance', 'Fight to Go Distance'),
    ('knockdown_betting', 'Knockdown Betting'),
]

