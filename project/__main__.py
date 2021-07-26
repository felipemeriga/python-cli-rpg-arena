import sys

from colorama import Fore
import atexit
from project.game import GameFactory
from project.message import print_greetings
from project.save import save_game_state_on_exit, get_saved_game_files


def exit_handler(orchestrator):
    save_game_state_on_exit(orchestrator)
    print('Closing Emberblast!')


def run_project(args):
    try:
        files = get_saved_game_files()
        print_greetings()
        game_factory = GameFactory()
        game_orchestrator = game_factory.new_game()
        atexit.register(exit_handler, game_orchestrator)
        game_orchestrator.execute_game()
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(Fore.RED + 'System shutdown with unexpected error')


if __name__ == '__main__':
    run_project(sys.argv)
