import pandas as pd
import numpy as np
import re

höheBigblind = 100
höheSmallblind = 50
bigblind_pos = 1
smallblind_pos = 0


def parsePluribus(path_to_txt):
    op = open (path_to_txt, "r")
    data=op.read()
    splitdata = data.split("\n")
    return splitdata

def calculateSituation(spieler, spielername, situation_string, spieler_pos, player_put_in_pot):
    i = 0
    j = spieler_pos
    ret = []
    raise_amount = 0
    spieler_temp = spieler.copy()
    while i < len(situation_string):
        if(j >= len(spieler_temp)):
            j = 0
        if(situation_string[i] == "r"):
            k = i + 1
            raise_amount_string = ""
            while situation_string[k].isdigit():
                raise_amount_string = raise_amount_string + situation_string[k]
                k = k + 1
            raise_amount = int(raise_amount_string) - raise_amount - player_put_in_pot
            if(spieler_temp[j] == spielername):
                ret.append((0,0,1, raise_amount))
            j = j + 1
            if(j > len(spieler_temp)):
                j = 0
            i = k
            continue
        if(situation_string[i] == "f"):
            if(spieler_temp[j] == spielername):
                ret.append((1,0,0,raise_amount))
            spieler_temp.remove(spieler_temp[j])
            j = j - 1
        if(situation_string[i] == "c"):
            if(spieler_temp[j] == spielername):
                ret.append((0,1,0,raise_amount))
        j = j + 1
        i = i + 1
    return ret, spieler_temp


def getPluribusHands(data, name):
    ret = []
    for index, hand in enumerate(data):
        gameId = re.split(":", hand)[1]
        spielername = name
        chips = 10000
        
        player_put_in_pot = 0

        dot_split = re.split(":", hand)
        spieler_string = dot_split[5]
        spieler = spieler_string.split("|")
        #spieler_pos fängt bei SmallBlind an mit 0 und zählt im Uhrzeigersinn
        spieler_pos = spieler.index(name)

        """
        Problem: Handkarten, bei denen der Spieler an Position 5 Sitzt und mindestens der Flop aufgedeckt wird,
        werden die Handkarten falsch erkannt (Der Spieler bekommt auch die Boardkarten mit als Handkarten eingetragen).
        """
        handkarten_string = dot_split[3]
        handkarten_alle = handkarten_string.split("|")
        handkarten = handkarten_alle[spieler_pos]
        handkarten = handkarten.split("/")[0]


        anzahlSpieler = len(spieler)
        
        # situations_string ist die Kombination aus Aktionen von Preflop bis River z.B: "r250ffffc/cc/cc/cr500f"
        situations_string = dot_split[2]

        #situations[0]: Preflop, situations[1]: Flop, situations[2]: Turn, situations[3]: River
        situations = re.split("/", situations_string)

        preflop, spieler_preflop = calculatePreflopSituation(spieler, spielername, situations[0], spieler_pos)
        
        #TODO: multiple betting in one round is not taken into account yet
        if preflop:
            if preflop[-1]:
                player_put_in_pot = preflop[-1][-1]
                
        #TODO: multiple betting in one round is not taken into account yet        
        if(len(situations) > 1): 
            flop, spieler_flop = calculateSituation(spieler_preflop, spielername, situations[1], 0, player_put_in_pot)
            if flop:
                if flop[-1]:
                    player_put_in_pot = flop[-1][-1]
        else:
            flop = []
            
        #TODO: multiple betting in one round is not taken into account yet    
        if(len(situations) > 2): 
           turn, spieler_turn = calculateSituation(spieler_flop, spielername, situations[2], 0, player_put_in_pot)
           if turn:
               if turn[-1]:
                   player_put_in_pot = turn[-1][-1]
        else:
           turn = []
           
        if(len(situations) > 3): 
            river, spieler_river = calculateSituation(spieler_turn, spielername, situations[3], 0, player_put_in_pot)
        else:
           river = []
           
        chips_gewinn_verlust_string = dot_split[4]
        chips_gewinn_verlust = int(chips_gewinn_verlust_string.split("|")[spieler_pos])
        
        ret.append((gameId, spieler, chips, handkarten, spieler_pos, bigblind_pos, smallblind_pos, höheBigblind, höheSmallblind, anzahlSpieler, preflop, flop, turn, river, chips_gewinn_verlust))
        
    return ret


#Seperate preflop calculation to get the right raise amounts concerning the big- and smallblind
def calculatePreflopSituation(spieler, spielername, situation_string, spieler_pos):
    i = 0
    #position starts with 2 instead of 0 because UTG starts the preflop betting round
    position = 2
    ret = []
    
    if spieler_pos == 0:
        raise_amount = höheSmallblind
    elif spieler_pos == 1:
        raise_amount = 0
    else:
        raise_amount = höheBigblind
        
    spieler_temp = spieler.copy()
    while i < len(situation_string):
        if(position >= len(spieler_temp)):
            position = 0
        if(situation_string[i] == "r"):
            k = i + 1
            raise_amount_string = ""
            while situation_string[k].isdigit():
                raise_amount_string = raise_amount_string + situation_string[k]
                k = k + 1
            if position == 0:
                raise_amount = int(raise_amount_string) - höheSmallblind
            elif position == 1:
                raise_amount = int(raise_amount_string) - höheBigblind
            else:
                raise_amount = int(raise_amount_string)
                
            if(spieler_temp[position] == spielername):
                ret.append((0,0,1, raise_amount))
            position = position + 1
            if(position > len(spieler_temp)):
                position = 0
            i = k
            continue
        if(situation_string[i] == "f"):
            if(spieler_temp[position] == spielername):
                ret.append((1,0,0,raise_amount))
            spieler_temp.remove(spieler_temp[position])
            position = position - 1
        if(situation_string[i] == "c"):
            if(spieler_temp[position] == spielername):
                ret.append((0,1,0,raise_amount))
        position = position + 1
        i = i + 1
    return ret, spieler_temp


allData = parsePluribus("./TestData/sample_game_117.log")
for (i, item) in enumerate(getPluribusHands(allData[4:-1], "Pluribus")):
    print(str(i)+": ", item[3], item[4], item[10],"\t\t\t", item[11], "\t\t\t ", item[12], "\t\t\t", item[13])