
#gówny plik gry zawiera logike gry interfejxy i glowna petle gry
import pygame
import random
import sys
import textwrap

from Player import Player
from Menu import show_menu
from Fields import generate_board
from State import set_last_action, get_last_action
from Chance_card import apply_chance_card

dice_sound = None

def get_position_coords(position):
#wspolrzedne pol na planszy
    mapping = {
        0: (700, 700), 1: (620, 700), 2: (555, 700), 3: (495, 700), 4: (435, 700),
        5: (375, 700), 6: (315, 700), 7: (255, 700), 8: (195, 700), 9: (135, 700),
        10: (50, 700), 11: (50, 620), 12: (50, 555), 13: (50, 495), 14: (50, 435),
        15: (50, 375), 16: (50, 315), 17: (50, 255), 18: (50, 195), 19: (50, 135),
        20: (50, 50), 21: (135, 50), 22: (195, 50), 23: (255, 50), 24: (315, 50),
        25: (375, 50), 26: (435, 50), 27: (495, 50), 28: (555, 50), 29: (620, 50),
        30: (700, 50), 31: (700, 135), 32: (700, 195), 33: (700, 255), 34: (700, 315),
        35: (700, 375), 36: (700, 435), 37: (700, 495), 38: (700, 555), 39: (700, 620),
    }
    return mapping.get(position, (0, 0))
