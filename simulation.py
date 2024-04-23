import random


def generate_goals(team, num_goals):
    goals = []
    for _ in range(num_goals):
        scoring_player = random.choice([team.goalie] + team.defence + team.offence)
        goals.append(f"{scoring_player.name} scored for {team.name}!")
    return goals


def generate_events(team, num_events):
    events = []
    for _ in range(num_events):
        event_player = random.choice([team.goalie] + team.defence + team.offence)
        event_type = random.choice(["tackle", "save", "shoot"])
        events.append(f"{event_player.name} {event_type}s for {team.name}!")
    return events


def simulate_match(team_1, team_2):
    winner = max(team_1, team_2, key=lambda team: team.team_power)
    loser = min(team_1, team_2, key=lambda team: team.team_power)

    winner_goals = random.randint(3, 6)
    loser_goals = random.randint(1, 3)

    winner_highlights = generate_goals(winner, winner_goals)
    loser_highlights = generate_goals(loser, loser_goals)
    match_events = generate_events(random.choice([winner, loser]), random.randint(1, 4))

    highlights = winner_highlights + loser_highlights + match_events
    random.shuffle(highlights)

    if winner_goals != loser_goals:
        result_str = f"{winner.name} WON AGAINST {loser.name} WITH A SCORE OF {winner_goals} : {loser_goals}!"
    else:
        result_str = f"IT'S A DRAW WITH A SCORE OF {winner_goals} : {loser_goals}!"

    highlights.append(result_str)

    return highlights
