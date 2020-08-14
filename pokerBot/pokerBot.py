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

def calculateSituation(spieler, spielername, situation_string, actualPot, isPreflop, player_put_in_pot, spieler_pos):
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
        
        if spieler_pos == 0:
            raise_amount = höheSmallblind
        elif spieler_pos == 1:
            raise_amount = 0
        else:
            raise_amount = höheBigblind
            
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
            #raise_amount gets corrected if player is in preflop phase
            if isPreflop:
                if j+2 == 0:
                    raise_amount = int(raise_amount_string) - raise_amount
                elif j+2 == 1:
                    raise_amount = int(raise_amount_string) - raise_amount
                elif len(ret) > 0:
                    raise_amount = int(raise_amount_string) - raise_amount
                else:
                    raise_amount = int(raise_amount_string)
            #TODO: turn and river show wrong raise_amounts
            else:
                raise_amount = int(raise_amount_string) - raise_amount - player_put_in_pot
                
            if(spieler_temp[j] == spielername):
                ret.append((0,0,1, raise_amount, sum(singlepot)))
            caller = int(raise_amount_string)
            singlepot[j] = int(raise_amount_string)
            i =+ k-1
        if(situation_string[i] == "f"):
            if(spieler_temp[j] == spielername):
                ret.append((1,0,0,raise_amount, sum(singlepot)))
            singlepot[len(spieler_temp)] =+ singlepot[j]
            singlepot.pop(j)
            spieler_temp.remove(spieler_temp[j])
            j = j - 1
        if(situation_string[i] == "c"):
            singlepot[j] = caller
            if(spieler_temp[j] == spielername):
                ret.append((0,1,0,raise_amount, sum(singlepot)))
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
        
        
        #reads out the boardcards
        boardcard_list = []
        flop_boardcards = ""
        turn_boardcards = ""
        river_boardcards = ""
        split_hand = hand.split("|")
        if len(split_hand[5].split("/")) > 1:
            boardcard_list = split_hand[5].split("/")[1:]
        if len(boardcard_list) == 1:
            flop_boardcards = boardcard_list[0].split(":")[0]
        if len(boardcard_list) == 2:
            flop_boardcards = boardcard_list[0]
            turn_boardcards = boardcard_list[1].split(":")[0]
        if len(boardcard_list) == 3:
            flop_boardcards = boardcard_list[0].split(":")[0]
            turn_boardcards = boardcard_list[1]
            river_boardcards = boardcard_list[2].split(":")[0]

        #for each hand the amount of chips that the player has already put into the pot starts with 0
        player_put_in_pot = 0

        dot_split = re.split(":", hand)
        spieler_string = dot_split[5]
        spieler = spieler_string.split("|")
        #spieler_pos starts with smallblind at 0 and counts clockwise
        spieler_pos = spieler.index(name)

        handkarten_string = dot_split[3]
        handkarten_alle = handkarten_string.split("|")
        handkarten = handkarten_alle[spieler_pos]
        handkarten = handkarten.split("/")[0]

        


        anzahlSpieler = len(spieler)
        
        # situations_string is the combination of actions from preflop to reiver e.g: "r250ffffc/cc/cc/cr500f"
        situations_string = dot_split[2]

        #situations[0]: Preflop, situations[1]: Flop, situations[2]: Turn, situations[3]: River
        situations = re.split("/", situations_string)

        preflop, spieler_preflop, actualpot = calculateSituation(spieler, spielername, situations[0], 0, True, 0, spieler_pos)
        if preflop:
            if preflop[-1]:
                player_put_in_pot = preflop[-1][-2]
                
        if(len(situations) > 1): 
            flop, spieler_flop, actualpot = calculateSituation(spieler_preflop, spielername, situations[1], actualpot, False, player_put_in_pot, spieler_pos)
            if flop:
                if flop[-1]:
                    player_put_in_pot = flop[-1][-2]
        else:
            flop = []
            
        if(len(situations) > 2): 
           turn, spieler_turn, actualpot = calculateSituation(spieler_flop, spielername, situations[2], actualpot, False, player_put_in_pot, spieler_pos)
           if turn:
               if turn[-1]:
                   player_put_in_pot = turn[-1][-2]
        else:
           turn = []
           
        if(len(situations) > 3): 
            river, spieler_river, actualpot = calculateSituation(spieler_turn, spielername, situations[3], actualpot, False, player_put_in_pot, spieler_pos)
        else:
           river = []
           
        chips_gewinn_verlust_string = dot_split[4]
        chips_gewinn_verlust = int(chips_gewinn_verlust_string.split("|")[spieler_pos])
        
        ret.append((gameId, spieler, chips, handkarten, spieler_pos, bigblind_pos, smallblind_pos, höheBigblind, höheSmallblind, anzahlSpieler, preflop, flop, turn, river, chips_gewinn_verlust, flop_boardcards, turn_boardcards, river_boardcards))
        
    return ret


allData = parsePluribus("./TestData/sample_game_117.log")
for (i, item) in enumerate(getPluribusHands(allData[4:-1], "Pluribus")):
    print(str(i)+": ", item[3], item[10],"\t\t\t", item[11], "\t\t\t ", item[12], "\t\t\t", item[13], item[15], item[16], item[17])