#glowna klasa zarzadzajaca logika gry i interfejsem
class GameLogic:
    def __init__(self, players, screen):
        #podstawowe zmienne gry
        self.players = players
        self.screen = screen
        self.board = generate_board()
        self.current_player_index = 0
        self.turn_phase = "waiting_for_roll"
        self.last_field = None
        self.last_player = None
        self.house_built_on_current_field = False
        self.dice = (1, 1)
        
        # Zmienne do obsługi animacji
        self.animation_index = 0
        self.animation_timer = 0
        self.dice_animation_active = False
        self.dice_animation_start = 0
        self.dice_animation_frames = []
        self.dice_animation_duration = 1000
        self.dice_animation_speed = 50
        self.dice_animation_last_update = 0
        self.pending_dice_roll = None
        
        # Przyciski i okna interfejsu
        self.pay_jail_button_rect = pygame.Rect(975, 480, 200, 40)
        self.mortgage_mode = False
        self.selected_mortgage_index = 0
        self.show_player_info_window = False
        self.selected_player_info_index = 0
        self.player_info_window = pygame.Rect(300, 100, 600, 600)
        
        # System handlu
        self.trading = {
            "active": False,
            "target": None,
            "property": None,
            "price": "",
            "phase": ""
        }
        
        # Zmienne do obsługi przewijania
        self.properties_scroll_offset = 0
        self.history_scroll_offset = 0
        self.properties_scroll_drag = False
        self.history_scroll_drag = False
        self.properties_scroll_rect = None
        self.history_scroll_rect = None
        
        # Panel boczny
        self.side_panel_width = 300
        self.button_rects = []
        self.player_panel_rects = []
        self.trade_player_btns = []
        self.trade_property_btns = []
        self.mortgage_window = None
        self.mortgage_buttons = []

        self.trade_price_input_rect = None
        self.trade_confirm_rect = None
        self.trade_cancel_rect = None
        self.trade_price_active = False
        
        # Przewijanie nieruchomości w handlu
        self.trade_properties_scroll_offset = 0
        self.trade_properties_scroll_drag = False
        self.trade_properties_scroll_rect = None
        
        # Zegar gry
        self.clock = pygame.time.Clock()
        
        # Przewijanie hipoteki
        self.mortgage_scroll_offset = 0
        self.mortgage_scroll_rect = None

    def start_dice_animation(self):
        #start animacji kostek
        self.dice_animation_active = True
        self.dice_animation_start = pygame.time.get_ticks()
        self.dice_animation_last_update = self.dice_animation_start
        self.animation_index = 0

    def update_dice_animation(self):
        #aktualizacja kostek
        if not self.dice_animation_active:
            return False

        current_time = pygame.time.get_ticks()
        
        # Sprawdz klatki  animacji
        if current_time - self.dice_animation_last_update >= self.dice_animation_speed:
            self.animation_index = (self.animation_index + 1) % len(self.dice_animation_frames)
            self.dice_animation_last_update = current_time
            
            # zatrzymaj animacje i wykonaj ruch
            if current_time - self.dice_animation_start >= self.dice_animation_duration:
                self.dice_animation_active = False
                if self.pending_dice_roll is not None:
                    self.dice = self.pending_dice_roll
                    self.pending_dice_roll = None
                    d1, d2 = self.dice
                    result = self.handle_roll(d1, d2)  # Przekazujemy wynik rzutu
                    if result == "escaped":
                        set_last_action(f"{self.current_player().name} wyszedł z więzienia.")
                    elif result == "stayed":
                        set_last_action(f"{self.current_player().name} zostaje w więzieniu.")
                    elif result == "triple_double":
                        set_last_action(f"{self.current_player().name} wyrzucił 3 dublety i trafia do więzienia!")
                    elif result == "rolled_double":
                        set_last_action(f"{self.current_player().name} wyrzucił dublet! Może rzucić ponownie.")
                    else:
                        set_last_action(f"{self.current_player().name} wykonał ruch.")
                return False
        return True

    def draw_dice_animation(self, screen):
        #rysowanie animacji kostki
        if not self.dice_animation_active or not self.dice_animation_frames:
            return

        # Rysuj obie kostki
        frame1 = self.dice_animation_frames[self.animation_index]
        frame2 = self.dice_animation_frames[(self.animation_index + 16) % len(self.dice_animation_frames)]
        
        # Pozycje kostek na planszy
        screen.blit(frame1, (300, 400))
        screen.blit(frame2, (400, 400))

    def roll_dice(self):
        #rzut kostka i start animacji
        global dice_sound
        self.pending_dice_roll = (random.randint(1, 6), random.randint(1, 6))
        self.start_dice_animation()
        if dice_sound:
            dice_sound.play()
        return self.pending_dice_roll

    def current_player(self):#zwraca aktualnego gracza
        return self.players[self.current_player_index]

    def next_player(self):#przechodzi do nast gracza i resetuje stan gry
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_phase = "waiting_for_roll"
        self.last_field = None
        self.last_player = None
        self.house_built_on_current_field = False
        self.mortgage_mode = False
        self.trading = {"active": False, "target": None, "property": None, "price": "", "phase": ""}
        # Reset flagi przejścia przez START
        if hasattr(self.current_player(), 'passed_start'):
            self.current_player().passed_start = False

    def handle_roll(self, d1, d2):#obsługa wyniku rzutu kostka
        player = self.current_player()

        if player.in_jail:
            if player.jail_turns >= 3:
                # automatycznie wyjdz z więzienia po 3 turach
                player.in_jail = False
                player.jail_turns = 0
                set_last_action(f"{player.name} wyszedł z więzienia po 3 turach.")
                self.turn_phase = "waiting_for_end_turn"
                return "escaped"
            
            escaped = player.try_exit_jail(d1, d2)
            if escaped:
                player.in_jail = False
                player.jail_turns = 0
                self.turn_phase = "waiting_for_end_turn"
                return "escaped"
            else:
                player.jail_turns += 1
                self.turn_phase = "waiting_for_end_turn"
                return "stayed"

        if self.turn_phase != "waiting_for_roll":
            return "gracz nie może teraz rzucać kostką"

        steps = d1 + d2
        # ścieżka animacji
        player.animation_path = []
        current_pos = player.position
        
        # Sprawdzamy czy gracz przejdzie przez START
        will_pass_start = False
        for i in range(1, steps + 1):
            next_pos = (current_pos + i) % 40
            if next_pos < current_pos:
                will_pass_start = True
                break
        
        # Dodajemy pozycje do ścieżki animacji
        for i in range(1, steps + 1):
            next_pos = (current_pos + i) % 40
            player.animation_path.append(next_pos)
            if will_pass_start and next_pos == 0:
                player.passed_start = True  # Oznaczamy, że gracz przeszedł przez START
        
        # Ustawiamy końcową pozycję
        player.position = player.animation_path[-1]
        player.animating = True
        player.animation_start = pygame.time.get_ticks()

        if d1 == d2:
            player.consecutive_doubles += 1
            if player.consecutive_doubles == 3:
                # Tworzymy nową ścieżkę animacji do więzienia
                player.animation_path = []
                current_pos = player.position
                jail_pos = 10  # Pozycja więzienia
                
                # Jeśli gracz jest przed więzieniem
                if current_pos < jail_pos:
                    for pos in range(current_pos + 1, jail_pos + 1):
                        player.animation_path.append(pos)
                # Jeśli gracz jest za więzieniem
                else:
                    # Najpierw do końca planszy
                    for pos in range(current_pos + 1, 40):
                        player.animation_path.append(pos)
                    # Potem od początku do więzienia
                    for pos in range(0, jail_pos + 1):
                        player.animation_path.append(pos)
                
                player.position = jail_pos
                player.animating = True
                player.animation_start = pygame.time.get_ticks()
                player.send_to_jail()
                self.turn_phase = "waiting_for_end_turn"
                set_last_action(f"{player.name} wyrzucił 3 dublety i trafia do więzienia!")
                return "triple_double"
            self.turn_phase = "waiting_for_roll"
            set_last_action(f"{player.name} wyrzucił dublet! Może rzucić ponownie.")
            return "rolled_double"

        player.consecutive_doubles = 0
        self.turn_phase = "waiting_for_end_turn"
        return "moving"

    def finish_animation(self):#koniec animacji ruchu gracza i obsługa akcji związane z polem
        player = self.current_player()
        position = player.position
        self.last_field = self.board[position]
        self.last_player = player

        # sprawdza czy gracz przeszedl przez pole start
        if hasattr(player, 'passed_start') and player.passed_start:
            player.receive(200)
            player.add_history("Otrzymał 200$ za przejście przez START")
            set_last_action(f"{player.name} minął pole START. Otrzymuje 200$")
            player.passed_start = False  
        elif position == 0:
            player.receive(200)
            player.add_history("Otrzymał 200$ za przejście przez START")
            set_last_action(f"{player.name} stanął na polu START. Otrzymuje 200$")

        # Resetujemy ścieżkę animacji
        player.animation_path = []

        if self.last_field.type in ["street", "station", "utility"] and self.last_field.owner is None:
            # Pole jest wolne gracz moze kupic
            self.turn_phase = "waiting_for_buy"
            set_last_action(
                f"{player.name} stanął na polu {self.last_field.name}. Może je kupić za {self.last_field.price}$")
        elif self.last_field.type in ["street", "station", "utility"] and self.last_field.owner != player:
            # Oblicz sumę oczek z kostek
            dice_sum = sum(self.dice)
            # Sprawdza czy gracz ma wszystkie nieruchomości z danej grupy
            if self.last_field.type == "street":
                group_fields = [f for f in self.board if f.type == "street" and f.group == self.last_field.group]
                has_all_group = all(f.owner == self.last_field.owner for f in group_fields)
                rent = self.last_field.calculate_rent(self.board, dice_sum)
                if has_all_group and self.last_field.houses == 0:  # Podwajamy czynsz tylko gdy nie ma domów
                    rent *= 2
            else:
                rent = self.last_field.calculate_rent(self.board, dice_sum)
                
            # Proba zaplaty za czynsz
            if not player.try_pay_or_mortgage(rent, self.last_field.owner):
                set_last_action(f"{player.name} nie może zapłacić czynszu {rent}$! Musi zastawić nieruchomości lub zbankrutować.")
            else:
                player.pay(rent)  # Pobierz czynsz od gracza
                self.last_field.owner.receive(rent)  # Przekaż czynsz właścicielowi
                player.add_history(f"Zapłacił {rent}$ czynszu za {self.last_field.name}")
                self.last_field.owner.add_history(f"Otrzymał {rent}$ czynszu od {player.name} za {self.last_field.name}")
                set_last_action(f"{player.name} stanął na polu {self.last_field.name}. Musi zapłacić {rent}$ czynszu właścicielowi {self.last_field.owner.name}.")
        elif self.last_field.type == "tax":
            # Obsługa pól podatkowych
            if not player.try_pay_or_mortgage(self.last_field.price):
                set_last_action(f"{player.name} nie może zapłacić podatku {self.last_field.price}$! Musi zastawić nieruchomości lub zbankrutować.")
                self.turn_phase = "waiting_for_mortgage"
            else:
                player.add_history(f"Zapłacił {self.last_field.price}$ podatku")
                set_last_action(f"{player.name} stanął na polu {self.last_field.name}. Musi zapłacić podatek {self.last_field.price}$")
        elif self.last_field.type == "gotojail":
            # Obsługa pola "Idź do więzienia"
            player.send_to_jail()
            set_last_action(f"{player.name} stanął na polu {self.last_field.name}. Trafia do więzienia!")
        elif self.last_field.type == "chance":
            # Obsługa pól z kartami szansy
            set_last_action(f"{player.name} stanął na polu {self.last_field.name}. Losuje kartę Szansa...")
            chance_text = apply_chance_card(player, self.players, self.board)
            set_last_action(f"{player.name} wylosował kartę Szansa: {chance_text}")
        else:
            # Obsługa pozostałych pól
            set_last_action(f"{player.name} stanął na polu {self.last_field.name}.")

        # Obsługa dubletów
        if player.consecutive_doubles > 0:
            if not (self.last_field.type in ["street", "station", "utility"] and self.last_field.owner is None):
                self.turn_phase = "waiting_for_roll"

    def draw_player_info_window(self, screen, font_panel):#rysuje okno informacji o graczu
        player = self.players[self.selected_player_info_index]
        shadow_rect = pygame.Rect(self.player_info_window.x + 5, self.player_info_window.y + 5, 
                                self.player_info_window.width, self.player_info_window.height)
        pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=15)
        pygame.draw.rect(screen, (240, 240, 240), self.player_info_window, border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), self.player_info_window, 3, border_radius=15)
        
        font = pygame.font.Font(None, 24)
        name_text = font.render(f"{player.name}", True, (0, 0, 0))
        balance_text = font.render(f"Saldo: {player.balance}$", True, (0, 0, 0))
        properties_text = font.render(f"Nieruchomości:", True, (0, 0, 0))
        
        screen.blit(name_text, (self.player_info_window.x + 20, self.player_info_window.y + 20))
        screen.blit(balance_text, (self.player_info_window.x + 20, self.player_info_window.y + 60))
        screen.blit(properties_text, (self.player_info_window.x + 20, self.player_info_window.y + 100))
        
        # Obszar na nieruchomości z suwakiem
        properties_area = pygame.Rect(
            self.player_info_window.x + 20,
            self.player_info_window.y + 130,
            self.player_info_window.width - 60,
            220  # Zmniejszona wysokość obszaru na nieruchomości
        )
        pygame.draw.rect(screen, (220, 220, 220), properties_area, border_radius=5)
        
        # Rysowanie nieruchomości z kolorowymi ramkami
        y = properties_area.y + 10 - self.properties_scroll_offset
        for prop in player.properties:
            if y + 30 <= properties_area.bottom and y >= properties_area.top - 30:
                prop_rect = pygame.Rect(properties_area.x, y, properties_area.width - 20, 30)
                color = prop.color
                pygame.draw.rect(screen, color, prop_rect, border_radius=3)
                pygame.draw.rect(screen, (0, 0, 0), prop_rect, 1, border_radius=3)
                brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
                text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)
                prop_text = font.render(f"{prop.name} - {prop.price}$", True, text_color)
                text_rect = prop_text.get_rect(center=prop_rect.center)
                screen.blit(prop_text, text_rect)
            y += 40
        # Suwak dla nieruchomości
        self.properties_scroll_rect = pygame.Rect(
            self.player_info_window.right - 30,
            properties_area.y,
            20,
            properties_area.height
        )
        pygame.draw.rect(screen, (180, 180, 180), self.properties_scroll_rect, border_radius=5)
        if len(player.properties) * 40 > properties_area.height:
            scroll_height = int(properties_area.height * (properties_area.height / (len(player.properties) * 40)))
            scroll_y = properties_area.y + int(self.properties_scroll_offset * (properties_area.height - scroll_height) / (len(player.properties) * 40 - properties_area.height))
            scroll_rect = pygame.Rect(self.properties_scroll_rect.x, scroll_y, 20, scroll_height)
            pygame.draw.rect(screen, (100, 100, 100), scroll_rect, border_radius=5)
        # Historia finansów
        history_y = properties_area.bottom + 5 
        font_title = pygame.font.Font(None, 28)
        history_label = font_title.render("Historia finansów:", True, (0, 0, 0))
        screen.blit(history_label, (self.player_info_window.x + 20, history_y))
        # Obszar na historię z suwakiem
        history_area = pygame.Rect(
            self.player_info_window.x + 20,history_y + 35,
            self.player_info_window.width - 60,200 
        )
        pygame.draw.rect(screen, (220, 220, 220), history_area, border_radius=5)
        y = history_area.y + 10 - self.history_scroll_offset
        font_small = pygame.font.Font(None, 24)
        for history_item in player.history:
            if y + 30 <= history_area.bottom and y >= history_area.top - 30:
                entry_rect = pygame.Rect(history_area.x + 5, y, history_area.width - 10, 30)
                pygame.draw.rect(screen, (200, 200, 200), entry_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 100, 100), entry_rect, 2, border_radius=5)
                history_text = font_small.render(f"{history_item}", True, (0, 0, 0))
                text_rect = history_text.get_rect(center=entry_rect.center)
                screen.blit(history_text, text_rect)
            y += 40
        self.history_scroll_rect = pygame.Rect(
            self.player_info_window.right - 30,
            history_area.y,
            20,
            history_area.height
        )
        pygame.draw.rect(screen, (180, 180, 180), self.history_scroll_rect, border_radius=5)
        if len(player.history) * 40 > history_area.height:
            scroll_height = int(history_area.height * (history_area.height / (len(player.history) * 40)))
            scroll_y = history_area.y + int(self.history_scroll_offset * (history_area.height - scroll_height) / (len(player.history) * 40 - history_area.height))
            scroll_rect = pygame.Rect(self.history_scroll_rect.x, scroll_y, 20, scroll_height)
            pygame.draw.rect(screen, (100, 100, 100), scroll_rect, border_radius=5)

        # Przycisk zamknięcia
        close_rect = pygame.Rect(self.player_info_window.x + self.player_info_window.width - 40, 
                               self.player_info_window.y + 10, 30, 30)
        pygame.draw.rect(screen, (200, 0, 0), close_rect)
        x_text = font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (close_rect.x + 7, close_rect.y))
        self.close_info_rect = close_rect

    def close_player_info_window(self):#zamyka okno informacji o graczu i aktualizuje stan gry
        self.show_player_info_window = False
        set_last_action(f"{self.current_player().name} zamknął okno z informacjami.")

    def buy_current_field(self):#próbuje kupić aktualne pole przez gracza
        if self.last_field and self.last_field.owner is None:
            self.last_player.buy_property(self.last_field)
            self.house_built_on_current_field = False
            self.turn_phase = "waiting_for_end_turn"

    def skip_buy(self):#pomija mozliwosc zakupu aktualnego pola
        self.turn_phase = "waiting_for_end_turn"

    def build_house(self):#próbuje zbudować dom na aktualnym polu
        if self.last_player and self.last_field and self.last_player.can_build_house(self.last_field):
            self.last_player.build_house(self.last_field)
            self.house_built_on_current_field = True

    def build_hotel(self):#próbuje zbudować hotel na aktualnym polu
        if self.last_player and self.last_field and self.last_player.can_build_hotel(self.last_field):
            self.last_player.build_hotel(self.last_field)

    
    def handle_mortgage_action(self, screen):#obsługuje akcje związane z hipoteką nieruchomości
        if not self.mortgage_mode:
            self.mortgage_mode = True
            self.selected_mortgage_index = 0
            self.draw_mortgage_window(screen)
            set_last_action(f"{self.current_player().name} otworzył okno hipoteki.")
        else:
            self.exit_mortgage_mode()
            set_last_action(f"{self.current_player().name} zamknął okno hipoteki.")

    def draw_mortgage_window(self, screen):#rysuje okno hipoteki nieruchomości
        window_width = 600
        window_height = 500
        window_x = (screen.get_width() - window_width) // 2
        window_y = (screen.get_height() - window_height) // 2
        
        # Rysowanie tła okna
        self.mortgage_window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        shadow_rect = pygame.Rect(window_x + 5, window_y + 5, window_width, window_height)
        pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=15)
        pygame.draw.rect(screen, (240, 240, 240), self.mortgage_window_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), self.mortgage_window_rect, 3, border_radius=15)

        # Rysowanie tytułu
        font = pygame.font.Font(None, 36)
        title = font.render("Hipoteka nieruchomości", True, (0, 0, 0))
        screen.blit(title, (window_x + 20, window_y + 20))

        # Przycisk zamknięcia
        close_rect = pygame.Rect(window_x + window_width - 40, window_y + 10, 30, 30)
        pygame.draw.rect(screen, (200, 0, 0), close_rect)
        x_text = font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (close_rect.x + 7, close_rect.y))
        self.mortgage_close_rect = close_rect

        # Lista nieruchomości
        font_small = pygame.font.Font(None, 24)
        y_start = window_y + 70
        list_area = pygame.Rect(window_x + 20, y_start, window_width - 60, window_height - 90)
        pygame.draw.rect(screen, (220, 220, 220), list_area, border_radius=5)
        y = list_area.y + 10 - self.mortgage_scroll_offset
        self.mortgage_buttons = []
        button_height = 40
        button_margin = 10

        # Rysowanie przycisków nieruchomości
        for prop in self.current_player().properties:
            if y + button_height <= list_area.bottom and y >= list_area.top - button_height:
                button_rect = pygame.Rect(list_area.x + 5, y, list_area.width - 10, button_height)
                # Sprawdzamy czy pole ma właściwość color
                color = prop.color if hasattr(prop, 'color') else (200, 200, 200)
                pygame.draw.rect(screen, color, button_rect, border_radius=5)
                pygame.draw.rect(screen, (0, 0, 0), button_rect, 1, border_radius=5)
                brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
                text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)
                status = "Zastawiona" if prop.mortgaged else "Dostępna"
                text = font_small.render(f"{prop.name} - {status} - Wartość: {prop.price}$", True, text_color)
                text_rect = text.get_rect(center=button_rect.center)
                screen.blit(text, text_rect)
                self.mortgage_buttons.append((button_rect, prop))
            y += button_height + button_margin

        # Suwak
        self.mortgage_scroll_rect = pygame.Rect(list_area.right + 5, list_area.y, 20, list_area.height)
        pygame.draw.rect(screen, (180, 180, 180), self.mortgage_scroll_rect, border_radius=5)
        total_height = len(self.current_player().properties) * (button_height + button_margin)
        if total_height > list_area.height:
            scroll_height = int(list_area.height * (list_area.height / total_height))
            scroll_y = list_area.y + int(self.mortgage_scroll_offset * (list_area.height - scroll_height) / (total_height - list_area.height))
            scroll_rect = pygame.Rect(self.mortgage_scroll_rect.x, scroll_y, 20, scroll_height)
            pygame.draw.rect(screen, (100, 100, 100), scroll_rect, border_radius=5)

    def handle_mortgage_click(self, mouse_pos):#obsługuje kliknięcia w oknie hipoteki
        if not hasattr(self, 'mortgage_window_rect'):
            return
            
        if not self.mortgage_window_rect.collidepoint(mouse_pos):
            return

        # Obsługa przycisku zamknięcia
        if hasattr(self, 'mortgage_close_rect') and self.mortgage_close_rect.collidepoint(mouse_pos):
            self.exit_mortgage_mode()
            return

        # Obsługa przycisków nieruchomości
        if hasattr(self, 'mortgage_buttons'):
            for rect, prop in self.mortgage_buttons:
                if rect.collidepoint(mouse_pos):
                    if prop.mortgaged:
                        # Próba odzastawienia nieruchomości
                        if self.current_player().balance >= prop.price * 0.55:
                            prop.mortgaged = False
                            self.current_player().pay(prop.price * 0.55)
                            self.current_player().add_history(f"Odzastawił {prop.name} za {prop.price * 0.55}$")
                            self.current_player().add_history(f"Otrzymał {prop.price * 0.55}$ za odzastawienie {prop.name}")
                        else:
                            set_last_action(f"{self.current_player().name} nie ma wystarczająco pieniędzy na odzastawienie {prop.name}")
                    else:
                        # Zastawienie nieruchomości
                        prop.mortgaged = True
                        self.current_player().receive(prop.price * 0.5)
                        self.current_player().add_history(f"Zastawił {prop.name} za {prop.price * 0.5}$")
                    return

    def exit_mortgage_mode(self):#zamyka tryb hipoteki i aktualizuje stan gry
        self.mortgage_mode = False
        set_last_action(f"{self.current_player().name} zamknął okno hipoteki.")

    def initiate_trade(self, target_player):#rozpoczyna proces handlu z wybranym graczem
        self.trading = {
            "active": True,
            "target": target_player,
            "property": None,
            "price": "",
            "phase": "select_property"
        }
        set_last_action(f"Wybrano gracza {target_player.name} do handlu. Wybierz nieruchomość.")

    def select_trade_property(self, prop):#wybiera nieruchomość do handlu
        self.trading["property"] = prop
        self.trading["phase"] = "input_price"
        set_last_action(f"Wybrano {prop.name}. Wpisz cenę na klawiaturze i zatwierdź ENTER.")

    def update_trade_price(self, key):#aktualizuje cenę w trakcie handlu na podstawie wciśniętego klawisza
        if key == pygame.K_BACKSPACE:
            self.trading["price"] = self.trading["price"][:-1]
        elif key == pygame.K_RETURN:
            if not self.trading["price"].isdigit() or int(self.trading["price"]) <= 0:
                set_last_action("Cena musi być liczbą większą niż 0.")
                return
            self.trading["phase"] = "confirm"
        elif key == pygame.K_ESCAPE:
            self.trading = {"active": False, "target": None, "property": None, "price": "", "phase": ""}
            set_last_action("Anulowano handel.")
        else:
            char = pygame.key.name(key)
            if char.isdigit():
                self.trading["price"] += char

    def cancel_trade(self):#anuluje aktualny handel i resetuje stan handlu
        self.trading = {"active": False, "target": None, "property": None, "price": "", "phase": ""}
        set_last_action("Anulowano handel.")

    def draw_side_panel(self, screen, panel_image):
        # Rysuj tło panelu bocznego
        screen.blit(panel_image, (750, 0))

        # Karty graczy
        card_width, card_height = 300, 120
        card_margin = 20
        start_x = 770
        start_y = 20

        self.player_panel_rects = []
        for i, player in enumerate(self.players):
            # Obliczanie pozycji w siatce 2x2
            row = i // 2  
            col = i % 2   
            
            x = start_x + col * (card_width + card_margin)
            y = start_y + row * (card_height + card_margin)
            
            # Rysowanie karty gracza
            rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(screen, (240, 240, 240), rect, border_radius=10)
            border_color = (0, 200, 0) if i == self.current_player_index else (100, 100, 100)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)
            
            # Informacje o graczu
            font = pygame.font.SysFont('arial', 22, bold=True)
            nick_surf = font.render(player.name, True, (0, 0, 0))
            screen.blit(nick_surf, (x + 10, y + 10))
            
            # Animacja pionka
            current_frame = int(pygame.time.get_ticks() / 240) % len(self.board_animations[player.token_type]['idle'])
            screen.blit(self.board_animations[player.token_type]['idle'][current_frame], (x + card_width - 100, y + 10))
            
            # Szczegóły gracza
            font_small = pygame.font.SysFont('arial', 18)
            field_name = self.board[player.position].name
            pos_surf = font_small.render(f"Pole: {field_name}", True, (0, 0, 0))
            prop_surf = font_small.render(f"Nieruchomości: {len(player.properties)}", True, (0, 0, 0))
            bal_surf = font_small.render(f"Saldo: {player.balance}$", True, (0, 0, 0))
            screen.blit(pos_surf, (x + 10, y + 40))
            screen.blit(prop_surf, (x + 10, y + 60))
            screen.blit(bal_surf, (x + 10, y + 80))

            # Informacja o więzieniu
            if player.in_jail:
                jail_surf = font_small.render(f"W więzieniu: {player.jail_turns}/3", True, (200, 0, 0))
                screen.blit(jail_surf, (x + 10, y + 100))

            self.player_panel_rects.append(rect)

        # Przyciski akcji
        button_width = 200
        button_height = 40
        button_margin = 10
        start_x = 975 
        start_y = 300  
        self.button_rects = []

        # Rzut kostką przycisk
        roll_rect = pygame.Rect(start_x, start_y, button_width, button_height)
        pygame.draw.rect(screen, (200, 200, 200) if self.turn_phase == "waiting_for_roll" else (150, 150, 150), roll_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), roll_rect, 2, border_radius=5)
        font = pygame.font.SysFont('arial', 18)
        text_surf = font.render('Rzuć kostką', True, (0, 0, 0) if self.turn_phase == "waiting_for_roll" else (100, 100, 100))
        text_rect = text_surf.get_rect(center=roll_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('roll', roll_rect))

        # Przyciski Kup i Pomiń
        buy_rect = pygame.Rect(start_x, start_y + button_height + button_margin, button_width - 100, button_height)
        skip_rect = pygame.Rect(start_x - 100 + button_width + 5, start_y + button_height + button_margin, button_width - 100, button_height)
        
        # Sprawdzenie możliwości zakupu
        can_buy = (self.turn_phase == "waiting_for_buy" and 
                  self.last_field and 
                  self.last_field.owner is None and 
                  self.current_player().balance >= self.last_field.price)
        
        pygame.draw.rect(screen, (200, 200, 200) if can_buy else (150, 150, 150), buy_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), buy_rect, 2, border_radius=5)
        text_surf = font.render('Kup', True, (0, 0, 0) if can_buy else (100, 100, 100))
        text_rect = text_surf.get_rect(center=buy_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('buy', buy_rect))

        # Przycisk Pomiń - tylko aktywny gdy gracz może kupić pole
        pygame.draw.rect(screen, (200, 200, 200) if self.turn_phase == "waiting_for_buy" else (150, 150, 150), skip_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), skip_rect, 2, border_radius=5)
        text_surf = font.render('Pomiń', True, (0, 0, 0) if self.turn_phase == "waiting_for_buy" else (100, 100, 100))
        text_rect = text_surf.get_rect(center=skip_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('skip', skip_rect))

        # Domek i Hotel obok siebie
        house_rect = pygame.Rect(start_x, start_y + 2 * (button_height + button_margin), button_width - 100, button_height)
        hotel_rect = pygame.Rect(start_x - 100 + button_width + 5, start_y + 2 * (button_height + button_margin), button_width - 100, button_height)
        
        # Przycisk Domek
        can_build_house = any(self.can_build_house(field) for field in self.current_player().properties)
        pygame.draw.rect(screen, (200, 200, 200) if can_build_house else (150, 150, 150), house_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), house_rect, 2, border_radius=5)
        text_surf = font.render('Domek', True, (0, 0, 0) if can_build_house else (100, 100, 100))
        text_rect = text_surf.get_rect(center=house_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('house', house_rect))

        # Przycisk Hotel
        can_build_hotel = any(self.can_build_hotel(field) for field in self.current_player().properties)
        pygame.draw.rect(screen, (200, 200, 200) if can_build_hotel else (150, 150, 150), hotel_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), hotel_rect, 2, border_radius=5)
        text_surf = font.render('Hotel', True, (0, 0, 0) if can_build_hotel else (100, 100, 100))
        text_rect = text_surf.get_rect(center=hotel_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('hotel', hotel_rect))

        # Hipoteka
        mortgage_rect = pygame.Rect(start_x, start_y + 3 * (button_height + button_margin), button_width, button_height)
        can_mortgage = any(not field.mortgaged for field in self.current_player().properties)
        pygame.draw.rect(screen, (200, 200, 200) if can_mortgage else (150, 150, 150), mortgage_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), mortgage_rect, 2, border_radius=5)
        text_surf = font.render('Hipoteka', True, (0, 0, 0) if can_mortgage else (100, 100, 100))
        text_rect = text_surf.get_rect(center=mortgage_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('mortgage', mortgage_rect))

        # Handluj
        trade_rect = pygame.Rect(start_x, start_y + 4 * (button_height + button_margin), button_width, button_height)
        can_trade = len(self.players) >= 2
        pygame.draw.rect(screen, (200, 200, 200) if can_trade else (150, 150, 150), trade_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), trade_rect, 2, border_radius=5)
        text_surf = font.render('Handluj', True, (0, 0, 0) if can_trade else (100, 100, 100))
        text_rect = text_surf.get_rect(center=trade_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('trade', trade_rect))

        # Koniec tury
        end_turn_rect = pygame.Rect(start_x, start_y + 5 * (button_height + button_margin), button_width, button_height)
        can_end_turn = self.turn_phase != "waiting_for_roll"
        pygame.draw.rect(screen, (200, 200, 200) if can_end_turn else (150, 150, 150), end_turn_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), end_turn_rect, 2, border_radius=5)
        text_surf = font.render('Koniec tury', True, (0, 0, 0) if can_end_turn else (100, 100, 100))
        text_rect = text_surf.get_rect(center=end_turn_rect.center)
        screen.blit(text_surf, text_rect)
        self.button_rects.append(('end_turn', end_turn_rect))

        # Info panel
        info_panel_rect = pygame.Rect(start_x - 100, start_y + 6 * (button_height + button_margin) + 20, 400, 100)
        pygame.draw.rect(screen, (240, 240, 240), info_panel_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), info_panel_rect, 2, border_radius=5)
        
        # Info text
        font = pygame.font.SysFont('arial', 16)
        info_text = get_last_action()
        wrapped_text = textwrap.fill(info_text, width=30)
        lines = wrapped_text.split('\n')
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, (0, 0, 0))
            screen.blit(text_surf, (info_panel_rect.x + 10, info_panel_rect.y + 10 + i * 20))

    def can_build_house(self, field):
        if not field or field.type != "street" or field.owner != self.current_player():
            return False
        if field.hotel or field.houses >= 4:
            return False
        group_fields = [f for f in self.board if f.type == "street" and f.group == field.group]
        if not all(f.owner == self.current_player() for f in group_fields):
            return False
        if self.current_player().balance < field.house_price:
            return False
        return True

    def can_build_hotel(self, field):
        if not field or field.type != "street" or field.owner != self.current_player():
            return False
        if field.hotel or field.houses < 4:
            return False
        group_fields = [f for f in self.board if f.type == "street" and f.group == field.group]
        if not all(f.owner == self.current_player() for f in group_fields):
            return False
        if self.current_player().balance < field.house_price:
            return False
        return True

    def show_mortgage_window(self, screen):
        if self.mortgage_window:
            self.mortgage_window.kill()
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        window_width = min(500, screen_width - 100)
        window_height = min(600, screen_height - 100)
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        


    def draw_trade_window(self, screen):
        window_width, window_height = 600, 400
        window_x = (screen.get_width() - window_width) // 2
        window_y = (screen.get_height() - window_height) // 2
        window_rect = pygame.Rect(window_x, window_y, window_width, window_height)

        # Draw shadow
        shadow_rect = pygame.Rect(window_x + 5, window_y + 5, window_width, window_height)
        pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=15)
        
        # Draw main window
        pygame.draw.rect(screen, (240, 240, 240), window_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), window_rect, 3, border_radius=15)

        font = pygame.font.SysFont('arial', 24, bold=True)
        small_font = pygame.font.SysFont('arial', 18)

        # Title
        screen.blit(font.render("Handel z innym graczem", True, (0, 0, 0)), (window_x + 20, window_y + 20))

        # Player selection
        screen.blit(small_font.render("Wybierz gracza:", True, (0, 0, 0)), (window_x + 20, window_y + 70))
        btn_y = window_y + 100
        self.trade_player_btns = []
        for i, player in enumerate(self.players):
            if i == self.current_player_index:
                continue
            btn_rect = pygame.Rect(window_x + 20, btn_y, 250, 35)
            color = (0, 200, 0) if self.trading.get("target") == player else (200, 200, 200)
            pygame.draw.rect(screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), btn_rect, 2, border_radius=5)
            text = f"{player.name} - Saldo: {player.balance}$"
            screen.blit(small_font.render(text, True, (0, 0, 0)), (btn_rect.x + 10, btn_rect.y + 5))
            self.trade_player_btns.append((btn_rect, player))
            btn_y += 45

        # Property selection z przewijaniem
        screen.blit(small_font.render("Wybierz nieruchomość:", True, (0, 0, 0)), (window_x + 320, window_y + 70))
        properties_area = pygame.Rect(window_x + 320, window_y + 100, 250, 140)
        pygame.draw.rect(screen, (220, 220, 220), properties_area, border_radius=5)
        btn_y = properties_area.y + 10 - self.trade_properties_scroll_offset
        self.trade_property_btns = []
        for prop in self.current_player().properties:
            if btn_y + 35 <= properties_area.bottom and btn_y >= properties_area.top - 35:
                btn_rect = pygame.Rect(properties_area.x + 5, btn_y, properties_area.width - 10, 35)
                field_color = prop.color if hasattr(prop, 'color') else (200, 200, 200)
                pygame.draw.rect(screen, field_color, btn_rect, border_radius=5)
                pygame.draw.rect(screen, (0, 0, 0), btn_rect, 1, border_radius=5)
                if self.trading.get("property") == prop:
                    pygame.draw.rect(screen, (0, 200, 0), btn_rect, 3, border_radius=5)
                brightness = (field_color[0] * 299 + field_color[1] * 587 + field_color[2] * 114) / 1000
                text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)
                text = f"{prop.name} - Wartość: {prop.price}$"
                screen.blit(small_font.render(text, True, text_color), (btn_rect.x + 10, btn_rect.y + 5))
                self.trade_property_btns.append((btn_rect, prop))
            btn_y += 45

        # Suwak
        self.trade_properties_scroll_rect = pygame.Rect(properties_area.right + 5, properties_area.y, 20, properties_area.height)
        pygame.draw.rect(screen, (180, 180, 180), self.trade_properties_scroll_rect, border_radius=5)
        total_height = len(self.current_player().properties) * 45
        if total_height > properties_area.height:
            scroll_height = int(properties_area.height * (properties_area.height / total_height))
            scroll_y = properties_area.y + int(self.trade_properties_scroll_offset * (properties_area.height - scroll_height) / (total_height - properties_area.height))
            scroll_rect = pygame.Rect(self.trade_properties_scroll_rect.x, scroll_y, 20, scroll_height)
            pygame.draw.rect(screen, (100, 100, 100), scroll_rect, border_radius=5)

        # Price input field
        screen.blit(small_font.render("Wpisz cenę:", True, (0, 0, 0)), (window_x + 20, window_y + 250))
        self.trade_price_input_rect = pygame.Rect(window_x + 150, window_y + 250, 200, 30)
        # Draw input field with different color when active
        field_color = (220, 220, 255) if self.trade_price_active else (255, 255, 255)
        pygame.draw.rect(screen, field_color, self.trade_price_input_rect, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), self.trade_price_input_rect, 2, border_radius=5)
        
        # Draw price text
        price_text = self.trading["price"] if self.trading["price"] else "0"
        screen.blit(small_font.render(f"{price_text}$", True, (0, 0, 0)), (self.trade_price_input_rect.x + 10, self.trade_price_input_rect.y + 5))

        # Confirm button
        self.trade_confirm_rect = pygame.Rect(window_x + 320, window_y + 320, 120, 40)
        pygame.draw.rect(screen, (0, 200, 0), self.trade_confirm_rect, border_radius=5)
        screen.blit(font.render("Sprzedaj", True, (255, 255, 255)), (self.trade_confirm_rect.x + 10, self.trade_confirm_rect.y + 5))

        # Cancel button
        self.trade_cancel_rect = pygame.Rect(window_x + 460, window_y + 320, 120, 40)
        pygame.draw.rect(screen, (200, 0, 0), self.trade_cancel_rect, border_radius=5)
        screen.blit(font.render("Anuluj", True, (255, 255, 255)), (self.trade_cancel_rect.x + 10, self.trade_cancel_rect.y + 5))

    def update_animation(self):
        now = pygame.time.get_ticks()
        player = self.current_player()
        if hasattr(player, 'animating') and player.animating and hasattr(player, 'animation_path') and player.animation_path:
            if now - self.animation_timer > 200:
                self.animation_index = (self.animation_index + 1) % 4
                self.animation_timer = now
                
                # Get current and next position
                current_pos = player.position
                next_pos = player.animation_path[0]
                
                # Determine direction based on movement
                if current_pos == 0:  # Starting from START
                    if next_pos <= 10:
                        player.direction = 'west'
                    else:
                        player.direction = 'north'
                elif current_pos <= 10:  # Bottom row
                    if next_pos <= 10:
                        player.direction = 'west'
                    else:
                        player.direction = 'north'
                elif current_pos <= 20:  # Left column
                    if next_pos <= 20:
                        player.direction = 'north'
                    else:
                        player.direction = 'east'
                elif current_pos <= 30:  # Top row
                    if next_pos <= 30:
                        player.direction = 'east'
                    else:
                        player.direction = 'south'
                else:  # Right column
                    if next_pos > current_pos or next_pos <= 10:
                        player.direction = 'south'
                    else:
                        player.direction = 'west'
                
                player.position = next_pos
                player.animation_path.pop(0)
                if not player.animation_path:
                    player.animating = False
                    self.finish_animation()

    def draw(self, screen, board_image, house_image, hotel_image, get_position_coords, dice_images):
        for i, player in enumerate(self.players):
            base_coords = get_position_coords(player.position)
            
            # Calculate diamond pattern offsets
            if i == 0:  # First player - center
                offset_x = -40
                offset_y = -40
            elif i == 1:  # Second player - right
                offset_x = -20
                offset_y = -40
            elif i == 2:  # Third player - bottom
                offset_x = -40
                offset_y = -20
            elif i == 3:  # Fourth player - left
                offset_x = -60
                offset_y = -40
            else:  # Additional players - top
                offset_x = -40
                offset_y = -60

            if hasattr(player, 'animating') and player.animating:
                current_frame = int((pygame.time.get_ticks() - player.animation_start) / 100) % 4
                # Use board animations based on player's token type and direction
                screen.blit(self.board_animations[player.token_type][player.direction][current_frame], 
                           (base_coords[0] + offset_x - 15, base_coords[1] + offset_y - 15))
            else:
                # Use idle animation when not moving
                current_frame = int(pygame.time.get_ticks() / 240) % len(self.board_animations[player.token_type]['idle'])
                screen.blit(self.board_animations[player.token_type]['idle'][current_frame], 
                           (base_coords[0] + offset_x - 15, base_coords[1] + offset_y - 15))

        for field in self.board:
            if field.type == "street":
                coords = get_position_coords(field.position)
                if hasattr(field, 'houses') and field.houses > 0:
                    for i in range(field.houses):
                        screen.blit(house_image, (coords[0] + i * 20, coords[1]))
                if hasattr(field, 'hotel') and field.hotel:
                    screen.blit(hotel_image, (coords[0], coords[1] - 10))

        # Rysuj kostki - animowane lub statyczne
        if self.dice_animation_active:
            self.draw_dice_animation(screen)
        else:
            d1, d2 = self.dice
            screen.blit(dice_images[d1 - 1], (300, 400))
            screen.blit(dice_images[d2 - 1], (400, 400))

    def handle_roll_action(self):
        """Obsługuje akcję rzutu kostkami"""
        if self.turn_phase == "waiting_for_roll":
            self.roll_dice()
            # Nie zmieniamy fazy tutaj - zmiana nastąpi po zakończeniu animacji w update_dice_animation

    def handle_buy_action(self):
        if self.last_field and self.last_field.owner is None:
            self.last_player.buy_property(self.last_field)
            self.house_built_on_current_field = False
            # If player rolled doubles, allow them to roll again
            if self.last_player.consecutive_doubles > 0:
                self.turn_phase = "waiting_for_roll"
                set_last_action(f"{self.last_player.name} kupił {self.last_field.name} i może rzucić ponownie.")
            else:
                self.turn_phase = "waiting_for_end_turn"
                set_last_action(f"{self.last_player.name} kupił {self.last_field.name}.")

    def handle_skip_action(self):
        self.turn_phase = "waiting_for_end_turn"

    def handle_build_house_action(self):
        self.build_house()

    def handle_build_hotel_action(self):
        self.build_hotel()

    def handle_end_turn_action(self):
        if self.turn_phase != "waiting_for_roll":
            self.next_player()
            set_last_action(f"Tura gracza {self.current_player().name}")

    def handle_scroll(self, event):
        if not self.show_player_info_window:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                if self.properties_scroll_rect and self.properties_scroll_rect.collidepoint(event.pos):
                    self.properties_scroll_offset = max(0, self.properties_scroll_offset - 20)
                elif self.history_scroll_rect and self.history_scroll_rect.collidepoint(event.pos):
                    self.history_scroll_offset = max(0, self.history_scroll_offset - 20)
            elif event.button == 5:  # Scroll down
                if self.properties_scroll_rect and self.properties_scroll_rect.collidepoint(event.pos):
                    player = self.players[self.selected_player_info_index]
                    max_scroll = max(0, len(player.properties) * 35 - 200)
                    self.properties_scroll_offset = min(max_scroll, self.properties_scroll_offset + 20)
                elif self.history_scroll_rect and self.history_scroll_rect.collidepoint(event.pos):
                    player = self.players[self.selected_player_info_index]
                    max_scroll = max(0, len(player.history) * 25 - 100)
                    self.history_scroll_offset = min(max_scroll, self.history_scroll_offset + 20)
            elif event.button == 1:  # Left click
                if self.properties_scroll_rect and self.properties_scroll_rect.collidepoint(event.pos):
                    self.properties_scroll_drag = True
                elif self.history_scroll_rect and self.history_scroll_rect.collidepoint(event.pos):
                    self.history_scroll_drag = True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            self.properties_scroll_drag = False
            self.history_scroll_drag = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.properties_scroll_drag:
                player = self.players[self.selected_player_info_index]
                max_scroll = max(0, len(player.properties) * 35 - 200)
                rel_y = event.pos[1] - self.properties_scroll_rect.y
                self.properties_scroll_offset = min(max_scroll, max(0, int(rel_y * max_scroll / self.properties_scroll_rect.height)))
            elif self.history_scroll_drag:
                player = self.players[self.selected_player_info_index]
                max_scroll = max(0, len(player.history) * 25 - 100)
                rel_y = event.pos[1] - self.history_scroll_rect.y
                self.history_scroll_offset = min(max_scroll, max(0, int(rel_y * max_scroll / self.history_scroll_rect.height)))

        if self.mortgage_mode:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    if self.mortgage_scroll_rect and self.mortgage_scroll_rect.collidepoint(event.pos):
                        self.mortgage_scroll_offset = max(0, self.mortgage_scroll_offset - 20)
                elif event.button == 5:  # Scroll down
                    if self.mortgage_scroll_rect and self.mortgage_scroll_rect.collidepoint(event.pos):
                        total_height = len(self.current_player().properties) * 50
                        max_scroll = max(0, total_height - (self.mortgage_window_rect.height - 90))
                        self.mortgage_scroll_offset = min(max_scroll, self.mortgage_scroll_offset + 20)

