

#Plik zawierający definicje pól planszy do gry Monopoly.
class BoardField:
    # Mapowanie kolorów grup na wartości RGB
    COLOR_MAP = {
        "brown": (139, 69, 19),
        "lightblue": (135, 206, 235),
        "pink": (255, 192, 203),
        "orange": (255, 165, 0),
        "red": (255, 0, 0),
        "yellow": (255, 255, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255)
    }

    # Ceny domów dla poszczególnych grup kolorów
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

    def __init__(self, position, name, field_type, price=0, group=None):
        self.position = position
        self.name = name
        self.type = field_type
        self.price = price
        self.group = group
        self.owner = None
        self.houses = 0
        self.hotel = False
        self.mortgaged = False
        self.house_price = self.HOUSE_PRICES_BY_GROUP.get(group, 0) if group else 0
        self.color = self.COLOR_MAP.get(group, (255, 255, 255))  # Domyślny kolor biały dla pól bez grupy

    # Słownik zawierający wartości czynszu dla każdej ulicy
    # Indeksy w tablicy odpowiadają liczbie domów (0-4) i hotelowi (5)
    rent_values = {
        "Rio De Janeiro": [2, 10, 30, 90, 160, 250],
        "Sao Paulo": [4, 20, 60, 180, 320, 450],
        "Sewilla": [6, 30, 90, 270, 400, 550],
        "Barcelona": [6, 30, 90, 270, 400, 550],
        "Madryt": [8, 40, 100, 300, 450, 600],
        "Saloniki": [10, 50, 150, 450, 625, 750],
        "Kreta": [10, 50, 150, 450, 625, 750],
        "Ateny": [12, 50, 180, 500, 700, 900],
        "Mediolan": [14, 70, 200, 550, 750, 950],
        "Neapol": [14, 70, 200, 550, 750, 950],
        "Rzym": [16, 80, 220, 600, 800, 1000],
        "Wrocław": [18, 90, 250, 700, 875, 1050],
        "Warszawa": [18, 90, 250, 700, 875, 1050],
        "Kraków": [20, 100, 300, 750, 925, 1100],
        "Osaka": [22, 110, 330, 800, 975, 1150],
        "Negoya": [22, 110, 330, 800, 975, 1150],
        "Tokio": [24, 120, 360, 850, 1025, 1200],
        "Monachium": [26, 130, 390, 900, 1100, 1275],
        "Hamburg": [26, 130, 390, 900, 1100, 1275],
        "Berlin": [28, 150, 450, 1000, 1200, 1400],
        "Brno": [35, 175, 500, 1100, 1300, 1500],
        "Genewa i Zurych": [50, 200, 600, 1200, 1700, 2000],
    }

    def calculate_rent(self, board_fields, dice_sum=None):
        #oblicza czynsz do zapłaty za dane pole
        if self.mortgaged:
            return 0

        if self.type == "street":
            if self.name not in self.rent_values:
                return 0
            rents = self.rent_values[self.name]
            if self.hotel:
                return rents[5]
            return rents[self.houses]
        elif self.type == "station":
            if self.mortgaged:
                return 0
            owner_fields = [f for f in board_fields if f.type == "station" and f.owner == self.owner and not f.mortgaged]
            return 25 * len(owner_fields)
        elif self.type == "utility":
            if self.mortgaged:
                return 0
            if dice_sum is None:
                return 0  # Zabezpieczenie przed brakiem sumy oczek
            owner_fields = [f for f in board_fields if f.type == "utility" and f.owner == self.owner and not f.mortgaged]
            multiplier = 4 if len(owner_fields) == 1 else 10
            return dice_sum * multiplier
        else:
            return 0


def generate_board():
    #generuje plansze
    return [
        BoardField(0, "START", "start", 0),
        BoardField(1, "Rio De Janeiro", "street", 60, "yellow"),
        BoardField(2, "Szansa", "chance"),
        BoardField(3, "Sao Paulo", "street", 60, "yellow"),
        BoardField(4, "Podatek", "tax", 200),
        BoardField(5, "Dworzec Południowy", "station", 200),
        BoardField(6, "Sewilla", "street", 100, "orange"),
        BoardField(7, "Szansa", "chance"),
        BoardField(8, "Barcelona", "street", 100, "orange"),
        BoardField(9, "Madryt", "street", 120, "orange"),
        BoardField(10, "Więzienie", "jail"),
        BoardField(11, "Saloniki", "street", 140, "blue"),
        BoardField(12, "Elektrownia", "utility", 150),
        BoardField(13, "Kreta", "street", 140, "blue"),
        BoardField(14, "Ateny", "street", 160, "blue"),
        BoardField(15, "Dworzec Zachodni", "station", 200),
        BoardField(16, "Mediolan", "street", 180, "green"),
        BoardField(17, "Szansa", "chance"),
        BoardField(18, "Neapol", "street", 180, "green"),
        BoardField(19, "Rzym", "street", 200, "green"),
        BoardField(20, "Parking", "parking"),
        BoardField(21, "Wrocław", "street", 220, "red"),
        BoardField(22, "Szansa", "chance"),
        BoardField(23, "Warszawa", "street", 220, "red"),
        BoardField(24, "Kraków", "street", 240, "red"),
        BoardField(25, "Dworzec Północny", "station", 200),
        BoardField(26, "Osaka", "street", 260, "pink"),
        BoardField(27, "Negoya", "street", 260, "pink"),
        BoardField(28, "Wodociągi", "utility", 150),
        BoardField(29, "Tokio", "street", 280, "pink"),
        BoardField(30, "Idź do więzienia", "gotojail"),
        BoardField(31, "Monachium", "street", 300, "brown"),
        BoardField(32, "Hamburg", "street", 300, "brown"),
        BoardField(33, "Szansa", "chance"),
        BoardField(34, "Berlin", "street", 320, "brown"),
        BoardField(35, "Dworzec Wschodni", "station", 200),
        BoardField(36, "Szansa", "chance"),
        BoardField(37, "Brno", "street", 350, "lightblue"),
        BoardField(38, "Podatek Luksusowy", "tax", 100),
        BoardField(39, "Genewa i Zurych", "street", 400, "lightblue"),
    ]
