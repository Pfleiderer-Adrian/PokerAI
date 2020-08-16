import pandas as pd
import numpy as np
import re
import copy

höheBigblind = 100
höheSmallblind = 50
bigblind_pos = 1
smallblind_pos = 0

def parsePluribus(path_to_txt):
    op = open (path_to_txt, "r")
    data=op.read()
    splitdata = data.split("\n")
    return splitdata

def calculateSituation(spieler, spielername, situation_string, actualPot, isPreflop):
    i = 0
    j = 0
    ret = []
    # raise_amount Placeholder
    raise_amount = 0
    
    # special order for preflop
    spieler_temp = copy.deepcopy(spieler)
    singlepot = [0] * (len(spieler_temp)+1)
    if(isPreflop):
        caller = höheBigblind
        spieler_temp.remove(spieler_temp[0])
        spieler_temp.remove(spieler_temp[0])
        spieler_temp.append(spieler[0])
        spieler_temp.append(spieler[1])
        singlepot[len(spieler_temp)-1] = höheSmallblind
        singlepot[len(spieler_temp)-2] = höheBigblind
    else:
        singlepot = actualPot
        caller = singlepot[0]

    # When Pluribus is on last posistion and all enemys are gone the sourcelog are inconsistent. -> no Pluribus action recorded
    if((situation_string == "fffff") and (spieler_temp[-1] == spielername)):
        ret.append((0,1,0,0,150))
        return ret, spieler_temp, singlepot

    while i < len(situation_string):
        if(j >= len(spieler_temp)):
            j = 0
        if(situation_string[i] == "r"):
            k = i + 1
            raise_amount_string = ""
            while situation_string[k].isdigit():
                raise_amount_string = raise_amount_string + situation_string[k]
                k = k + 1
            raise_amount = int(raise_amount_string) - singlepot[j]
            if(spieler_temp[j] == spielername):
                ret.append((0,0,1, raise_amount, sum(singlepot)))
            caller = int(raise_amount_string)
            singlepot[j] = int(raise_amount_string)
            i =+ k-1
        if(situation_string[i] == "f"):
            raise_amount = caller - singlepot[j]
            if(spieler_temp[j] == spielername):
                ret.append((1,0,0, raise_amount, sum(singlepot)))
            singlepot[len(spieler_temp)] =+ singlepot[j]
            singlepot.pop(j)
            spieler_temp.remove(spieler_temp[j])
            j = j - 1
        if(situation_string[i] == "c"):
            raise_amount = caller - singlepot[j]
            singlepot[j] = caller
            if(spieler_temp[j] == spielername):
                ret.append((0,1,0, raise_amount, sum(singlepot)))
        j = j + 1
        i = i + 1

    #recreate correct order for after preflop
    if(isPreflop):
        tempcopy = copy.deepcopy(spieler)
        for x in spieler:
            if(x not in spieler_temp):
                tempcopy.remove(x)
        spieler_temp = tempcopy
    return ret, spieler_temp, singlepot


def getPluribusHands(data, name):
    ret = []
    for index, hand in enumerate(data):
        gameId = re.split(":", hand)[1]
        spielername = name
        chips = 10000

        dot_split = re.split(":", hand)
        spieler_string = dot_split[5]
        spieler = spieler_string.split("|")
        #spieler_pos fängt bei SmallBlind an mit 0 und zählt im Uhrzeigersinn
        spieler_pos = spieler.index(name)

        handkarten_string = dot_split[3]
        handkarten_alle = handkarten_string.split("|")
        handkarten = handkarten_alle[spieler_pos]
        handkarten = handkarten.split("/")[0]

        


        anzahlSpieler = len(spieler)
        
        # situations_string ist die Kombination aus Aktionen von Preflop bis River z.B: "r250ffffc/cc/cc/cr500f"
        situations_string = dot_split[2]

        #situations[0]: Preflop, situations[1]: Flop, situations[2]: Turn, situations[3]: River
        situations = re.split("/", situations_string)

        preflop, spieler_preflop, actualpot = calculateSituation(spieler, spielername, situations[0], 0, True)
        if(len(situations) > 1): 
            flop, spieler_flop, actualpot = calculateSituation(spieler_preflop, spielername, situations[1], actualpot, False)
        else:
            flop = []
        if(len(situations) > 2): 
           turn, spieler_turn, actualpot = calculateSituation(spieler_flop, spielername, situations[2], actualpot, False)
        else:
           turn = []
        if(len(situations) > 3): 
            river, spieler_river, actualpot = calculateSituation(spieler_turn, spielername, situations[3], actualpot, False)
        else:
           river = []
           
        chips_gewinn_verlust_string = dot_split[4]
        chips_gewinn_verlust = int(chips_gewinn_verlust_string.split("|")[spieler_pos])
        
        ret.append((gameId, spieler, chips, handkarten, spieler_pos, bigblind_pos, smallblind_pos, höheBigblind, höheSmallblind, anzahlSpieler, preflop, flop, turn, river, chips_gewinn_verlust))
        
    return ret

#PreflopSituation muss ausgelagert werden, weil... (?)
def calculatePreflopSituation(spieler, situation, spieler_pos):
    test = 1


allData = parsePluribus("./TestData/sample_game_117.log")
for (i, item) in enumerate(getPluribusHands(allData[4:-1], "Pluribus")):
    print(str(i)+": ", item[3], item[10],"\t\t\t", item[11], "\t\t\t ", item[12], "\t\t\t", item[13])
