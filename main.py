from random import randint

class Dot: 
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

def __eq__(self, other) -> None: 
    return self.x == other.x and self.y == other.y

def __repr__(self) -> None: 
    return f"Dot({self.x}, {self.y})"


"""Catching Board Exceptions"""

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


"""Main ship's class with directions(1, 0)"""


class Ship:
    def __init__(self, bow, l, o) -> None:
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self) -> None:
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y
            
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots

    def shooten(self, shot) -> None:
        return shot in self.dots


"""Main board's class"""
class Board:
    def __init__(self, hid = False, size = 6) -> None:
        self.size = size
        self.hid = hid
        
        self.count = 0 # Количество пораженных кораблей
        
        self.field = [ ["O"]*size for _ in range(size) ] # Состояние клеток на поле
        
        self.busy = [] # Показывает занятые точки
        self.ships = [] # Список кораблей на доске


    def __str__(self) -> None: # Вырисовываем игровое поле
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid: 
            res=res.replace("■", "0")
        return res


    def out(self, d) -> None: # Проверка точки на нахождение в пределах доски
        return not((0<= d.x < self.size) and (0<= d.y < self.size))
    

    def contour(self, ship, verb = False) -> None:
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship) -> None: # Проверка на границы и занятость точек на игровом поле(кораблем)
        
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d) -> None: # Код хода(выстрела) на игровом поле
        
        if self.out(d): 
            raise BoardOutException()
        
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships: # Проверка хода
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0: 
                    self.count += 1 # Счетчик уничтоженных кораблей
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    
    def begin(self) -> None:
        self.busy = []

    def defeat(self) -> None:
        return self.count == len(self.ships)


"""Player's class"""

class Player:
    def __init__(self, board, enemy) -> None:
        self.board = board
        self.enemy = enemy
    
    def ask(self) -> None: 
        raise NotImplementedError()
    
    def move(self) -> None: # В бесконечном цикле пытаемся сделать игровой ход(выстрел)
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


"""AI class for playing with computer"""
class AI(Player):
    def ask(self) -> None:
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


"""User's class"""
class User(Player):
    def ask(self) -> None:
        while True:
            cords = input("Ваш ход: ").split()
            
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

"""Game's class"""
class Game:
    def __init__(self, size = 6) -> None:
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self) -> None: # Гарантированное создание игрового поля
        board = None
        while board is None:
            board = self.try_board()
        return board
    
    def try_board(self) -> None: # Пытаемся поставить корабль в бесконечном цикле
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0 # Начальное количество попыток создать доску
        for l in lens:
            while True:
                attempts += 1 
                if attempts > 2000: # Закрытие бесконечного числа попыток создать доску
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    
    
    

    def greet(self) -> None:
        print("-------------------")
        print("  Приветствуем вас ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self) -> None:
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
                
            if repeat:
                num -= 1
            
            if self.ai.board.defeat():
                print("-"*20)
                print("Пользователь выиграл!")
                break
            
            if self.us.board.defeat():
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self) -> None:
        self.greet()
        self.loop()
            
            
g = Game()
g.start()
