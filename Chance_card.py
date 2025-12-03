
#plik z kartami szans
import random
from State import set_last_action

def apply_chance_card(player, players, board_fields):
 #losuje i robi akcje karty szans
    cards = [
        # Karty związane z pieniędzmi
        ("Otrzymujesz 200$", lambda p: (p.receive(200), p.add_history("Otrzymał 200$ z karty Szansa"))),
        ("Otrzymujesz 100$", lambda p: (p.receive(100), p.add_history("Otrzymał 100$ z karty Szansa"))),
        ("Otrzymujesz 50$", lambda p: (p.receive(50), p.add_history("Otrzymał 50$ z karty Szansa"))),
        ("Otrzymujesz 150$", lambda p: (p.receive(150), p.add_history("Otrzymał 150$ z karty Szansa"))),
        ("Otrzymujesz 300$", lambda p: (p.receive(300), p.add_history("Otrzymał 300$ z karty Szansa"))),
        ("Płacisz 100$", lambda p: (p.pay(100), p.add_history("Zapłacił 100$ z karty Szansa"))),
        ("Płacisz 150$", lambda p: (p.pay(150), p.add_history("Zapłacił 150$ z karty Szansa"))),
        ("Płacisz 200$", lambda p: (p.pay(200), p.add_history("Zapłacił 200$ z karty Szansa"))),
        ("Płacisz 50$", lambda p: (p.pay(50), p.add_history("Zapłacił 50$ z karty Szansa"))),
        ("Płacisz 75$", lambda p: (p.pay(75), p.add_history("Zapłacił 75$ z karty Szansa"))),
        
        # Karty związane z więzieniem
        ("Trafiasz do więzienia", lambda p: (p.send_to_jail(), p.add_history("Trafił do więzienia z karty Szansa"))),
        ("Trafiasz do więzienia", lambda p: (p.send_to_jail(), p.add_history("Trafił do więzienia z karty Szansa"))),
        ("Trafiasz do więzienia", lambda p: (p.send_to_jail(), p.add_history("Trafił do więzienia z karty Szansa"))),
        
        # Karty związane z nieruchomościami
        ("Remont nieruchomości: płać 40$ za domek", 
         lambda p: (p.pay(len([f for f in p.properties if f.houses]) * 40), 
                   p.add_history(f"Zapłacił {len([f for f in p.properties if f.houses]) * 40}$ za remont nieruchomości z karty Szansa"))),
        ("Remont nieruchomości: płać 25$ za domek", 
         lambda p: (p.pay(len([f for f in p.properties if f.houses]) * 25), 
                   p.add_history(f"Zapłacił {len([f for f in p.properties if f.houses]) * 25}$ za remont nieruchomości z karty Szansa"))),
        ("Sprzedaj wszystkie domy za połowę ceny", 
         lambda p: ([p.receive(f.house_price * f.houses // 2) for f in p.properties if f.houses > 0], 
                   p.add_history("Sprzedał wszystkie domy za połowę ceny z karty Szansa"))),
        
        # Karty związane z podatkami i opłatami
        ("Zapłata za leczenie 100$", lambda p: (p.pay(100), p.add_history("Zapłacił 100$ za leczenie z karty Szansa"))),
        ("Zapłata za leczenie 150$", lambda p: (p.pay(150), p.add_history("Zapłacił 150$ za leczenie z karty Szansa"))),
        ("Otrzymujesz zwrot podatku 150$", lambda p: (p.receive(150), p.add_history("Otrzymał 150$ zwrotu podatku z karty Szansa"))),
        ("Otrzymujesz zwrot podatku 200$", lambda p: (p.receive(200), p.add_history("Otrzymał 200$ zwrotu podatku z karty Szansa"))),
        ("Płacisz podatek 200$", lambda p: (p.pay(200), p.add_history("Zapłacił 200$ podatku z karty Szansa"))),
        ("Płacisz podatek 150$", lambda p: (p.pay(150), p.add_history("Zapłacił 150$ podatku z karty Szansa"))),
        
        # Karty związane z bankiem
        ("Bank płaci Ci dywidendę 50$", lambda p: (p.receive(50), p.add_history("Otrzymał 50$ dywidendy z banku z karty Szansa"))),
        ("Bank płaci Ci dywidendę 100$", lambda p: (p.receive(100), p.add_history("Otrzymał 100$ dywidendy z banku z karty Szansa"))),
        ("Bank płaci Ci dywidendę 150$", lambda p: (p.receive(150), p.add_history("Otrzymał 150$ dywidendy z banku z karty Szansa"))),
        ("Bank pobiera od Ciebie 100$", lambda p: (p.pay(100), p.add_history("Zapłacił 100$ do banku z karty Szansa"))),
        ("Bank pobiera od Ciebie 150$", lambda p: (p.pay(150), p.add_history("Zapłacił 150$ do banku z karty Szansa"))),
        
        # Karty związane z innymi graczami
        ("Zostałeś przewodniczącym: płać 50$ każdemu graczowi",
         lambda p: all(p.pay(50) and other.receive(50) and other.add_history(f"Otrzymał 50$ od {p.name} z karty Szansa")
                      for other in players if other != p)),
        ("Każdy gracz płaci Ci 50$",
         lambda p: ([other.pay(50) and p.receive(50) for other in players if other != p], 
                   p.add_history("Otrzymał 50$ od każdego gracza z karty Szansa"))),
        ("Każdy gracz płaci Ci 100$",
         lambda p: ([other.pay(100) and p.receive(100) for other in players if other != p], 
                   p.add_history("Otrzymał 100$ od każdego gracza z karty Szansa"))),
        ("Płacisz 100$ każdemu graczowi",
         lambda p: ([p.pay(100) and other.receive(100) for other in players if other != p], 
                   p.add_history("Zapłacił 100$ każdemu graczowi z karty Szansa"))),
        
        # Karty związane z podatkami
        ("Płacisz podatek: 15$ za każdy domek i 40$ za każdy hotel",
         lambda p: (p.pay(sum(f.houses * 15 + (40 if f.hotel else 0) for f in p.properties)),
                   p.add_history(f"Zapłacił podatek z karty Szansa"))),
        
        # Karty związane z bankiem
        ("Otrzymujesz dywidendę: 50$", lambda p: (p.receive(50), p.add_history("Otrzymał 50$ dywidendy z karty Szansa"))),
        ("Płacisz bankowi: 100$", lambda p: (p.pay(100), p.add_history("Zapłacił 100$ bankowi z karty Szansa"))),
        
        # Karty związane z nieruchomościami
        ("Sprzedajesz domy: otrzymujesz 25$ za każdy domek i 100$ za każdy hotel",
         lambda p: (p.receive(sum(f.houses * 25 + (100 if f.hotel else 0) for f in p.properties)),
                   p.add_history(f"Otrzymał pieniądze za sprzedaż domów z karty Szansa"))),
        
        # Karty związane z innymi graczami
        ("Płacisz każdemu graczowi 10$",
         lambda p: all(p.pay(10) and other.receive(10) and other.add_history(f"Otrzymał 10$ od {p.name} z karty Szansa")
                      for other in players if other != p)),
        
        # Karty związane z pieniędzmi
        ("Otrzymujesz zwrot podatku: 20$", lambda p: (p.receive(20), p.add_history("Otrzymał 20$ zwrotu podatku z karty Szansa"))),
        ("Płacisz za ubezpieczenie: 50$", lambda p: (p.pay(50), p.add_history("Zapłacił 50$ za ubezpieczenie z karty Szansa")))
    ]
    
    # Losujemy kartę
    card_text, card_action = random.choice(cards)
    
    # Wykonujemy akcję karty
    card_action(player)
    
    return card_text