def main():
    pygame.init()
    display_width, display_height = 1400, 750
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption("Monopoly")
    
    # Załaduj dźwięk kostek
    global dice_sound
    pygame.mixer.init()
    dice_sound = pygame.mixer.Sound("images/dice_sound.wav")
    
    # Załaduj animacje kostek
    dice_animations = [pygame.transform.scale(pygame.image.load(f"images/dice_animations/{i:02d}.png"), (70, 70)) for i in range(1, 33)]
    
    # Load idle animations for menu
    cat_idle_images = [pygame.transform.scale(pygame.image.load(f"images/cat_idle/cat_idle{i}.png"), (100, 100)) for i in range(1, 10)]
    dog_idle_images = [pygame.transform.scale(pygame.image.load(f"images/dog_idle/dog_idle{i}.png"), (100, 100)) for i in range(1, 5)]
    capybara_idle_images = [pygame.transform.scale(pygame.image.load(f"images/capybara_idle/capybara_idle{i}.png"), (100, 100)) for i in range(1, 9)]
    duck_idle_images = [pygame.transform.scale(pygame.image.load(f"images/duck_idle/duck_idle{i}.png"), (100, 100)) for i in range(1, 10)]
    
    # Load walk animations for board movement - adjusted size to match idle
    cat_walk_east_images = [pygame.transform.scale(pygame.image.load(f"images/cat_walk/east/cat_east{i}.png"), (100, 100)) for i in range(1, 5)]
    dog_walk_east_images = [pygame.transform.scale(pygame.image.load(f"images/dog_walk/east/dog_east{i}.png"), (100, 100)) for i in range(1, 5)]
    capybara_walk_east_images = [pygame.transform.scale(pygame.image.load(f"images/capybara_walk/east/capybara_east{i}.png"), (100, 100)) for i in range(1, 5)]
    duck_walk_east_images = [pygame.transform.scale(pygame.image.load(f"images/duck_walk/east/duck_east{i}.png"), (100, 100)) for i in range(1, 5)]
    
    cat_walk_west_images = [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/cat_walk/east/cat_east{i}.png"), (100, 100)), True, False) for i in range(1, 5)]
    dog_walk_west_images = [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/dog_walk/east/dog_east{i}.png"), (100, 100)), True, False) for i in range(1, 5)]
    capybara_walk_west_images = [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/capybara_walk/east/capybara_east{i}.png"), (100, 100)), True, False) for i in range(1, 5)]
    duck_walk_west_images = [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/duck_walk/east/duck_east{i}.png"), (100, 100)), True, False) for i in range(1, 5)]
    
    cat_walk_north_images = [pygame.transform.scale(pygame.image.load(f"images/cat_walk/north/cat_north{i}.png"), (100, 100)) for i in range(1, 5)]
    dog_walk_north_images = [pygame.transform.scale(pygame.image.load(f"images/dog_walk/north/dog_north{i}.png"), (100, 100)) for i in range(1, 5)]
    capybara_walk_north_images = [pygame.transform.scale(pygame.image.load(f"images/capybara_walk/north/capybara_north{i}.png"), (100, 100)) for i in range(1, 5)]
    duck_walk_north_images = [pygame.transform.scale(pygame.image.load(f"images/duck_walk/north/duck_north{i}.png"), (100, 100)) for i in range(1, 5)]
    
    cat_walk_south_images = [pygame.transform.scale(pygame.image.load(f"images/cat_walk/south/cat_south{i}.png"), (100, 100)) for i in range(1, 5)]
    dog_walk_south_images = [pygame.transform.scale(pygame.image.load(f"images/dog_walk/south/dog_south{i}.png"), (100, 100)) for i in range(1, 5)]
    capybara_walk_south_images = [pygame.transform.scale(pygame.image.load(f"images/capybara_walk/south/capybara_south{i}.png"), (100, 100)) for i in range(1, 5)]
    duck_walk_south_images = [pygame.transform.scale(pygame.image.load(f"images/duck_walk/south/duck_south{i}.png"), (100, 100)) for i in range(1, 5)]
    
    # Combine animations for menu and board
    menu_animations = [cat_idle_images, dog_idle_images, capybara_idle_images, duck_idle_images]
    
    # Create directional animations dictionary for each character
    board_animations = {
        0: {  # Cat
            'east': cat_walk_east_images,
            'north': cat_walk_north_images,
            'south': cat_walk_south_images,
            'west': cat_walk_west_images,
            'idle': cat_idle_images
        },
        1: {  # Dog
            'east': dog_walk_east_images,
            'north': dog_walk_north_images,
            'south': dog_walk_south_images,
            'west': dog_walk_west_images,
            'idle': dog_idle_images
        },
        2: {  # Capybara
            'east': capybara_walk_east_images,
            'north': capybara_walk_north_images,
            'south': capybara_walk_south_images,
            'west': capybara_walk_west_images,
            'idle': capybara_idle_images
        },
        3: {  # Duck
            'east': duck_walk_east_images,
            'north': duck_walk_north_images,
            'south': duck_walk_south_images,
            'west': duck_walk_west_images,
            'idle': duck_idle_images
        }
    }
    
    dice_images = [pygame.transform.scale(pygame.image.load(f"images/dice/dice{i}.png"), (70, 70)) for i in range(1, 7)]
    board_image = pygame.image.load("images/MONOPOLOWY.png")
    backgrounds_menu_images = pygame.image.load("images/background.png")
    house_image = pygame.transform.scale(pygame.image.load("images/House.png"), (20, 20))
    hotel_image = pygame.transform.scale(pygame.image.load("images/Hotel.png"), (30, 30))
    panel_image = pygame.transform.scale(pygame.image.load("images/panel_boczny.png"), (1400, 750))
    
    selected_players, selected_tokens, nicknames = show_menu(screen, menu_animations, backgrounds_menu_images)
    
    # Create players with their selected token types
    players = []
    for i in range(selected_players):
        player = Player(nicknames[i])
        player.token_type = selected_tokens[i]  # Store the token type (0=cat, 1=dog, 2=capybara, 3=duck)
        player.direction = 'east'  # Default direction
        players.append(player)
    
    game = GameLogic(players, screen)
    game.board_animations = board_animations  # Add board animations to game instance
    game.dice_animation_frames = dice_animations  # Ustaw klatki animacji kostek
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        time_delta = clock.tick(60)/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            # Obsługa przewijania
            game.handle_scroll(event)
            
            mouse_pos = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Obsługa przycisków
                for button_id, rect in game.button_rects:
                    if rect.collidepoint(mouse_pos):
                        if button_id == 'roll':
                            game.handle_roll_action()
                        elif button_id == 'buy':
                            game.handle_buy_action()
                        elif button_id == 'skip':
                            game.handle_skip_action()
                        elif button_id == 'house':
                            game.handle_build_house_action()
                        elif button_id == 'hotel':
                            game.handle_build_hotel_action()
                        elif button_id == 'mortgage':
                            game.handle_mortgage_action(game.screen)
                        elif button_id == 'trade':
                            game.trading["active"] = True
                        elif button_id == 'end_turn':
                            game.handle_end_turn_action()
                
                # Obsługa kliknięć w karty graczy
                for i, rect in enumerate(game.player_panel_rects):
                    if rect.collidepoint(mouse_pos):
                        game.selected_player_info_index = i
                        game.show_player_info_window = True
                        break
                
                # Obsługa kliknięć w okno informacji o graczu
                if game.show_player_info_window and hasattr(game, 'close_info_rect'):
                    if game.close_info_rect.collidepoint(mouse_pos):
                        game.close_player_info_window()
                
                # Obsługa kliknięć w okno hipoteki
                if game.mortgage_mode:
                    game.handle_mortgage_click(mouse_pos)
                
                if game.trading["active"]:
                    # Handle player selection
                    for btn_rect, player in game.trade_player_btns:
                        if btn_rect.collidepoint(mouse_pos):
                            game.trading["target"] = player
                            set_last_action(f"Wybrano gracza {player.name} do handlu")
                    
                    # Handle property selection
                    for btn_rect, prop in game.trade_property_btns:
                        if btn_rect.collidepoint(mouse_pos):
                            game.trading["property"] = prop
                            set_last_action(f"Wybrano nieruchomość {prop.name} do handlu")
                    
                    # Handle confirm button
                    if game.trade_confirm_rect and game.trade_confirm_rect.collidepoint(mouse_pos):
                        target = game.trading.get("target")
                        prop = game.trading.get("property")
                        price = game.trading["price"]
                        if not target or not prop:
                            set_last_action("Uzupełnij wszystkie pola!")
                        elif not price or int(price) > target.balance:
                            set_last_action("Gracz nie ma tyle pieniędzy!")
                        else:
                            target.balance -= int(price)
                            game.current_player().balance += int(price)
                            prop.owner = target
                            target.properties.append(prop)
                            game.current_player().properties.remove(prop)
                            target.add_history(f"Kupił {prop.name} od {game.current_player().name} za {price}$")
                            game.current_player().add_history(f"Sprzedał {prop.name} do {target.name} za {price}$")
                            set_last_action(f"Transakcja: {target.name} kupił {prop.name} za {price}$")
                            game.trading = {"active": False, "target": None, "property": None, "price": "", "phase": ""}
                    
                    # Handle cancel button
                    if game.trade_cancel_rect and game.trade_cancel_rect.collidepoint(mouse_pos):
                        game.trading = {"active": False, "target": None, "property": None, "price": "", "phase": ""}
                        set_last_action("Anulowano handel")
                    
                    # Handle price input field click
                    if game.trade_price_input_rect and game.trade_price_input_rect.collidepoint(mouse_pos):
                        game.trade_price_active = True
                    else:
                        game.trade_price_active = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.mortgage_mode:
                        game.exit_mortgage_mode()
                    elif game.trading["active"]:
                        game.cancel_trade()
                    else:
                        running = False
                elif game.trading["active"] and game.trade_price_active:
                    if event.key == pygame.K_BACKSPACE:
                        game.trading["price"] = game.trading["price"][:-1]
                    elif event.key == pygame.K_RETURN:
                        game.trade_price_active = False
                    elif event.unicode.isdigit():
                        game.trading["price"] += event.unicode
        
        # Aktualizacja animacji kostek
        game.update_dice_animation()
        
        screen.fill((255, 255, 255))
        screen.blit(board_image, (0, 0))
        
        game.draw_side_panel(screen, panel_image)
        
        game.update_animation()
        game.draw(screen, board_image, house_image, hotel_image, get_position_coords, dice_images)
        
        # Rysuj animację kostek jeśli jest aktywna
        if game.dice_animation_active:
            game.draw_dice_animation(screen)
        
        if game.show_player_info_window:
            game.draw_player_info_window(screen, pygame.font.Font(None, 36))
        
        if game.trading["active"]:
            game.draw_trade_window(screen)
        
        if game.mortgage_mode:
            game.draw_mortgage_window(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()