from random import randrange

from InquirerPy import prompt

from project.conf.conf import get_configuration
from project.questions.new_game import BEGIN_GAME_QUESTIONS
from project.map.map import MapFactory
from project.player.job import dynamic_jobs_classes
from project.player.player import ControlledPlayer, bot_factory
from project.player.race import dynamic_races_classes
from project.utils.constants import GAME_SECTION


class Game:

    def __init__(self, main_player, bots, game_map):
        self.main_player = main_player
        self.bots = bots
        self.game_map = game_map
        self.turns = {1: []}

    # The turn order is calculated based on the will of the character, the players are sorted
    #  based on the following equation: (will/10) * (dice result), the number of the dice sides
    #  can be configured in the main configuration file
    def calculate_turn_order(self):
        players = []
        turn = 0
        if not self.turns:
            turn = 1
            self.turns[turn] = []
        else:
            turn = list(self.turns)[-1] + 1
            self.turns[turn] = []
        players.extend(self.bots)
        players.append(self.main_player)
        players.sort(key=lambda x: (x.will / 10) * randrange(get_configuration(GAME_SECTION).get('dice_sides', 6)),
                     reverse=True)
        self.turns[turn] = players

    def init_game(self):
        raise NotImplementedError('Game::to_string() should be implemented!')


class Deathmatch(Game):

    def __init__(self, main_player, bots, game_map):
        super(Deathmatch, self).__init__(main_player, bots, game_map)

    def init_game(self):
        pass


class GameFactory:
    def __init__(self):
        self.begin_question_results = None

    def new_game(self):
        self.begin_question_results = prompt(BEGIN_GAME_QUESTIONS)
        main_player = self.init_players()
        main_player.earn_xp(100)

        bots = self.init_bots()

        game_map = self.init_map()

        if self.begin_question_results.get('game') == 'Deathmatch':
            game = Deathmatch(main_player, bots, game_map)
            game.calculate_turn_order()
            return game

    def init_map(self):
        return MapFactory().create_map()

    def init_players(self):
        return ControlledPlayer(self.begin_question_results.get('name'),
                                dynamic_jobs_classes[self.begin_question_results.get('job')](),
                                dynamic_races_classes[self.begin_question_results.get('race')]())

    def init_bots(self):
        return bot_factory(self.begin_question_results.get('bots_number'))
