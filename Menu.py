#plik menu

import pygame
import sys

def show_menu(screen, token_animations, background_image):
    #wyswitla menu poczatakowe gry i obsluge wyboru graczy

    # Inicjalizacja czcionki i zmiennych
    font = pygame.font.Font(None, 36)
    selected_players = 2
    player_tokens = [None] * 4
    selected_token_types = [None] * 4
    chosen_tokens = []
    current_player = 0
    selecting_tokens = False
    entering_names = False
    nickname_input = ""
    nicknames = []

    # Zmienne do animacji
    animation_index = 0
    animation_timer = 0

    while True:
        # Aktualizacja animacji
        dt = pygame.time.get_ticks()
        if dt - animation_timer > 200:
            animation_index = (animation_index + 1) % 4
            animation_timer = dt

        # Rysowanie tła
        scaled_background = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(scaled_background, (0, 0))

        if entering_names:
            # Ekran wpisywania nicków
            input_box = pygame.Rect(500, 400, 400, 50)
            pygame.draw.rect(screen, (255, 255, 255), input_box)
            pygame.draw.rect(screen, (0, 0, 0), input_box, 2)

            prompt = font.render(f"Gracz {current_player+1}, wpisz swój nick:", True, (0,0,0))
            screen.blit(prompt, prompt.get_rect(center=(screen.get_width()//2, 350)))

            nickname_surface = font.render(nickname_input, True, (0,0,0))
            screen.blit(nickname_surface, nickname_surface.get_rect(center=input_box.center))
            pygame.display.flip()

            # Obsługa zdarzeń podczas wpisywania nicku
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if nickname_input.strip() == "":
                            nickname_input = f"Gracz {current_player+1}"
                        nicknames.append(nickname_input.strip())
                        current_player += 1
                        nickname_input = ""
                        if current_player == selected_players:
                            selecting_tokens = True
                            entering_names = False
                            current_player = 0
                    elif event.key == pygame.K_BACKSPACE:
                        nickname_input = nickname_input[:-1]
                    else:
                        nickname_input += event.unicode
            continue

        elif not selecting_tokens:
            # Ekran wyboru liczby graczy
            number_of_players_rect = pygame.Rect(500, 300, 400, 50)
            pygame.draw.rect(screen, (191, 223, 223), number_of_players_rect)
            text = font.render(f"Liczba graczy: {selected_players}", True, (0,0,0))
            screen.blit(text, text.get_rect(center=number_of_players_rect.center))

            start_button_rect = pygame.Rect(500, 400, 400, 50)
            pygame.draw.rect(screen, (191, 223, 223), start_button_rect)
            start_text = font.render("Rozpocznij grę", True, (0,0,0))
            screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))

            # Obsługa zdarzeń podczas wyboru liczby graczy
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if number_of_players_rect.collidepoint(event.pos):
                        selected_players = (selected_players % 4) + 1
                    elif start_button_rect.collidepoint(event.pos):
                        entering_names = True
                        current_player = 0

        else:
            # Ekran wyboru pionków
            instruction_text = f"{nicknames[current_player]} wybierz pionek:"
            instruction = font.render(instruction_text, True, (0, 0, 0))
            instruction_rect = instruction.get_rect(center=(screen.get_width() // 2, 300))

            # Rysowanie tła dla instrukcji
            padding = 20
            background_rect = pygame.Rect(
                instruction_rect.left - padding // 2,
                instruction_rect.top - padding // 2,
                instruction_rect.width + padding,
                instruction_rect.height + padding
            )
            pygame.draw.rect(screen, (191, 223, 223), background_rect)
            screen.blit(instruction, instruction_rect)

            # Rysowanie dostępnych pionków
            token_rects = []
            for i, anim in enumerate(token_animations):
                frame = anim[animation_index]
                preview = pygame.transform.scale(frame, (100, 100))
                x = 250 + i * 250
                y = 350
                rect = preview.get_rect(topleft=(x, y))
                token_rects.append(rect)

                pygame.draw.rect(screen, (191, 223, 223), rect.inflate(10, 10))
                screen.blit(preview, rect)

                # Zaznaczanie już wybranych pionków
                if i in chosen_tokens:
                    pygame.draw.rect(screen, (100, 100, 100), rect, 5)

            # Obsługa zdarzeń podczas wyboru pionka
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(token_rects):
                        if rect.collidepoint(event.pos) and i not in chosen_tokens:
                            player_tokens[current_player] = token_animations[i]
                            selected_token_types[current_player] = i
                            chosen_tokens.append(i)
                            current_player += 1
                            if current_player == selected_players:
                                return selected_players, selected_token_types[:selected_players], nicknames

        pygame.display.flip()
