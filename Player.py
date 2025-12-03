import random


#Plik ktory reprezentuje gracza i metody ziwazane z akcjami gracza

class Player:
    # Ceny domów dla różnych grup kolorów
    HOUSE_PRICES_BY_GROUP = {
        "brown": 50,
        "lightblue": 50,
        "pink": 100,
        "orange": 100,
        "red": 150,
        "yellow": 150,
        "green": 200,
        "blue": 200
    }

    def __init__(self, name):
        # Podstawowe właściwości gracza
        self.name = name
        self.balance = 1500
        self.position = 0
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.consecutive_doubles = 0
        self.history = []
        
        # Właściwości związane z animacją
        self.token_type = 0
        self.direction = 'east'
        self.animating = False
        self.animation_path = []
        self.animation_start = 0

    def roll_dice(self):
        #symulacja rzutu kostka
        return random.randint(1, 6), random.randint(1, 6)

    def add_history(self, text):
        #dodaje wpis do histori
        self.history.append(text)

    def move(self, steps):
        #przesuwa gracza o okreslona liczbe pol
        self.position = (self.position + steps) % 40

    def buy_property(self, field):
        #funkcja kupowania nieruchomosci jak ma kase
        if self.balance >= field.price:
            self.balance -= field.price
            field.owner = self
            self.properties.append(field)
            self.add_history(f"Kupił {field.name} za {field.price}$")
            return True
        return False

    def can_build_house(self, field):
        #sprawdza czy gracz moze kupic dom
        if not field or field.type != "street" or field.owner != self:
            return False
        if field.hotel or field.houses >= 4:
            return False
        if self.balance < field.house_price:
            return False
            
        # sprawdza czy gracz ma wszystkie pola danego koloru
        group_fields = [f for f in self.properties if f.type == "street" and f.group == field.group]
        all_group_fields = [f for f in self.properties if f.type == "street" and f.group == field.group]
        if len(group_fields) != len(all_group_fields):
            return False
        if not all(f.houses >= field.houses for f in group_fields):
            return False
        return True

    def build_house(self, field):
        #buduje dom
        if not self.can_build_house(field):
            return False
        if self.balance >= field.house_price:
            self.balance -= field.house_price
            field.houses += 1
            self.add_history(f"Zbudował domek na {field.name} za {field.house_price}$")
            return True
        return False

    def can_build_hotel(self, field):
        #sprawdza czy moze kupic hotel
        if not field or field.type != "street" or field.owner != self:
            return False
        if field.hotel or field.houses < 4:
            return False
        if self.balance < field.house_price:
            return False
            
        # sprawdza czy ma wszystkie nieruchomosci z danego koloru
        group_fields = [f for f in self.properties if f.type == "street" and f.group == field.group]
        all_group_fields = [f for f in self.properties if f.type == "street" and f.group == field.group]
        if len(group_fields) != len(all_group_fields):
            return False
            
        # Sprawdza czy wszystkie pola mają po 4 domy
        if not all(f.houses == 4 for f in group_fields):
            return False
        return True

    def build_hotel(self, field):
        #buduje hotel
        if not self.can_build_hotel(field):
            return False
        if self.balance >= field.house_price:
            self.balance -= field.house_price
            field.houses = 0
            field.hotel = True
            self.add_history(f"Zbudował hotel na {field.name} za {field.house_price}$")
            return True
        return False

    def pay(self, amount):
        #funkcja ktora jest po to bgy placicl okreslona kwote
        if self.balance >= amount:
            self.balance -= amount
            self.add_history(f"Zapłacił {amount}$")
            return True
        return False

    def receive(self, amount):
        #otrzymuje okreslona kwote
        self.balance += amount
        self.add_history(f"Otrzymał {amount}$")

    def send_to_jail(self):
        #funkcja od weizienia
        self.in_jail = True
        self.jail_turns = 0
        self.position = 10
        self.add_history("Trafił do więzienia")

    def __str__(self):
        #zwaraca reprezentacje tekstowa gracza
        return f"{self.name} (${self.balance})"

    def try_exit_jail(self, dice1, dice2):
        #funkcja od wiezienia
        if dice1 == dice2:
            self.in_jail = False
            self.jail_turns = 0
            self.add_history("Wyszedł z więzienia wyrzucając dublet")
            return True
        self.jail_turns += 1
        return False

    def mortgage_property(self, field):
        #hipoteka nieruchomosci
        if not field.mortgaged and field.owner == self:
            mortgage_value = field.price // 2
            self.receive(mortgage_value)
            field.mortgaged = True
            self.add_history(f"Zastawił {field.name} za {mortgage_value}$")
            return True
        return False

    def lift_mortgage(self, field):
        #odzyskuje nieruchomosc
        if field.mortgaged and field.owner == self:
            lift_cost = int(field.price)
            if self.balance >= lift_cost:
                self.pay(lift_cost)
                field.mortgaged = False
                self.add_history(f"Odzastawił {field.name} za {lift_cost}$")
                return True
        return False

    def sell_house(self, field):
        #sprzedaz domu
        if field.houses > 0 and field.owner == self:
            sell_value = field.house_price // 2
            self.receive(sell_value)
            field.houses -= 1
            self.add_history(f"Sprzedał domek na {field.name} za {sell_value}$")
            return True
        return False

    def sell_hotel(self, field):
        #sprzedaz nieruchomosci
        if field.hotel and field.owner == self:
            sell_value = field.house_price // 2
            self.receive(sell_value)
            field.hotel = False
            field.houses = 4
            self.add_history(f"Sprzedał hotel na {field.name} za {sell_value}$")
            return True
        return False

    def sell_buildings_for_money(self, amount_needed):
        total_raised = 0
        
        # Najpierw spróbuj sprzedać hotele
        for prop in self.properties:
            if prop.type == "street" and prop.hotel:
                if self.sell_hotel(prop):
                    total_raised += prop.house_price // 2
                    if self.balance >= amount_needed:
                        return True
        
        #  spróbuj sprzedać domy
        while total_raised < amount_needed:
            sold_any = False
            for prop in self.properties:
                if prop.type == "street" and prop.houses > 0:
                    if self.sell_house(prop):
                        total_raised += prop.house_price // 2
                        sold_any = True
                        if self.balance >= amount_needed:
                            return True
            if not sold_any:
                break
        
        return self.balance >= amount_needed

    def can_pay(self, amount):
        #sprawdza czy gracz moze zaplacic
        return self.balance >= amount

    def get_total_assets(self):
        #oblicza calkowity majatek gracza
        total = self.balance
        # Dodaj wartość nieruchomości
        for prop in self.properties:
            if not prop.mortgaged:
                total += prop.price
                # Dodaj wartość domów i hoteli
                if prop.type == "street":
                    if prop.hotel:
                        total += prop.house_price
                    else:
                        total += prop.houses * prop.house_price
        return total

    def declare_bankruptcy(self, creditor=None):
        #deklaracja bankructwa
        for prop in self.properties:
            if creditor:
                prop.owner = creditor
                creditor.properties.append(prop)
                creditor.add_history(f"Otrzymał {prop.name} od bankruta {self.name}")
            else:
                # Przekaż nieruchomość do banku
                prop.owner = None
                prop.houses = 0
                prop.hotel = False
                prop.mortgaged = False
        self.properties = []
        self.balance = 0
        self.add_history("Zbankrutował")

    def try_pay_or_mortgage(self, amount, creditor=None):
        #jak nie ma wystarczajaco kasy to musi w hipoteke lub w sprzedaz
        if self.can_pay(amount):
            return self.pay(amount)

        # Spróbuj sprzedać domy i hotele
        if self.sell_buildings_for_money(amount):
            return self.pay(amount)

        # Spróbuj zastawić nieruchomości
        for prop in self.properties:
            if not prop.mortgaged:
                if self.mortgage_property(prop):
                    if self.can_pay(amount):
                        return self.pay(amount)

        #jesli dalej nie ma wystarczajaco kasy to bankrut
        self.declare_bankruptcy(creditor)
        return False
