dict_situations = { "PREGAME" : 1, "PREFLOP" : 2, "FLOP" : 3, "TURN" : 4, "RIVER" : 5}
dict_action = {"CALL" : 0, "FOLD" : 1, "RAISE" : 2}

class game:
    def __init__(self, number, playerList, tableCards, winner):
        self.number = number
        self.playerList = playerList
        self.tableCards = tableCards
        self.winner = winner

class player:
    def __init__(self, name, handcards, preChipStack):
        self.name = name
        self.handcards = handcards
        self.actions = {k: [] for k in range(6)}
        self.chipStack = preChipStack

    def setAction(self, action, situation):
        self.actions[dict_situations[situation]].append(action)

class action:
    def __init__(self, act, preSinglePot, raiseAmount, postSinglePot, preCompletePot, postCompletePot):
        self.preSinglePot = preSinglePot
        self.postSinglePot = postSinglePot
        self.preCompletePot = preCompletePot
        self.postCompletePot = postCompletePot
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

def analyzeSituation(text, players, situation, actualPot, preCompletePot, bigBlind):
    ret = []
    actualRaise = bigBlind
    singleLines = text.split("\n")
    for singleLine in singleLines:
        playername = singleLine.split(":")[0]
        playerobj = next((x for x in players if x.name == playername), None)
        if(playerobj == None):
            continue
        if("folds" in singleLine):
       
            playerobj.setAction(action("FOLD", actualPot, actualRaise,  actualPot + actualRaise, preCompletePot, preCompletePot + actualRaise), situation)
            continue
        if("bets" in singleLine and (not "all-in" in singleLine)):
            actualRaise = float(singleLine.split(": bets $")[1].split()[0])
            playerobj.setAction(action("BETS", actualPot, actualRaise, actualPot + actualRaise, preCompletePot, preCompletePot + actualRaise), situation)
            actualPot =+ actualRaise
            continue
        if(("raises" in singleLine) and (not "all-in" in singleLine)):
            actualRaise = float(singleLine.split(": raises $")[1].split()[0])
            playerobj.setAction(action("RAISE", actualPot, actualRaise, actualPot + actualRaise, preCompletePot, preCompletePot + actualRaise), situation)
            actualPot =+ actualRaise
            continue
        if("all-in" in singleLine):
            if("raises" in singleLine):
                actualRaise = float(singleLine.split(": raises $")[1].split()[0])
            if("bets" in singleLine):
                actualRaise = float(singleLine.split(": bets $")[1].split()[0])
            playerobj.setAction(action("ALL IN", actualPot, actualRaise, actualPot + actualRaise, preCompletePot, preCompletePot + actualRaise), situation)
            actualPot =+ actualRaise
            continue
        if("calls" in singleLine):
            playerobj.setAction(action("CALL", actualPot, actualRaise, actualPot + actualRaise, preCompletePot, preCompletePot + actualRaise), situation)
            continue
    return actualPot, preCompletePot + actualRaise

def printPlayerStats(player):
    print(player.name,"\n", "Handcards: ", player.handcards, " Chipstack: ", player.chipStack)
    for key,values in player.actions.items():
     for v in values:
          print(list(dict_situations.keys())[list(dict_situations.values()).index(key)]," : ", v.act, "( RaiseAmount: ", v.raiseAmount, " PrePotSize: ", v.preCompletePot, " )")

def parseGame(logText):
    
    if("#" not in logText):
        return None

    # get game number
    gamenum = int(logText.split("#")[1].split(":")[0])

    #get board cards
    if("Board [" in logText):
        board = logText.split("Board [")[1].split("]")[0]
    else:
        board = None

    # create Players
    players = createPlayers(logText)

    # create SmallBlind
    smallPlayer = logText.split(": posts small blind $")[0].split("\n")[-1]
    smallBlind = float(logText.split(": posts small blind $")[1].split("\n")[0])
    playerobj = next((x for x in players if x.name == smallPlayer), None)
    assert (playerobj != None)
    playerobj.setAction(action("RAISE", 0, smallBlind, smallBlind, 0, smallBlind), "PREGAME")
    # create BigBlind
    bigPlayer = logText.split(": posts big blind $")[0].split("\n")[-1]
    bigBlind = float(logText.split(": posts big blind $")[1].split("\n")[0])
    playerobj = next((x for x in players if x.name == bigPlayer), None)
    assert (playerobj != None)
    playerobj.setAction(action("RAISE", 0, bigBlind, bigBlind, smallBlind, bigBlind), "PREGAME")

    # analyze PreFlop
    if("*** FLOP ***" in logText):
        preFlopText = logText.split("*** HOLE CARDS ***")[1].split("\n*** FLOP ***")[0].split("]\n")[1]
        actualpot, completePot = analyzeSituation(preFlopText, players, "PREFLOP", 0, bigBlind, bigBlind)
    else:
        preFlopText = logText.split("*** HOLE CARDS ***")[1].split("\n*** SUMMARY ***")[0].split("]\n")[1]
        actualpot, completePot = analyzeSituation(preFlopText, players, "PREFLOP", 0, bigBlind, bigBlind)

    # analyze Flop
    if("*** FLOP ***" in logText and "*** TURN ***" in logText):
        flopText = logText.split("*** FLOP ***")[1].split("]\n")[1].split("\n*** TURN ***")[0]
        actualpot, completePot = analyzeSituation(flopText, players, "FLOP", actualpot, completePot, bigBlind)
    if("*** FLOP ***" in logText and not "*** TURN ***" in logText):
        flopText = logText.split("*** FLOP ***")[1].split("]\n")[1].split("\n*** SUMMARY ***")[0]
        actualpot, completePot = analyzeSituation(flopText, players, "FLOP", actualpot, completePot, bigBlind)

    # analyze TURN
    if("*** TURN ***" in logText and "*** RIVER ***" in logText):
        turnText = logText.split("*** TURN ***")[1].split("]\n")[1].split("\n*** RIVER ***")[0]
        actualpot, completePot = analyzeSituation(turnText, players, "TURN", actualpot, completePot, bigBlind)
    if("*** TURN ***" in logText and not "*** RIVER ***" in logText):
        turnText = logText.split("*** TURN ***")[1].split("]\n")[1].split("\n*** SHOW DOWN ***")[0]
        actualpot, completePot = analyzeSituation(turnText, players, "TURN", actualpot, completePot, bigBlind)
           
    # analyze RIVER
    if("*** RIVER ***" in logText and "*** SHOW DOWN ***" in logText):
        riverText = logText.split("*** RIVER ***")[1].split("]\n")[1].split("\n*** SHOW DOWN ***")[0]
        actualpot, completePot = analyzeSituation(riverText, players, "RIVER", actualpot, completePot, bigBlind)  
    if("*** RIVER ***" in logText and not "*** SHOW DOWN ***" in logText):
        riverText = logText.split("*** RIVER ***")[1].split("]\n")[1].split("\n*** SUMMARY ***")[0]
        actualpot, completePot = analyzeSituation(riverText, players, "RIVER", actualpot, completePot, bigBlind)

    # analyze FINISH
    playername = logText.split(" collected $")[0].split("\n")[-1]
    winner = next((x for x in players if x.name == playername), None)

    return game(gamenum, players, board, winner)

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