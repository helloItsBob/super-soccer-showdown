from unittest.mock import Mock
import pytest
from model import Player, PlayerFactory, Team, SuperSoccerTeamBuilder, PlayerCache, Universe
from simulation import generate_goals, generate_events, simulate_match
from team_generator import PlayerProvider, TeamGenerator


@pytest.fixture
def sample_team_1():
    return Team(name='STAR_WARS',
                goalie=Player(name='Tion Medon', weight=80, height=206, power=18),
                defence=[Player(name='Darth Maul', weight=80, height=175, power=85),
                         Player(name='Qui-Gon Jinn', weight=89, height=193, power=59)],
                offence=[Player(name='Wedge Antilles', weight=77, height=170, power=6),
                         Player(name='Plo Koon', weight=80, height=188, power=16)])


@pytest.fixture
def sample_team_2():
    return Team(name='POKEMON', goalie=Player(name='abra', weight=195, height=9, power=97),
                defence=[Player(name='machop', weight=195, height=8, power=30),
                         Player(name='victini', weight=40, height=4, power=74)],
                offence=[Player(name='woobat', weight=21, height=4, power=44),
                         Player(name='chimecho', weight=10, height=6, power=14)])


@pytest.fixture
def sample_team_generator():
    player_provider = PlayerProvider()
    return TeamGenerator(player_provider)


@pytest.fixture
def mock_requests_get(monkeypatch):
    mock_response = Mock()
    mock_response.json.return_value = {"name": "Test Player", "weight": 70, "height": 180}
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)


class TestModel:

    def test_create_player_pokemon(self):
        data = {'name': 'Pikachu', 'weight': 60, 'height': 40}
        player = PlayerFactory.create_player(data, Universe.POKEMON)
        assert player.name == 'Pikachu'
        assert player.weight == 60
        assert player.height == 40

    def test_create_player_star_wars(self):
        data = {'name': 'Luke Skywalker', 'mass': '77', 'height': '172'}
        player = PlayerFactory.create_player(data, Universe.STAR_WARS)
        assert player.name == 'Luke Skywalker'
        assert player.weight == 77
        assert player.height == 172

    def test_create_player_invalid_universe(self):
        with pytest.raises(ValueError) as exc_info:
            data = {'name': 'Invalid Player'}
            PlayerFactory.create_player(data, Universe.NINJA_TURTLES)
        assert str(exc_info.value) == 'Universe.NINJA_TURTLES not supported yet!'

    def test_team_creation(self):
        goalie = Player('Goalie', 80, 180)
        defence = [Player('Defender1', 70, 170), Player('Defender2', 75, 175)]
        offence = [Player('Attacker1', 65, 160), Player('Attacker2', 70, 165)]

        team = Team('Test Team', goalie, defence, offence)
        assert team.name == 'Test Team'
        assert team.goalie == goalie
        assert team.defence == defence
        assert team.offence == offence

    def test_team_power(self):
        goalie = Player('Goalie', 80, 180, 90)
        defence = [Player('Defender1', 70, 170, 80), Player('Defender2', 75, 175, 85)]
        offence = [Player('Attacker1', 65, 160, 70), Player('Attacker2', 70, 165, 75)]

        team = Team('Test Team', goalie, defence, offence)
        expected_total_power = (goalie.power + sum(player.power for player in defence) +
                                sum(player.power for player in offence))
        assert team.team_power == expected_total_power

    def test_team_builder(self):
        builder = SuperSoccerTeamBuilder('Test Team')
        goalie = Player('Goalie', 80, 180)
        defence = [Player('Defender1', 70, 170), Player('Defender2', 75, 175)]
        offence = [Player('Attacker1', 65, 160), Player('Attacker2', 70, 165)]

        team = builder.set_goalie(goalie).set_defence(defence).set_offence(offence).build()

        assert team.name == 'Test Team'
        assert team.goalie == goalie
        assert team.defence == defence
        assert team.offence == offence

    def test_player_cache(self):
        cache = PlayerCache()
        assert isinstance(cache.players_cache, dict)

        cache.players_cache['test_key'] = 'test_value'
        cache.save_cache()

        new_cache = PlayerCache()
        assert new_cache.players_cache['test_key'] == 'test_value'


class TestSimulation:

    def test_generate_goals(self, sample_team_1):
        num_goals = 5
        goals = generate_goals(sample_team_1, num_goals)
        assert len(goals) == num_goals
        for goal in goals:
            assert f"{sample_team_1.name}" in goal

    def test_generate_events(self, sample_team_1):
        num_events = 4
        events = generate_events(sample_team_1, num_events)
        assert len(events) == num_events
        for event in events:
            assert f"{sample_team_1.name}" in event

    def test_simulate_match(self, sample_team_1, sample_team_2):
        team_1 = sample_team_1
        team_2 = sample_team_2
        highlights = simulate_match(team_1, team_2)
        assert isinstance(highlights, list)
        assert len(highlights) > 0
        assert any(team_1.name in highlight for highlight in highlights)
        assert any(team_2.name in highlight for highlight in highlights)
        assert any("WON AGAINST" in highlight for highlight in highlights) or any(
            "IT'S A DRAW" in highlight for highlight in highlights)


class TestTeamGenerator:

    def test_player_provider_get_random_players(self, mock_requests_get, sample_team_generator):
        player = sample_team_generator.player_provider.get_random_players(Universe.STAR_WARS)
        assert isinstance(player, Player)

    def test_team_generator_generate_team(self, mock_requests_get, sample_team_generator):
        size = 7
        team = sample_team_generator.generate_team(Universe.STAR_WARS, size)
        assert isinstance(team, Team)
        assert len(team.defence) == len(team.offence) == size // 2
        assert team.goalie is not None
        assert team.name == Universe.STAR_WARS.value

    def test_team_generator_generate_team_even_size(self, mock_requests_get, sample_team_generator):
        with pytest.raises(ValueError) as exc_info:
            sample_team_generator.generate_team(Universe.STAR_WARS, 4)
        assert str(exc_info.value) == 'Team size must be an odd number!'

    def test_team_generator_generate_team_unsupported_universe(self, mock_requests_get, sample_team_generator):
        with pytest.raises(ValueError) as exc_info:
            sample_team_generator.player_provider.get_random_players(Universe.NINJA_TURTLES)
        assert str(exc_info.value) == 'Universe.NINJA_TURTLES not supported yet!'
