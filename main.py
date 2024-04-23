from team_generator import PlayerProvider, TeamGenerator
from model import Universe
from simulation import simulate_match


if __name__ == '__main__':
    player_provider = PlayerProvider()
    generator = TeamGenerator(player_provider)

    print("\nSTAR WARS TEAM:")
    team1 = generator.generate_team(Universe.STAR_WARS)
    print(team1)
    print('Total team power: {}'.format(team1.team_power))

    print("\nPOKEMON TEAM:")
    team2 = generator.generate_team(Universe.POKEMON)
    print(team2)
    print('Total team power: {}'.format(team2.team_power))

    print('\nMATCH RESULTS:')
    print(simulate_match(team1, team2))
