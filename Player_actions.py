
#Plik zawierający definicje akcji gracza w grze Monopoly.
from State import set_last_action, get_last_action
from Chance_card import apply_chance_card  # Import funkcji obsługującej karty szansy

def handle_field_action(player, players, board_fields):
    #Obsługuje akcje związane z polem, na którym stanął gracz.

    field = board_fields[player.position]
    base_info = f"{player.name} stanął na polu: {field.name} ({field.type})"

    if field.type in ["street", "station", "utility"]:
        # Obsługa pól nieruchomości 
        if field.owner is None:
            # Pole jest wolne - gracz może je kupić
            set_last_action(base_info + f"\nMoże kupić to pole za {field.price}$")
        elif field.owner != player:
            # Gracz musi zapłacić czynsz
            rent = field.calculate_rent(board_fields)
            set_last_action(base_info + f"\nGracz musi zapłacić {rent}$ czynszu właścicielowi {field.owner.name}")
    elif field.type == "tax":
        # Gracz płaci podatek
        set_last_action(base_info + f"\nGracz musi zapłacić podatek {field.price}$")
        player.pay(field.price)
    elif field.type == "chance":
        # Gracz losuje kartę szansy
        text = apply_chance_card(player, players, board_fields)
        set_last_action(base_info + f"\nKarta Szansa: {text}")
    elif field.type == "gotojail":
        # Gracz idzie do więzienia
        player.send_to_jail()
        set_last_action(base_info + f"\nGracz idzie do więzienia!")
    elif field.type == "start":
        # Gracz przechodzi przez START
        player.receive(200)
        set_last_action(base_info + f"\nGracz otrzymuje 200$ za START")
    else:
        # Inne pola (parking, więzienie)
        set_last_action(base_info)
