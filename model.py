from dataclasses import dataclass, field
from enum import Enum
import random
import pickle
import os
from abc import ABC, abstractmethod


class Universe(Enum):
    STAR_WARS = 'star_wars'
    POKEMON = 'pokemon'
    NINJA_TURTLES = 'ninja_turtles'


@dataclass
class Player:
    name: str = 'unknown'
    weight: int = 0
    height: int = 0
    power: int = field(default_factory=lambda: random.randint(1, 100))


class PlayerFactory:
    @staticmethod
    def create_player(data, universe):
        if universe == Universe.POKEMON:
            return Player(data['name'], data['weight'], data['height'])
        elif universe == Universe.STAR_WARS:
            try:
                weight = int(data['mass'], 0)
                height = int(data['height'], 0)
            except ValueError:
                weight = 0
                height = 0
            return Player(data['name'], weight, height)
        else:
            raise ValueError(f'{universe} not supported yet!')


class IPlayerProvider(ABC):
    API_URLS = {
        Universe.STAR_WARS: 'https://swapi.dev/api/people/',
        Universe.POKEMON: 'https://pokeapi.co/api/v2/pokemon/'
    }

    @abstractmethod
    def get_random_players(self, universe) -> Player:
        pass


@dataclass
class Team:
    name: str
    goalie: Player = None
    defence: list[Player] = None
    offence: list[Player] = None

    @property
    def team_power(self) -> int:
        total_power = 0
        if self.goalie:
            total_power += self.goalie.power
        if self.defence:
            total_power += sum(player.power for player in self.defence)
        if self.offence:
            total_power += sum(player.power for player in self.offence)
        return total_power


class ITeamBuilder(ABC):
    @abstractmethod
    def set_goalie(self, goalie: 'Player'):
        pass

    @abstractmethod
    def set_defence(self, defence: list['Player']):
        pass

    @abstractmethod
    def set_offence(self, offence: list['Player']):
        pass

    @abstractmethod
    def build(self) -> 'Team':
        pass


class SuperSoccerTeamBuilder(ITeamBuilder):
    def __init__(self, name: str):
        self.name = name
        self.goalie = None
        self.defence = None
        self.offence = None

    def set_goalie(self, goalie: Player):
        self.goalie = goalie
        return self

    def set_defence(self, defence: list[Player]):
        self.defence = defence
        return self

    def set_offence(self, offence: list[Player]):
        self.offence = offence
        return self

    def build(self) -> Team:
        return Team(self.name, self.goalie, self.defence, self.offence)


class PlayerCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache_file = "player_cache.pkl"
            cls._instance.players_cache = cls._instance.load_cache()
        return cls._instance

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as file:
                return pickle.load(file)
        return {}

    def save_cache(self):
        with open(self.cache_file, "wb") as file:
            pickle.dump(self.players_cache, file)
