import logging
import random
import requests
from model import IPlayerProvider, Universe, PlayerFactory, SuperSoccerTeamBuilder, PlayerCache


class PlayerProvider(IPlayerProvider):
    def __init__(self):
        self.cache = PlayerCache()

    def get_random_players(self, universe, max_retries=3):
        if universe not in self.API_URLS:
            raise ValueError(f'{universe} not supported yet!')

        for _ in range(max_retries):
            rand_num = random.randint(1, 83) if universe == Universe.STAR_WARS else random.randint(1, 1025)
            cache_key = (universe, rand_num)

            if cache_key in self.cache.players_cache:
                return self.cache.players_cache[cache_key]

            api_url = self.API_URLS[universe] + str(rand_num)

            try:
                """ swapi.dev server currently has a problem with their SSL certificate (it has expired), to work 
                around this issue I have used 'verify=False' option to prevent SSL certificate verification, thus still 
                allowing us to use their API. However, I am well aware that this exposes us to certain security risks 
                of establishing secure communication with the given server and should never be used in a production 
                environment. I have included a picture named 'swapi_expired_SSL_cert' in a zip file as a proof. """
                response = requests.get(api_url, verify=False)
                response.raise_for_status()
                data = response.json()
                player = PlayerFactory.create_player(data, universe)
                self.cache.players_cache[cache_key] = player
                self.cache.save_cache()

                return player

            except requests.RequestException as e:
                logging.error(f"Failed to fetch player data from {api_url}: {e}")

        logging.error(f"Failed to fetch player data after {max_retries} retries.")

        return None


class TeamGenerator:
    def __init__(self, player_provider: PlayerProvider):
        self.player_provider = player_provider

    def generate_team(self, universe, size=5):
        if size % 2 == 0:
            raise ValueError('Team size must be an odd number!')

        if universe not in self.player_provider.API_URLS:
            raise ValueError(f'{universe} not supported yet! Try {Universe.STAR_WARS} or {Universe.POKEMON} instead.')

        team_builder = SuperSoccerTeamBuilder(universe.value)
        players = [self.player_provider.get_random_players(universe) for _ in range(size)]

        goalie = max(players, key=lambda x: x.height)
        team_builder.set_goalie(goalie)
        players.remove(goalie)

        defence = sorted(players, key=lambda x: x.weight, reverse=True)[:(size // 2)]
        team_builder.set_defence(defence)
        players = [player for player in players if player not in defence]

        offence = sorted(players, key=lambda x: x.height)[:(size // 2)]
        team_builder.set_offence(offence)

        team = team_builder.build()
        return team
