PREFLOP = 0
FLOP = 1
TURN = 2
RIVER = 3
SMALL = 4
BIG = 5

CALL = 0
FOLD = 1
RAISE = 2

class game:
    def __init__(self, number, playerList, tableCards):
        self.number = number
        self.playerList = playerList
        self.tableCards = tableCards

class player:
    def __init__(self, name, handcards, preChipStack):
        self.name = name
        self.handcards = handcards
        self.actions = [[]] * 6
        self.chipStack = preChipStack

    def setAction(self, action, situation):
        self.actions[situation].append(action)

class action:
    def __init__(self, act, prePotSize, raiseAmount):
        self.prePotSize = prePotSize
        self.raiseAmount = raiseAmount
        self.act = act

def createPlayers(logText):
    ret = []
    name = ""
    stack = ""
    handcards = None
    username = logText.split("Dealt to ")[1].split()[0]
    seatSplit = logText.split("Seat ")
    for seatText in seatSplit[2:]:
        name = seatText.split(": ")[1].split(" ($")[0]
        stack = float(seatText.split(" ($")[1].split()[0])
        if(name == username):
                handcards = logText.split("Dealt to ")[1].split("[")[1][:5]
        ret.append(player(name, handcards, stack))
        handcards = None
        if(len(seatText) > 50):
            break
    return ret

def analyzeSituation(text, players, situation, actualPot, bigBlind):
    ret = []
    actualRaise = bigBlind
    #Delete "*** HOLE CARDS ***"-Tag and HandCards-Tag
    singleLines = text.split("\n")
    for singleLine in singleLines:
        playername = singleLine.split(":")[0]
        playerobj = next((x for x in players if x.name == playername), None)
        if(playerobj == None):
            continue
        if("folds" in singleLine):
            playerobj.setAction(action(FOLD, actualPot, actualRaise), situation)
        if("bets" in singleLine):
            actualRaise = float(singleLine.split(": bets $")[1].split()[0])
            playerobj.setAction(action(RAISE, actualPot, actualRaise), situation)
            actualPot =+ actualRaise
        if("calls" in singleLine):
            playerobj.setAction(action(CALL, actualPot, actualRaise), situation)
            actualPot =+ actualRaise
    return actualPot 

def parseGame(logText):
    
    if("#" not in logText):
        return None

    # get game number
    gamenum = int(logText.split("#")[1].split(":")[0])

    #get board cards
    if("Board [" in logText):
        board = logText.split("Board [")[1].split("]")[0]
    board = None

    # create Players
    players = createPlayers(logText)

    # create SmallBlind
    smallPlayer = logText.split(": posts small blind $")[0].split("\n")[-1]
    smallBlind = float(logText.split(": posts small blind $")[1].split("\n")[0])
    playerobj = next((x for x in players if x.name == smallPlayer), None)
    assert (playerobj != None)
    playerobj.setAction(action(SMALL, 0, smallBlind), SMALL)

    # create BigBlind
    smallPlayer = logText.split(": posts small blind $")[0].split("\n")[-1]
    bigBlind = float(logText.split(": posts big blind $")[1].split("\n")[0])
    playerobj = next((x for x in players if x.name == smallPlayer), None)
    assert (playerobj != None)
    playerobj.setAction(action(BIG, 0, bigBlind), BIG)

    # analyze PreFlop
    if("*** FLOP ***" in logText):
        preFlopText = logText.split("*** HOLE CARDS ***")[1].split("\n*** FLOP ***")[0].split("]\n")[1]
        actualpot = analyzeSituation(preFlopText, players, PREFLOP, smallBlind + bigBlind, bigBlind)
    else:
        preFlopText = logText.split("*** HOLE CARDS ***")[1].split("\n*** SUMMARY ***")[0].split("]\n")[1]
        actualpot = analyzeSituation(preFlopText, players, PREFLOP, smallBlind + bigBlind, bigBlind)

    # analyze Flop
    if("*** FLOP ***" in logText and "*** TURN ***" in logText):
        flopText = logText.split("*** FLOP ***")[1].split("]\n")[1].split("\n*** TURN ***")[0]
        actualpot = analyzeSituation(flopText, players, FLOP, actualpot, bigBlind)
    if("*** FLOP ***" in logText and not "*** TURN ***" in logText):
        flopText = logText.split("*** FLOP ***")[1].split("]\n")[1].split("\n*** SUMMARY ***")[0]
        actualpot = analyzeSituation(flopText, players, FLOP, actualpot, bigBlind)

    # analyze TURN
    if("*** TURN ***" in logText and "*** RIVER ***" in logText):
        turnText = logText.split("*** TURN ***")[1].split("]\n")[1].split("\n*** RIVER ***")[0]
        actualpot = analyzeSituation(turnText, players, TURN, actualpot, bigBlind)
    if("*** TURN ***" in logText and not "*** RIVER ***" in logText):
        turnText = logText.split("*** TURN ***")[1].split("]\n")[1].split("\n*** SHOW DOWN ***")[0]
        actualpot = analyzeSituation(turnText, players, TURN, actualpot, bigBlind)
           
    # analyze RIVER
    if("*** RIVER ***" in logText and "*** SHOW DOWN ***" in logText):
        riverText = logText.split("*** RIVER ***")[1].split("]\n")[1].split("\n*** SHOW DOWN ***")[0]
        actualpot = analyzeSituation(riverText, players, RIVER, actualpot, bigBlind)  
    if("*** RIVER ***" in logText and not "*** SHOW DOWN ***" in logText):
        riverText = logText.split("*** RIVER ***")[1].split("]\n")[1].split("\n*** SUMMARY ***")[0]
        actualpot = analyzeSituation(riverText, players, RIVER, actualpot, bigBlind)

    return game(gamenum, players, board)

def parseLogFile(path_to_file):
    op = open (path_to_file, "r")
    data=op.read()
    splitdata = data.split("\n\n\n\n")
    games = []
    for logText in splitdata:
        game_temp = parseGame(logText)
        if(game_temp != None):
            games.append(game_temp)
    return games

for x in parseLogFile("./TestData/testLog.txt"):
    print("---"+str(x.number)+"---")
    for y in x.playerList:
        print(y.name, y.chipStack)
        for z in y.actions:
            print(" ")
            for ß in z:
                print(ß.act, ß.raiseAmount)
    print("---------------------")