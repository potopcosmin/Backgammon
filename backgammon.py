import pygame as pg
import random
import time
import copy
pg.init()
board = pg.image.load("img/board.png")
board = pg.transform.scale(board, (600, 600))
bkg=pg.image.load("img/bkg.jpg")
bkg=pg.transform.scale(bkg,(700,700))
screen = pg.display.set_mode((700, 700))
running = True
exitimage=pg.image.load("img/exitgame.png")
exitgame=pg.transform.scale(exitimage,(50,50))
exitRect=pg.Rect(650,650,50,50)
class Button:
    """
    Butonul pentru aruncarea zarurilor.
    """
    def __init__(self, text,  pos, font, bg="black"):
        self.x, self.y = pos
        self.font = pg.font.SysFont("Arial", font)
        self.change_text(text, bg)
    
    def change_text(self, text, bg="black"):
        """
        Schimba textul afisat pe buton
        """

        self.text = self.font.render(text, 1, pg.Color("White"))
        self.size = self.text.get_size()
        self.surface = pg.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pg.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self):
        """
        Randeaza butonul
        """
        screen.blit(self.surface, (self.x, self.y))


class Column:
    """
    Elementele unei coloane in care se afla piesele.Atributul number
    reprezinta numerul coloanei in functie de numerotarea de pe tabla.
    Atributul count reprezinta numarul de piese de pe acea coloana.
    Atributul type reprezinta tipul piesei aflat pe coloana white,black,None.
    Atributele , piecexstart si pieceystart ,reprezinta coordonatele de unde se incepe randarea pieselor
    Atributul pgrect ,reprezinta varaibila de tip Rect folosita pentru randare
    """
    def __init__(self, numberr:int, noofpieces:int, color=None:str, middle=None:bool)->Column:
        """
        :param: numberr:Numarul coloanei
        :param: nofopieces:Numarul de piese de pe acea coloana
        :param:colo: white/black
        :param middle: True,daca coloana este rezervata pentru Hitted Pieces
        False altfel
        :returns : an Column object
        """
        self.type = color
        self.number = numberr
        self.count = noofpieces
        if self.number <= 6:
            if self.number == 1:
                self.piecexstart = 600-35*numberr
            else:
                self.piecexstart = 565-43*(numberr-1)
        elif self.number <= 12:
            self.piecexstart = 285-44*(numberr-7)
        elif self.number < 19:
            self.piecexstart = 35+43*(numberr-13)
        elif self.number <= 24:
            self.piecexstart = 35+43*(numberr-13)+25

        if middle is not None and color == "black":
            self.piecexstart = 285
            self.pieceystart = 35
        if middle is not None and color == "white":
            self.piecexstart = 285+35
            self.pieceystart = 600-35

        if self.number <= 12:
            self.pieceystart = 600-31
        else:
            self.pieceystart = 31

        if self.number <= 12:
            self.pgrect = pg.Rect(self.piecexstart-35, 320, 35, 250)
        else:
            self.pgrect = pg.Rect(self.piecexstart, 35, 35, 250)

    def show(self):
        
        """
        Randeaza elementele coloanei
        """
        if self.type == "white":
            img = pg.image.load("img/whitepiece.png")
        elif self.type == "black":
            img = pg.image.load("img/blackpiece.png")
        for i in range(1, self.count+1):
            if self.number <= 12:
                screen.blit(img, (self.piecexstart-32, self.pieceystart-32*i))

            if self.number > 12:
                screen.blit(img, (self.piecexstart, self.pieceystart+32*(i-1)))

    def add(self, color=None:str):
        """
        Adauga piese la coloana,Daca color este none atunci
         se mentine tipul piesei din acea coloana

        :params:color None ,White or Black
        """
        self.count += 1

        if color != None:
            self.type = color
            self.count = 1

    def remove(self):
        """
        Elimina piesa din coloana
        :params:
        :returns: Nothing
        """
        self.count -= 1

    def setTypeNone(self):
        """
        Seteaza tipul coloanei la None 
        """
        self.type = None

    def checkavailabletomove(self, dice1:int)->int:
        """
        Verifica daca se poate executa mutarea folosind zrul dice1 ,plecand de la self
        :param dice1:numarul de pe zar
        :returns: int
        Returneaza 0, daca este imposibil,int >0 daca este posibil(destinatia)
        """
        available = 0
        if (self.type == "white"):
            if (AllColumns.get(self.number+dice1)):
                if (AllColumns.get(self.number+dice1).type == "white" or AllColumns.get(self.number+dice1).type == None or (AllColumns.get(self.number+dice1).type == "black" and AllColumns.get(self.number+dice1).count == 1)):
                    available = self.number+dice1

        if (self.type == "black"):
            if (AllColumns.get(self.number-dice1)):
                if (AllColumns.get(self.number-dice1).type == "black" or AllColumns.get(self.number-dice1).type == None or (AllColumns.get(self.number-dice1).type == "white" and AllColumns.get(self.number-dice1).count == 1)):
                    available = self.number-dice1

        return available


def checktobear(type:str)->bool:
    """
    Verifica daca se poate incepe procedura de la finalul jocului de a scoate piese
    :param type : tipul piesei
    :returns : True daca jucatorul a scos deja o piesa , sau poate scoate,
    False in caz contrar
    """
    if (type == "black"):
        sum = 0
        for i in range(1, 7):
            if AllColumns[i].type == "black":
                sum += AllColumns[i].count
        if (sum != 15):
            return False
        return True
    if (type == "white"):
        sum = 0
        for i in range(19, 25):
            if AllColumns[i].type == "white":
                sum += AllColumns[i].count
        if (sum != 15):
            return False
        return True


