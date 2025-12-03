
# plik z stanem gry
class GameState:
    #klasa zarzadzania stanem gry przechowuje informacje o aktualnym stanem gry
    
    def __init__(self):
        self._state = {
            "turn_phase": "waiting_for_roll",
            "current_player_index": 0,
            "last_field": None,
            "last_player": None,
            "dice": (1, 1),
            "animation_in_progress": False,
            "mortgage_mode": False,
            "trading": {
                "active": False,
                "target": None,
                "property": None,
                "price": "",
                "phase": ""
            }
        }


#aktualizuje stan gry
    def update_state(self, updates):
        self._state.update(updates)

# Zmienna globalna przechowująca ostatnią akcję w grze
_last_action = ""

def set_last_action(action):
    #ostatnia akcja
    global _last_action
    _last_action = action

def get_last_action():
    return _last_action
#zwaraca osttania akcje
