import PokerStars_LogAnalyzer as analyzer

for x in analyzer.parseLogFile("./TestData/testLog.txt"):
    if(x.number == int(216384247999)):
        print("")
        print("---"+str(x.number)+"---")
        print(" Tablecards: ", x.tableCards)
        print("")
        for y in x.playerList:
            analyzer.printPlayerStats(y)
            print("")
        print("Winner: ", x.winner.name)
        print("----------------------------------------")