def checkifanyavailable(dice:int, turn:str)->bool:
    """
    Verirfica daca exista macar o mutare posibila in tot jocul
    :param dice:numarul zarului
    :param turn:white sau black ,player pentru care se verifica
    :returns : True daca exista o mutare posibila folosind zarul dice pentru turn,False in caz contrar
    """
    for i in AllColumns.values():
        if i.type == turn:
            if i.checkavailabletomove(dice) != 0:
                return True
    return False


def checkfinish()->bool:
    """
    :returns :True ,daca jocul s-a terminat
    
    False in caz contrar
    """
    sumWhite = 0
    sumBlack = 0
    for i in AllColumns.values():
        if i.type == "white":
            sumWhite += i.count
        else:
            sumBlack += i.count
    if (sumWhite == 0 or sumBlack == 0):
        return True
    return False


pieceOutsideHome = False


button1 = Button(
    "Roll",
    (650, 300),
    font=30,
    bg="navy",
)
initgood = {
    1: Column(1, 2, "white"),
    2: Column(2, 0),
    3: Column(3, 0),
    4: Column(4, 0),
    5: Column(5, 0),
    6: Column(6, 5, "black"),
    7: Column(7, 0),
    8: Column(8, 3, "black"),
    9: Column(9, 0),
    10: Column(10, 0),
    11: Column(11, 0),
    12: Column(12, 5, "white"),
    13: Column(13, 5, "black"),
    14: Column(14, 0),
    15: Column(15, 0),
    16: Column(16, 0),
    17: Column(17, 3, "white"),
    18: Column(18, 0),
    19: Column(19, 5, "white"),
    20: Column(20, 0),
    21: Column(21, 0),
    22: Column(22, 0),
    23: Column(23, 0),
    24: Column(24, 2, "black"),
}
hittedWhite = Column(3, 0, "white", True)
hittedBlack = Column(23, 0, "black", True)

AllColumns = copy.deepcopy(initgood)
moving = False
toroll = True
dice1 = pg.image.load("img/load.png")
dice1 = pg.transform.scale(dice1, (40, 40))
dice2 = pg.image.load("img/load.png")
dice2 = pg.transform.scale(dice1, (40, 40))

pieceremoved = True
fromcolumn = None
diceroll = []
doubledice = False
turn = "white"
tobearWhite = False
tobearBlack = False
pvp = False
pvc = False
menu = True


