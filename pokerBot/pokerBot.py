import pandas as pd
import numpy as np
import re

def parsePluribus(path_to_txt):
    op = open (path_to_txt, "r")
    data=op.read()
    splitdata = data.split("\n")
    return splitdata

def calculateSituation(spieler, spielername, situation_string, spieler_pos, bigblind):
    i = 0
    j = spieler_pos
    ret = []
    rase_amount = bigblind
    spieler_temp = spieler.copy()
    while i < len(situation_string):
        if(j >= len(spieler_temp)):
            j = 0
        if(situation_string[i] == "r"):
            k = i + 1
            rase_amount_string = ""
            while situation_string[k].isdigit():
                rase_amount_string = rase_amount_string + situation_string[k]
                k = k + 1
            rase_amount = int(rase_amount_string) - rase_amount 
            if(spieler_temp[j] == spielername):
                ret.append((0,0,1, rase_amount))
            j = j + 1
            if(j > len(spieler_temp)):
                j = 0
            i = k
            continue
        if(situation_string[i] == "f"):
            if(spieler_temp[j] == spielername):
                ret.append((1,0,0,rase_amount))
            spieler_temp.remove(spieler_temp[j])
            j = j - 1
        if(situation_string[i] == "c"):
            if(spieler_temp[j] == spielername):
                ret.append((0,1,0,rase_amount))
        j = j + 1
        i = i + 1
    return ret, spieler_temp


def getPluribusHands(data, name):
    ret = []
    for index, hand in enumerate(data):
        gameId = re.split(":", hand)[1]
        spielername = name
        chips = 10000

        dot_split = re.split(":", hand)

        spieler_string = dot_split[5]
        spieler = spieler_string.split("|")
        spieler_pos = spieler.index(name)

        handkarten_string = dot_split[3]
        handkarten_alle = handkarten_string.split("|")
        handkarten = handkarten_alle[spieler_pos]

        bigblind_pos = 1
        smallblind_pos = 0

        höheBigblind = 100
        höheSmallblind = 50

        anzahlSpieler = len(spieler)
        
        situations_string = dot_split[2]

        situations = re.split("/", situations_string)

        preflop, spieler_preflop = calculateSituation(spieler, spielername, situations[0], 2, 100)
        if(len(situations) > 1): 
            flop, spieler_flop = calculateSituation(spieler_preflop, spielername, situations[1], 0, 100)
        else:
            flop = []
        if(len(situations) > 2): 
           turn, spieler_turn = calculateSituation(spieler_flop, spielername, situations[2], 0, 100)
        else:
           turn = []
        if(len(situations) > 3): 
            river, spieler_river = calculateSituation(spieler_turn, spielername, situations[3], 0, 100)
        else:
           river = []
           
        chips_gewinn_verlust_string = dot_split[4]
        chips_gewinn_verlust = int(chips_gewinn_verlust_string.split("|")[spieler_pos])
        
        ret.append((gameId, spieler, chips, handkarten, spieler_pos, bigblind_pos, smallblind_pos, höheBigblind, höheSmallblind, anzahlSpieler, preflop, flop, turn, river, chips_gewinn_verlust))
        
    return ret

allData = parsePluribus("./TestData/sample_game_117.log")
for (i, item) in enumerate(getPluribusHands(allData[4:-2], "Pluribus")):
    print(str(i)+": ", item[10],"\t\t\t", item[11], "\t\t\t ", item[12], "\t\t\t", item[13])

