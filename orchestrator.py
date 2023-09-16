from typing import Dict
from game import Game
from exceptions import GameAlreadyExistError

class Orchestrator:
  """
  ## The Grand O
  - Manages **EVERY** game initiated on Telegram.
  - Communicates with players about their game status or globally (warnings, upcoming games, ban status, money drops).
  - Acts as a central point for systems to communicate about game events and state changes. For instance, the Orchestrator may notify the manager when a player exits a game.
  - Provides high-level insights on the bot's activity.
  - Can be very persistent, but not at the db level. It only monitors the current state of every game being played.
  - Logs these insights for monitoring purposes or specialized logging.
  """
  def __init__(self):
    # dict of games, key = chat_id, value = Game object
    self.games: Dict[str, Game] = {}

  def new_game(self, chat_id):
    """ initializes a new game in a chat """

    # do not start another if there's already one going on
    if chat_id in self.games:
      raise GameAlreadyExistError()

    self.games[chat_id] = Game(chat_id)