while (running):
    if (menu == True):
        PvCrect = pg.Rect((190, 220), (350, 45))
        PvPrect = pg.Rect((190, 300), (350, 45))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                print(x, y)
                if PvCrect.collidepoint(x, y) == True:
                    
                    """
                    Reinitializare game
                    """
                    menu = False
                    pvc = True
                    hittedWhite = Column(3, 0, "white", True)
                    hittedBlack = Column(23, 0, "black", True)

                    AllColumns = copy.deepcopy(initgood)
                    moving = False
                    toroll = True
                    dice1 = pg.image.load("img/load.png")
                    dice1 = pg.transform.scale(dice1, (40, 40))
                    dice2 = pg.image.load("img/load.png")
                    dice2 = pg.transform.scale(dice1, (40, 40))

                    pieceremoved = True
                    fromcolumn = None
                    diceroll = []
                    doubledice = False
                    turn = "white"
                    tobearWhite = False
                    tobearBlack = False
                    break
                if PvPrect.collidepoint(x, y) == True:
                    menu = False
                    pvp = True
                    hittedWhite = Column(3, 0, "white", True)
                    hittedBlack = Column(23, 0, "black", True)

                    AllColumns = copy.deepcopy(initgood)
                    moving = False
                    toroll = True
                    dice1 = pg.image.load("img/load.png")
                    dice1 = pg.transform.scale(dice1, (40, 40))
                    dice2 = pg.image.load("img/load.png")
                    dice2 = pg.transform.scale(dice1, (40, 40))

                    pieceremoved = True
                    fromcolumn = None
                    diceroll = []
                    doubledice = False
                    turn = "white"
                    tobearWhite = False
                    tobearBlack = False
                    break
        menuimg = pg.image.load("img/menu.jpg")
        menuimg = pg.transform.scale(menuimg, (700, 700))
        screen.fill((0, 0, 0))
        screen.blit(menuimg, (0, 0))
        pg.display.update()
        continue

    if (pvp == True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                
                x, y = event.pos
                if exitRect.collidepoint(x,y):
                    menu=True
                    pvp=False
                    break
                if (toroll == True):
                    """
                    Setarea zarurilor
                    """
                    if button1.rect.collidepoint(x, y) == True:
                        doubledice = False
                        diceroll = []
                        diceroll.append(random.randint(1, 6))
                        diceroll.append(random.randint(1, 6))
                        if (diceroll[0] == diceroll[1]):
                            diceroll.append(diceroll[0])
                            diceroll.append(diceroll[0])
                            doubledice = True
                        dice1 = pg.image.load(
                            "img/dice"+str(diceroll[0])+".png")
                        dice1 = pg.transform.scale(dice1, (40, 40))
                        dice2 = pg.image.load(
                            "img/dice"+str(diceroll[1])+".png")
                        dice2 = pg.transform.scale(dice2, (40, 40))
                        toroll = False
                """
                Verificare daca o piese este iesita din casa , in vederea eliminarii lor
                """
                pieceOutsideHome = False
                for i in list(AllColumns.values())[6:25]:
                    if i.type == "black":
                        pieceOutsideHome = True
                        break

                if (event.button == 3 and toroll == False):
                    """
                    Eliminarea pieselor
                    """
                    if (tobearBlack == True and turn == "black" and pieceOutsideHome == False):
                        index = 0
                        if (hittedBlack.count == 0):
                            pieceremoved = False
                            for i in range(1, 7):
                                col = AllColumns[7-i]
                                if (col.type != "black"):
                                    continue
                                index = col.number
                                break

                            """
                            Setarea zarului astfel incat sa corespunda celei mai departate 
                            coloane care contine piese de scos
                            """
                            if index != 6:
                                if (len(diceroll) > 0):
                                    if (max(diceroll) > index):
                                        diceroll[diceroll.index(
                                            max(diceroll))] = index


                            for i in range(1, 7):
                                col = AllColumns[i]
                                if col.pgrect.collidepoint(x, y):
                                    if col.type == "black":
                                        if col.number in diceroll:
                                            AllColumns[col.number].remove()
                                            if (AllColumns[col.number].count == 0):
                                                AllColumns[col.number].setTypeNone(
                                                )
                                            diceroll.remove(col.number)
                                            pieceremoved = True
                                        else:
                                            continue
                            if (pieceremoved == True):
                                moving = False
                                break
                    if (tobearWhite == True and turn == "white"):
                        if (len(diceroll) == 0):
                            toroll = True
                            turn = "black"
                            moving = False
                            break
                        index = 0
                        pieceOutsideHome = False
                        for i in list(AllColumns.values())[1:19]:
                            if i.type == "white":
                                pieceOutsideHome = True
                            if (pieceOutsideHome == False):
                                if (hittedWhite.count == 0):
                                    pieceremoved = False
                                    for i in range(19, 25):
                                        col = AllColumns[i]
                                        if (col.type != "white"):
                                            continue
                                        index = 25-col.number
                                        break
                                    if index != 6:
                                        if (len(diceroll) > 0):

                                            if (max(diceroll) > index):
                                                diceroll[diceroll.index(
                                                    max(diceroll))] = index

                                    for i in range(19, 25):
                                        col = AllColumns[i]
                                        if col.pgrect.collidepoint(x, y):
                                            if col.type == "white":
                                                if 25-col.number in diceroll:
                                                    AllColumns[col.number].remove(
                                                    )
                                                    if (AllColumns[col.number].count == 0):
                                                        AllColumns[col.number].setTypeNone(
                                                        )
                                                    diceroll.remove(
                                                        25-col.number)
                                                    pieceremoved = True
                                                else:
                                                    continue
                                if (pieceremoved == True):
                                    moving = False
                                    break
                if (hittedWhite.count != 0 and turn == "white"):
                    """
                    Reintroducerea pieselor in joc , dupa ce au fost scoase de adversar
                    """
                    availabale = []
                    if diceroll == []:
                        toroll = True
                        turn = "black"
                        moving = False
                        continue
                    """
                    Verificarea valabilitatii locului unde se poate aseza piesa
                    """
                    if (len(diceroll) > 1):
                        if (AllColumns[diceroll[0]].type == "white" or AllColumns[diceroll[0]].type == None or (AllColumns[diceroll[0]].type == "black" and AllColumns[diceroll[0]].count == 1)):
                            availabale.append(diceroll[0])
                        if (AllColumns[diceroll[1]].type == "white" or AllColumns[diceroll[1]].type == None or (AllColumns[diceroll[1]].type == "black" and AllColumns[diceroll[1]].count == 1)):
                            availabale.append(diceroll[1])
                    else:
                        if (AllColumns[diceroll[0]].type == "white" or AllColumns[diceroll[0]].type == None or (AllColumns[diceroll[0]].type == "black" and AllColumns[diceroll[0]].count == 1)):
                            availabale.append(diceroll[0])
                    for i in range(1, 7):
                        col = AllColumns[i]
                        if col.pgrect.collidepoint(x, y):
                            if col.number in availabale:
                                if col.type == "black":
                                    AllColumns.get(col.number).add(turn)
                                    AllColumns.get(col.number).type = turn
                                    hittedWhite.remove()
                                    hittedBlack.add()
                                elif col.type is None:
                                    AllColumns.get(col.number).add(turn)
                                    hittedWhite.remove()
                                else:
                                    AllColumns.get(col.number).add()
                                    hittedWhite.remove()
                                diceroll.remove(col.number)
                    if (availabale == []):
                        toroll = True
                        turn = "black"
                        moving = False
                        continue
                    if (hittedWhite.count != 0):
                        continue
                    if (hittedWhite.count == 0):
                        moving = False

                if (hittedBlack.count != 0 and turn == "black"):
                    availabale = []
                    if diceroll == []:
                        toroll = True
                        turn = "white"
                        moving = False
                        continue
                    if (len(diceroll) > 1):
                        if (AllColumns[25-diceroll[0]].type == "black" or AllColumns[25-diceroll[0]].type == None or (AllColumns[25-diceroll[0]].type == "white" and AllColumns[25-diceroll[0]].count == 1)):
                            availabale.append(25-diceroll[0])
                        if (AllColumns[25-diceroll[1]].type == "black" or AllColumns[25-diceroll[1]].type == None or (AllColumns[25-diceroll[1]].type == "white" and AllColumns[25-diceroll[1]].count == 1)):
                            availabale.append(25-diceroll[1])
                    else:
                        if (AllColumns[25-diceroll[0]].type == "black" or AllColumns[25-diceroll[0]].type == None or (AllColumns[25-diceroll[0]].type == "white" and AllColumns[25-diceroll[0]].count == 1)):
                            availabale.append(25-diceroll[0])
                    for i in range(19, 25):
                        col = AllColumns[i]
                        if col.pgrect.collidepoint(x, y):
                            if col.number in availabale:
                                if col.type == "white":
                                    AllColumns.get(col.number).add(turn)
                                    AllColumns.get(col.number).type = turn
                                    hittedBlack.remove()
                                    hittedWhite.add()
                                elif col.type is None:
                                    AllColumns.get(col.number).add(turn)
                                    hittedBlack.remove()
                                else:
                                    AllColumns.get(col.number).add()
                                    hittedBlack.remove()
                                diceroll.remove(25-col.number)
                    if (availabale == []):
                        toroll = True
                        turn = "white"
                        moving = False
                        continue
                    if (hittedBlack.count != 0):
                        continue
                    if (hittedBlack.count == 0):
                        moving = False

                elif (event.button == 1):
                    if (moving == False and toroll == False):
                        """
                        Alegerea piesei pe care dorim sa o mutam
                        moving=False inseamna ca alegem piesa
                        moving=True inseamna ca este in curs de mutare
                        """
                        if (len(diceroll) == 0):
                            moving = False
                            toroll = True
                            if (turn == "white"):
                                turn = "black"
                            else:
                                turn = "white"
                            continue

                        anyMovePossible = False
                        """
                        Se verifica daca exista macar o mutare posibila
                        """
                        for j in diceroll:
                            anyMovePossible = checkifanyavailable(j, turn)
                            if (anyMovePossible != False):
                                break
                        
                        if anyMovePossible == False:
                            """
                            Se verifica cazul in care , nu exista mutare disponibila 
                            dar totusi se poate elimina piesa din casa
                            """
                            outside = False
                            if (turn == "white"):
                                if (tobearWhite == True):
                                    for i in list(AllColumns.values())[1:19]:
                                        if i.type == "turn":
                                            outside = True
                                    if (outside == False):
                                        continue
                            else:
                                if (tobearBlack == True):
                                    for i in list(AllColumns.values())[1:19]:
                                        if i.type == "turn":
                                            outside = True
                                    if (outside == False):
                                        continue
                            toroll = True
                            moving = False
                            if (turn == "white"):
                                turn = "black"
                            else:
                                turn = "white"
                            continue

                        colavail = []
                        for i in AllColumns.values():
                            if i.pgrect.collidepoint(x, y):
                                if i.type == turn:
                                    if (doubledice == False):
                                        if (len(diceroll) == 2):
                                            dice1Availablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            dice2Availablepoz = i.checkavailabletomove(
                                                diceroll[1])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                diceroll[0]+diceroll[1])
                                            if (dice1Availablepoz != 0):
                                                colavail.append(
                                                    dice1Availablepoz)
                                            if (dice2Availablepoz != 0):
                                                colavail.append(
                                                    dice2Availablepoz)
                                            if (sumAvailablepoz != 0 and (dice1Availablepoz != 0 or dice2Availablepoz != 0)):
                                                colavail.append(
                                                    sumAvailablepoz)
                                        elif (len(diceroll) == 1):
                                            dice1Availablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            if (dice1Availablepoz != 0):
                                                colavail.append(
                                                    dice1Availablepoz)
                                    if (doubledice == True):
                                        if (len(diceroll) == 4):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                2*diceroll[0])
                                            sum2Availablepoz = i.checkavailabletomove(
                                                3*diceroll[0])
                                            sum3Availablepoz = i.checkavailabletomove(
                                                4*diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0:
                                                colavail.append(
                                                    sumAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0 and sum2Availablepoz != 0:
                                                colavail.append(
                                                    sum2Availablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0 and sum2Availablepoz != 0 and sum3Availablepoz:
                                                colavail.append(
                                                    sum3Availablepoz)
                                        elif (len(diceroll) == 3):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                2*diceroll[0])
                                            sum2Availablepoz = i.checkavailabletomove(
                                                3*diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0:
                                                colavail.append(
                                                    sumAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0 and sum2Availablepoz != 0:
                                                colavail.append(
                                                    sum2Availablepoz)
                                        elif (len(diceroll) == 2):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                2*diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0:
                                                colavail.append(
                                                    sumAvailablepoz)
                                        elif (len(diceroll) == 1):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)

                                    fromcolumn = i
                                    if (len(colavail) != 0):
                                        moving = True

                    elif (moving == True):
                        for i in AllColumns.values():
                            if i.pgrect.collidepoint(x, y):
                                if i.number in colavail:
                                    if (i.type == None):
                                        AllColumns.get(i.number).add(turn)
                                    else:
                                        if (i.count == 1 and i.type != turn):
                                            AllColumns.get(i.number).add(turn)
                                            AllColumns.get(
                                                i.number).type = turn
                                            if (turn == "white"):
                                                hittedBlack.add()
                                            else:
                                                hittedWhite.add()

                                        else:
                                            AllColumns.get(i.number).add()
                                    AllColumns.get(fromcolumn.number).remove()
                                    moving = False
                                    if (i.type == "white"):
                                        if (doubledice == False):
                                            if len(diceroll) == 2:
                                                if i.number == fromcolumn.number+diceroll[0]+diceroll[1]:
                                                    diceroll = []
                                                elif (i.number == fromcolumn.number+diceroll[0]):
                                                    diceroll.remove(
                                                        diceroll[0])
                                                elif (i.number == fromcolumn.number+diceroll[1]):
                                                    diceroll.remove(
                                                        diceroll[1])
                                            elif len(diceroll) == 1:
                                                if (i.number == fromcolumn.number+diceroll[0]):
                                                    diceroll.remove(
                                                        diceroll[0])
                                        else:
                                            if i.number == fromcolumn.number+4*diceroll[0]:
                                                diceroll = []
                                            elif i.number == fromcolumn.number+3*diceroll[0]:
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                            elif i.number == fromcolumn.number+2*diceroll[0]:
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                            elif i.number == fromcolumn.number+diceroll[0]:
                                                diceroll.remove(diceroll[0])

                                    else:
                                        if (doubledice == False):
                                            if len(diceroll) == 2:
                                                if i.number == fromcolumn.number-diceroll[0]-diceroll[1]:
                                                    diceroll = []
                                                elif (i.number == fromcolumn.number-diceroll[0]):
                                                    diceroll.remove(
                                                        diceroll[0])
                                                elif (i.number == fromcolumn.number-diceroll[1]):
                                                    diceroll.remove(
                                                        diceroll[1])
                                            elif len(diceroll) == 1:
                                                if (i.number == fromcolumn.number-diceroll[0]):
                                                    diceroll.remove(
                                                        diceroll[0])
                                        else:
                                            if i.number == fromcolumn.number-4*diceroll[0]:
                                                diceroll = []
                                            elif i.number == fromcolumn.number-3*diceroll[0]:
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                            elif i.number == fromcolumn.number-2*diceroll[0]:
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                            elif i.number == fromcolumn.number-diceroll[0]:
                                                diceroll.remove(diceroll[0])

                                    if (AllColumns.get(fromcolumn.number).count == 0):
                                        AllColumns.get(
                                            fromcolumn.number).setTypeNone()

                                    if (tobearWhite != True):
                                        tobearWhite = checktobear("white")
                                        if (tobearWhite == True):
                                            continue
                                    if (tobearBlack != True):
                                        tobearBlack = checktobear("black")

                                    break
                                else:
                                    moving = False
                                    break

    if (pvc == True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break
            if event.type == pg.USEREVENT+2 and turn == "black":
                if (checkfinish() == True):
                    break
                if (toroll == True):
                    doubledice = False
                    diceroll = []
                    diceroll.append(random.randint(1, 6))
                    diceroll.append(random.randint(1, 6))
                    if (diceroll[0] == diceroll[1]):
                        diceroll.append(diceroll[0])
                        diceroll.append(diceroll[0])
                        doubledice = True
                    dice1 = pg.image.load("img/dice"+str(diceroll[0])+".png")
                    dice1 = pg.transform.scale(dice1, (40, 40))
                    dice2 = pg.image.load("img/dice"+str(diceroll[1])+".png")
                    dice2 = pg.transform.scale(dice2, (40, 40))
                    toroll = False
                else:
                    print(diceroll)
                    if (len(diceroll) == 0):
                        turn = "white"
                        toroll = True
                        moving = False
                        if (checkfinish() == True):
                            break
                        continue

                    if (tobearBlack == True):
                        index = 0
                        pieceOutsideHome = False
                        for i in list(AllColumns.values())[6:24]:
                            if i.type == "black":
                                pieceOutsideHome = True
                        if (pieceOutsideHome == False):
                            if (hittedBlack.count == 0):
                                pieceremoved = False
                                for i in range(1, 7):
                                    col = AllColumns[7-i]
                                    if (col.type != "black"):
                                        continue
                                    index = col.number
                                    break
                                if index != 6:
                                    if (len(diceroll) >= 2):
                                        if (max(diceroll) > index):
                                            diceroll[diceroll.index(
                                                max(diceroll))] = index
                                    elif (len(diceroll) == 1):
                                        if (max(diceroll) > index):
                                            diceroll[0] = index
                                
                                choseToBear = random.choice(diceroll)
                                AllColumns[col.number].remove()
                                if (AllColumns[col.number].count == 0):
                                    AllColumns[col.number].setTypeNone(
                                    )
                                diceroll.remove(choseToBear)
                                pieceremoved = True
                                if (pieceremoved == True):
                                    pg.event.post(
                                        pg.event.Event(pg.USEREVENT+2))
                                    if (checkfinish() == True):
                                        break
                                    continue

                    if (hittedBlack.count != 0):
                        availabale = []
                        if (len(diceroll) > 1):
                            if (AllColumns[25-diceroll[0]].type == "black" or AllColumns[25-diceroll[0]].type == None or (AllColumns[25-diceroll[0]].type == "white" and AllColumns[25-diceroll[0]].count == 1)):
                                availabale.append(25-diceroll[0])
                            if (AllColumns[25-diceroll[1]].type == "black" or AllColumns[25-diceroll[1]].type == None or (AllColumns[25-diceroll[1]].type == "white" and AllColumns[25-diceroll[1]].count == 1)):
                                availabale.append(25-diceroll[1])
                        else:
                            if (AllColumns[25-diceroll[0]].type == "black" or AllColumns[25-diceroll[0]].type == None or (AllColumns[25-diceroll[0]].type == "white" and AllColumns[25-diceroll[0]].count == 1)):
                                availabale.append(25-diceroll[0])
                        if (availabale == []):
                            toroll = True
                            turn = "white"
                            moving = False
                            if (checkfinish() == True):
                                break
                            continue
                        chosenPoz = 0
                        if (len(availabale) > 1):
                            chosenPoz = availabale[random.randint(
                                0, len(availabale)-1)]
                        elif len(availabale) == 1:
                            chosenPoz = availabale[0]
                        elif len(availabale) == 0:
                            turn = "white"
                            toroll = True
                            if (checkfinish() == True):
                                break
                            continue
                        col = AllColumns[chosenPoz]
                        if col.type is None:
                            AllColumns.get(col.number).add(turn)
                            hittedBlack.remove()

                        elif col.type == "white":
                            AllColumns.get(col.number).add(turn)
                            AllColumns.get(col.number).type = turn
                            hittedBlack.remove()
                            hittedWhite.add()
                        else:
                            AllColumns.get(col.number).add()
                            hittedBlack.remove()
                        diceroll.remove(25-col.number)

                    else:
                        startPoz = filter(lambda v: v.type ==
                                          "black", AllColumns.values())
                        availStartPoz = []
                        for i in startPoz:
                            if len(diceroll) == 2:
                                if (i.checkavailabletomove(diceroll[0]) != 0 or i.checkavailabletomove(diceroll[1]) != 0):
                                    availStartPoz.append(i)
                            else:
                                if i.checkavailabletomove(diceroll[0]) != 0:
                                    availStartPoz.append(i)

                        if (availStartPoz == []):
                            turn = "white"
                            toroll = True
                            if (checkfinish() == True):
                                break
                            continue
                        if len(availStartPoz) > 1:
                            chosenStart = availStartPoz[random.randint(
                                0, len(availStartPoz)-1)]
                        else:
                            chosenStart = availStartPoz[0]
                        avMovePoz = []
                        av1 = 0
                        av2 = 0
                        av3 = 0
                        av4 = 0
                        if (len(diceroll) == 2):
                            av1 = chosenStart.checkavailabletomove(diceroll[0])
                            av2 = chosenStart.checkavailabletomove(diceroll[1])
                            if (av1 != 0 or av2 != 0) and chosenStart.checkavailabletomove(diceroll[0]+diceroll[1]) != 0:
                                av3 = chosenStart.checkavailabletomove(
                                    diceroll[0]+diceroll[1])
                            if (av1 != 0):
                                avMovePoz.append(av1)
                            if (av2 != 0):
                                avMovePoz.append(av2)
                            if (av3 != 0):
                                avMovePoz.append(av3)

                        elif (len(diceroll) == 1):
                            av1 = chosenStart.checkavailabletomove(diceroll[0])
                            if (av1 != 0):
                                avMovePoz.append(av1)
                        elif len(diceroll) == 4:
                            av1 = chosenStart.checkavailabletomove(diceroll[0])
                            av2 = chosenStart.checkavailabletomove(
                                2*diceroll[0])
                            av3 = chosenStart.checkavailabletomove(
                                3*diceroll[0])
                            av4 = chosenStart.checkavailabletomove(
                                4*diceroll[0])
                            if (av1 != 0):
                                avMovePoz.append(av1)
                            if (av2 != 0 and av1 != 0):
                                avMovePoz.append(av2)
                            if (av3 != 0 and av2 != 0 and av1 != 0):
                                avMovePoz.append(av3)
                            if (av4 != 0 and av3 != 0 and av2 != 0 and av1 != 0):
                                avMovePoz.append(av4)
                        elif len(diceroll) == 3:
                            av1 = chosenStart.checkavailabletomove(diceroll[0])
                            av2 = chosenStart.checkavailabletomove(
                                2*diceroll[0])
                            av3 = chosenStart.checkavailabletomove(
                                3*diceroll[0])
                            if (av1 != 0):
                                avMovePoz.append(av1)
                            if (av2 != 0 and av1 != 0):
                                avMovePoz.append(av2)
                            if (av3 != 0 and av2 != 0 and av1 != 0):
                                avMovePoz.append(av3)

                        if (len(avMovePoz)) < 2:
                            movedest = avMovePoz[0]
                        else:
                            movedest = avMovePoz[random.randint(
                                0, len(avMovePoz)-1)]
                        AllColumns[chosenStart.number].remove()
                        if (AllColumns[chosenStart.number].count) == 0:
                            AllColumns[chosenStart.number].setTypeNone()
                        if (AllColumns[movedest]).type == None:
                            AllColumns[movedest].add("black")
                        elif AllColumns[movedest].type == "black":
                            AllColumns[movedest].add()
                        elif AllColumns[movedest].type == "white":
                            AllColumns[movedest].add("black")
                            hittedWhite.add()

                        if (doubledice == False):
                            if (len(diceroll) == 2):
                                if (av1 == movedest):
                                    diceroll.remove(diceroll[0])
                                if (av2 == movedest):
                                    diceroll.remove(diceroll[1])
                                if (av3 == movedest):
                                    diceroll.remove(diceroll[1])
                                    diceroll.remove(diceroll[0])
                            elif (len(diceroll) == 1):
                                if (av1 == movedest):
                                    diceroll.remove(diceroll[0])
                        if (doubledice == True):
                            if movedest == chosenStart.number-4*diceroll[0]:
                                diceroll = []
                            elif movedest == chosenStart.number-3*diceroll[0]:
                                diceroll.remove(diceroll[0])
                                diceroll.remove(diceroll[0])
                                diceroll.remove(diceroll[0])
                            elif movedest == chosenStart.number-2*diceroll[0]:
                                diceroll.remove(diceroll[0])
                                diceroll.remove(diceroll[0])
                            elif movedest == chosenStart.number-diceroll[0]:
                                diceroll.remove(diceroll[0])
                        if (AllColumns[chosenStart.number].count == 0):
                            AllColumns[chosenStart.number].setTypeNone()
                        if (tobearBlack != True):
                            tobearBlack = checktobear("black")
                        print("startPoz ", chosenStart.number,
                              "MovePoz ", movedest)
                if (checkfinish() == True):
                    break
                if (turn == "black"):
                    pg.event.post(pg.event.Event(pg.USEREVENT+2))

            if event.type == pg.MOUSEBUTTONDOWN and turn == "white":
                x, y = event.pos
                if exitRect.collidepoint(x,y):
                    menu=True
                    pvc=False
                    break
                if (checkfinish() == True):
                    break
                clickOnInteresetzone = False
                for i in AllColumns.values():
                    if i.pgrect.collidepoint(x, y) == True:
                        clickOnInteresetzone = True
                        break
                if button1.rect.collidepoint(x, y) == True:
                    clickOnInteresetzone = True

                if clickOnInteresetzone == False:
                    moving = False
                    continue
                if (toroll == True):
                    if button1.rect.collidepoint(x, y) == True:
                        doubledice = False
                        diceroll = []
                        diceroll.append(random.randint(1, 6))
                        diceroll.append(random.randint(1, 6))
                        if (diceroll[0] == diceroll[1]):
                            diceroll.append(diceroll[0])
                            diceroll.append(diceroll[0])
                            doubledice = True
                        dice1 = pg.image.load(
                            "img/dice"+str(diceroll[0])+".png")
                        dice1 = pg.transform.scale(dice1, (40, 40))
                        dice2 = pg.image.load(
                            "img/dice"+str(diceroll[1])+".png")
                        dice2 = pg.transform.scale(dice2, (40, 40))
                        toroll = False
                        continue
                if (event.button == 3 and toroll == False):
                    if (tobearWhite == False):
                        tobearWhite == checktobear("white")
                    x, y = event.pos
                    pieceOutsideHome = False
                    for i in list(AllColumns.values())[0:18]:
                        if i.type == "white":
                            pieceOutsideHome = True
                            continue
                    if (tobearWhite == True and pieceOutsideHome == False):
                        if (len(diceroll) == 0):
                            toroll = True
                            turn = "black"
                            pg.event.post(pg.event.Event(pg.USEREVENT+2))
                            moving = False
                            if (checkfinish() == True):
                                break
                            continue
                        index = 0
                        if (hittedWhite.count == 0):
                            pieceremoved = False
                            for i in range(19, 25):
                                col = AllColumns[i]
                                if (col.type != "white"):
                                    continue
                                index = 25-col.number
                                break
                            if index != 6:
                                if (len(diceroll) >= 2):
                                    if (max(diceroll) > index):
                                        diceroll[diceroll.index(
                                            max(diceroll))] = index
                                elif (len(diceroll) == 1):
                                    if (max(diceroll) > index):
                                        diceroll[0] = index
                            for i in range(19, 25):
                                col = AllColumns[i]
                                if col.pgrect.collidepoint(x, y):
                                    if col.type == "white":
                                        if 25-col.number in diceroll:
                                            AllColumns[col.number].remove()
                                            if (AllColumns[col.number].count == 0):
                                                AllColumns[col.number].setTypeNone(
                                                )
                                            diceroll.remove(25-col.number)
                                            pieceremoved = True
                                        else:
                                            if (checkfinish() == True):
                                                break
                                            continue
                        if (pieceremoved == True):
                            moving = False
                            if (checkfinish() == True):
                                break
                            continue
                    if (turn == "black"):
                        pg.event.post(pg.event.Event(pg.USEREVENT+2))
                if (event.button == 1):
                    if (tobearWhite == False):
                        tobearBlack == checktobear("white")
                    if (hittedWhite.count != 0 and turn == "white"):
                        availabale = []
                        if diceroll == []:
                            toroll = True
                            turn = "black"
                            pg.event.post(pg.event.Event(pg.USEREVENT+2))
                            moving = False
                            if (checkfinish() == True):
                                break
                            continue
                        if (len(diceroll) > 1):
                            if (AllColumns[diceroll[0]].type == "white" or AllColumns[diceroll[0]].type == None or (AllColumns[diceroll[0]].type == "black" and AllColumns[diceroll[0]].count == 1)):
                                availabale.append(diceroll[0])
                            if (AllColumns[diceroll[1]].type == "white" or AllColumns[diceroll[1]].type == None or (AllColumns[diceroll[1]].type == "black" and AllColumns[diceroll[1]].count == 1)):
                                availabale.append(diceroll[1])
                        else:
                            if (AllColumns[diceroll[0]].type == "white" or AllColumns[diceroll[0]].type == None or (AllColumns[diceroll[0]].type == "black" and AllColumns[diceroll[0]].count == 1)):
                                availabale.append(diceroll[0])
                        for i in range(1, 7):
                            col = AllColumns[i]
                            if col.pgrect.collidepoint(x, y):
                                if col.number in availabale:
                                    if col.type == "black":
                                        AllColumns.get(col.number).add(turn)
                                        AllColumns.get(col.number).type = turn
                                        hittedWhite.remove()
                                        hittedBlack.add()
                                    elif col.type is None:
                                        AllColumns.get(col.number).add(turn)
                                        hittedWhite.remove()
                                    else:
                                        AllColumns.get(col.number).add()
                                        hittedWhite.remove()
                                    diceroll.remove(col.number)

                        if (availabale == []):
                            outside = False
                            if (tobearWhite == True):
                                for i in list(AllColumns.values())[1:19]:
                                    if i.type == "white":
                                        outside = True
                                if (outside == False):
                                    continue
                            toroll = True
                            turn = "black"
                            pg.event.post(pg.event.Event(pg.USEREVENT+2))
                            moving = False
                            if (checkfinish() == True):
                                break
                            continue
                        if (hittedWhite.count != 0):
                            continue
                        if (hittedWhite.count == 0):
                            moving = False
                    if (moving == False and toroll == False):
                        anyMovePossible = False
                        for j in diceroll:
                            anyMovePossible = checkifanyavailable(j, turn)
                            if (anyMovePossible != False):
                                break

                        if anyMovePossible == False:
                            if (tobearWhite == True):
                                anyMovePossible = True
                                continue
                            toroll = True
                            moving = False
                            if (turn == "white"):
                                turn = "black"
                                pg.event.post(pg.event.Event(pg.USEREVENT+2))
                            else:
                                turn = "white"
                            if (checkfinish() == True):
                                break
                            continue

                        colavail = []
                        for i in AllColumns.values():
                            if i.pgrect.collidepoint(x, y):
                                if i.type == turn:
                                    if (doubledice == False):
                                        if (len(diceroll) == 2):
                                            dice1Availablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            dice2Availablepoz = i.checkavailabletomove(
                                                diceroll[1])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                diceroll[0]+diceroll[1])
                                            if (dice1Availablepoz != 0):
                                                colavail.append(
                                                    dice1Availablepoz)
                                            if (dice2Availablepoz != 0):
                                                colavail.append(
                                                    dice2Availablepoz)
                                            if (sumAvailablepoz != 0 and (dice1Availablepoz != 0 or dice2Availablepoz != 0)):
                                                colavail.append(
                                                    sumAvailablepoz)
                                        elif (len(diceroll) == 1):
                                            dice1Availablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            if (dice1Availablepoz != 0):
                                                colavail.append(
                                                    dice1Availablepoz)
                                    if (doubledice == True):
                                        if (len(diceroll) == 4):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                2*diceroll[0])
                                            sum2Availablepoz = i.checkavailabletomove(
                                                3*diceroll[0])
                                            sum3Availablepoz = i.checkavailabletomove(
                                                4*diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0:
                                                colavail.append(
                                                    sumAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0 and sum2Availablepoz != 0:
                                                colavail.append(
                                                    sum2Availablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0 and sum2Availablepoz != 0 and sum3Availablepoz:
                                                colavail.append(
                                                    sum3Availablepoz)
                                        elif (len(diceroll) == 3):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                2*diceroll[0])
                                            sum2Availablepoz = i.checkavailabletomove(
                                                3*diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0:
                                                colavail.append(
                                                    sumAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0 and sum2Availablepoz != 0:
                                                colavail.append(
                                                    sum2Availablepoz)
                                        elif (len(diceroll) == 2):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            sumAvailablepoz = i.checkavailabletomove(
                                                2*diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)
                                            if sumAvailablepoz != 0 and diceAvailablepoz != 0:
                                                colavail.append(
                                                    sumAvailablepoz)
                                        elif (len(diceroll) == 1):
                                            diceAvailablepoz = i.checkavailabletomove(
                                                diceroll[0])
                                            if (diceAvailablepoz != 0):
                                                colavail.append(
                                                    diceAvailablepoz)

                                    fromcolumn = i
                                    if (len(colavail) != 0):
                                        moving = True

                    elif (moving == True):
                        for i in AllColumns.values():
                            if i.pgrect.collidepoint(x, y):
                                if i.number in colavail:
                                    if (i.type == None):
                                        AllColumns.get(i.number).add(turn)
                                    else:
                                        if (i.count == 1 and i.type != turn):
                                            AllColumns.get(i.number).add(turn)
                                            AllColumns.get(
                                                i.number).type = turn
                                            hittedBlack.add()
                                        else:
                                            AllColumns.get(i.number).add()
                                    AllColumns.get(fromcolumn.number).remove()
                                    moving = False
                                    if (i.type == "white"):
                                        if (doubledice == False):
                                            if len(diceroll) == 2:
                                                if i.number == fromcolumn.number+diceroll[0]+diceroll[1]:
                                                    diceroll = []
                                                elif (i.number == fromcolumn.number+diceroll[0]):
                                                    diceroll.remove(
                                                        diceroll[0])
                                                elif (i.number == fromcolumn.number+diceroll[1]):
                                                    diceroll.remove(
                                                        diceroll[1])
                                            elif len(diceroll) == 1:
                                                if (i.number == fromcolumn.number+diceroll[0]):
                                                    diceroll.remove(
                                                        diceroll[0])
                                        else:
                                            if i.number == fromcolumn.number+4*diceroll[0]:
                                                diceroll = []
                                            elif i.number == fromcolumn.number+3*diceroll[0]:
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                            elif i.number == fromcolumn.number+2*diceroll[0]:
                                                diceroll.remove(diceroll[0])
                                                diceroll.remove(diceroll[0])
                                            elif i.number == fromcolumn.number+diceroll[0]:
                                                diceroll.remove(diceroll[0])

                                    if (AllColumns.get(fromcolumn.number).count == 0):
                                        AllColumns.get(
                                            fromcolumn.number).setTypeNone()

                                    if (tobearWhite != True):
                                        tobearWhite = checktobear("white")
                                    continue
                                else:
                                    moving = False
                                    if (checkfinish() == True):
                                        break
                                    continue
                        if (len(diceroll) == 0):
                            moving = False
                            toroll = True
                            if (turn == "white"):
                                turn = "black"
                                pg.event.post(pg.event.Event(pg.USEREVENT+2))
                            else:
                                turn = "white"
                    if (turn == "black"):
                        pg.event.post(pg.event.Event(pg.USEREVENT+2))

    if (checkfinish() == True):
        menu = True
        continue
    if (toroll == True):
        dice1 = pg.image.load("img/load.png")
        dice1 = pg.transform.scale(dice1, (40, 40))
        dice2 = pg.image.load("img/load.png")
        dice2 = pg.transform.scale(dice1, (40, 40))
    font = pg.font.SysFont(None, 25)
    text = font.render(turn, True, (255, 255, 255))
    text = font.render(turn, True, (255, 255, 255))
    screen.blit(bkg,(0,0))
    screen.blit(board, (0, 0))
    for x in AllColumns.values():
        x.show()
    hittedBlack.show()
    hittedWhite.show()
    button1.show()
    screen.blit(dice1, (620, 250))
    screen.blit(dice2, (620, 350))
    screen.blit(exitgame,(650,650))
    font = pg.font.SysFont(None, 25)
    if(toroll==False):
        text = font.render(turn + " Turn " + "Dice available to move " +
                        str(diceroll),  True, (255, 255, 255))
    else:text = font.render(turn + " Turn " + "ROLL " 
                        ,  True, (255, 255, 255))
    screen.blit(text, (10, 630))
    pg.display.update()

pg.quit()
