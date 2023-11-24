from numpy import *

#We create a character class to gather all the data extracted from the game
class character:
    def __init__(self,name,ID,ally,max_health,PV,armor,atk,PM,PA,position) -> None:
        self.name = name            #The name of the cbaracter
        self.ID = ID                #An ID to easily distinguish all characters
        self.ally = ally            #A boolean to divide character into allies and enemies
        self.max_health = max_health#The maximum value for PV
        self.PV = PV                #The health points of the character
        self.armor = armor          #The armor points of the character
        self.atk = atk              #The attack value of the character
        self.PA = PA
        self.PM = PM                #The movement point of the character
        self.position = position    #The position of the character on the board as a tuple (x,y)
        pass

#We create a board class to set a template for all our generated boards
class board:
    def __init__(self,board_ID,char_list,instruction_list,spell_list,score = 0) -> None:
        self.board_ID = board_ID                        #The unique ID of the board build on parents boards if any
        self.char_list = []                             #The list of all charcaters on board
        for i in range (len(char_list)):
            self.char_list.append(character(char_list[i].name,char_list[i].ID,char_list[i].ally,char_list[i].max_health,char_list[i].PV,char_list[i].armor,char_list[i].atk,char_list[i].PM,char_list[i].PA,char_list[i].position))
        self.instruction_list = instruction_list[:]     #The list of instructions required to reach the board
        self.score = score                              #The score of the board, calculated later
        self.spell_list = spell_list[:]                 #The spells available to the player, maximum of 7
        pass

class spell:
    def __init__(self,ID,name,cost,dmg,extra_effect):
        self.ID=ID
        self.name=name
        self.cost=cost
        self.dmg=dmg
        self.extra_effect=extra_effect

exemple = []

exemple.append(character("Arti Ficelle","0",True,391,391,120,35,3,6,(4,4)))
exemple.append(character("Tofu 1","1",False,120,120,0,30,3,0,(5,4)))
exemple.append(character("Tofu 2","2",False,110,110,0,32,3,0,(4,5)))

spells = []

spells.append(spell("0","Fulgur",3,14,("single_dmg_melee",4)))
spells.append(spell("1","Touche Enflammée",3,9,("square_dmg_heor_melee",5)))
spells.append(spell("2","Nouvelle vague",6,36,("None")))
spells.append(spell("3","Onde de choc",8,38,("cost_reduce_melee",8)))
spells.append(spell("4","Armure brutale",3,0,("dmg_equal_armor")))

test_board = board("0",exemple,[[]],spells,0)

#For debug purpose
def print_board(board):
    tab = [['/' for i in range (7)] for j in range (7)]
    for i in range(len(board)):
        if(board[i].ally):
            tab[board[i].position[0]][board[i].position[1]]="\033[92m" + board[i].ID + "\033[0m"
        else:
            tab[board[i].position[0]][board[i].position[1]]="\033[91m" + board[i].ID + "\033[0m"
    return tab

#???
def remplissage(character) :
    characters = character[7][7]
    for i in range(7):
        for j in range(7):
            characters[i][j] = character[i*j]

#This function test if a chosen cell is free to move on
def IsCellFree(wanted_cell,char_list,ID):
    available = True
    for i in range (len(char_list)):
        if(ID != char_list[i].ID):
            if(wanted_cell == char_list[i].position):
                available = False
    return available

#A function to calcul all available deplacements
def TheoricalMovment(starting_pos,char_list,mouvment,ID,n = 4):
    if (n != 0) :
        if(-1<starting_pos[0]<7 and -1<starting_pos[1]<7):
            if(IsCellFree(starting_pos,exemple,ID)):
                mouvment[starting_pos[0]][starting_pos[1]] = 1
                TheoricalMovment((starting_pos[0]+1,starting_pos[1]),char_list,mouvment,ID,n-1)
                TheoricalMovment((starting_pos[0]-1,starting_pos[1]),char_list,mouvment,ID,n-1)
                TheoricalMovment((starting_pos[0],starting_pos[1]+1),char_list,mouvment,ID,n-1)
                TheoricalMovment((starting_pos[0],starting_pos[1]-1),char_list,mouvment,ID,n-1)
            else:
                mouvment[starting_pos[0]][starting_pos[1]] = 2

#A function to know how many foes are in the melee keyword
def melee_count(position,char_list,ID):
    cpt = 0
    for i in range (len(char_list)):
        if (ID != char_list[i].ID):
            if (abs(char_list[i].position[0]-position[0])<=1) and (abs(char_list[i].position[1]-position[1])<=1):
                cpt +=1
    return cpt

def launch_simulation(previous_boards = [],n = 1):
    if(n>0):    
        all_boards = move_simulation(previous_boards[-1])
        all_boards = spell_simulation(all_boards)
        all_boards = foes_simulation(all_boards)
        for i in all_boards:
            i.score = score_calcul(i)
        previous_boards.append([all_boards])  
        launch_simulation(previous_boards,n-1)
    else:
        if(len(previous_boards)>0):
            best_board = previous_boards[0]
            for i in range (1,len(previous_boards)):
                if(previous_boards[i].score > best_board.score):
                    best_board = previous_boards[i]
            return best_board.instruction_list
        else:
            print("error, no board generated")

def score_calcul(board,newboard) :
    result = 0
    for i in range(board.len):
        if (board[i].ID == 0):
            if(newboard[i].PV <= 0):
                result = result-10000
            else:
                result = result - (board[i].PV - newboard[i].PV)
        else:
            if(newboard[i].PV <= 0):
                result = result + 2000 + newboard[i].atk
            else:
                result = result + 5*(board[i].PV - newboard[i].PV )
    return result

def foes_simulation(board,perso,mouvment):
    mainpos = perso[0].position
    for i in range(perso.len):
        if (i!=0):
            TheoricalMovment(perso[i].position,board,mouvment,n=perso[i].PM)
            if(mouvment[mainpos[0] + 1][mainpos[1]] == 1):
                board[mainpos[0] + 1][mainpos[1]] = board[perso[i].position[0]][perso[i].position[1]]
                board[perso[i].position[0]][perso[i].position[1]] = 0
                perso[0].PV = perso[0].PV-perso[i].atk

            elif(mouvment[mainpos[0]][mainpos[1]+1] == 1):
                board[mainpos[0]][mainpos[1]+1] = board[perso[i].position[0]][perso[i].position[1]]
                board[perso[i].position[0]][perso[i].position[1]] = 0
                perso[0].PV = perso[0].PV-perso[i].atk

            elif(mouvment[mainpos[0] - 1][mainpos[1]] == 1):
                board[mainpos[0] - 1][mainpos[1]] = board[perso[i].position[0]][perso[i].position[1]]
                board[perso[i].position[0]][perso[i].position[1]] = 0
                perso[0].PV = perso[0].PV-perso[i].atk

            elif(mouvment[mainpos[0] - 1][mainpos[1]] == 1):
                board[mainpos[0] - 1][mainpos[1]] = board[perso[i].position[0]][perso[i].position[1]]
                board[perso[i].position[0]][perso[i].position[1]] = 0
                perso[0].PV = perso[0].PV-perso[i].atk

def damage(char_list, damages, defender_ID):
    char_list[int(defender_ID)].armor = char_list[int(defender_ID)].armor - damages
    if(char_list[int(defender_ID)].armor <= 0):
        char_list[int(defender_ID)].PV = char_list[int(defender_ID)].PV + char_list[int(defender_ID)].armor
        char_list[int(defender_ID)].armor = 0
    
    if(char_list[int(defender_ID)].PV <= 0 ):
        char_list.pop(int(defender_ID))

def heal(char, value):
    char.PV += value
    if(char.PV>char.max_health):
        char.PV = char.max_health


def move_simulation(previous_boards):
    for i in range (len(previous_boards)):
        cpt = 1
        return_boards = []
        mouvment = [[0 for j in range (7)] for i in range(7)]
        TheoricalMovment(previous_boards[i].char_list[0].position,previous_boards[i].char_list,mouvment,"0")
        for x in range (7):
            for y in range (7):
                if(mouvment[x][y]==2):
                    if(mouvment[x-1][y] == 1):
                        return_boards.append(board(previous_boards[i].board_ID+"/"+str(cpt),previous_boards[i].char_list,previous_boards[i].instruction_list,previous_boards[i].spell_list))
                        return_boards[-1].instruction_list += [[2,(x-1,y),(x,y)]]
                        return_boards[-1].char_list[0].position = (x-1,y)
                        cpt+=1
                        for j in range (len(return_boards[-1].char_list)):
                            if(return_boards[-1].char_list[j].position == (x,y)):
                                damage(return_boards[-1].char_list,return_boards[-1].char_list[0].atk+(0.6*return_boards[-1].char_list[0].armor),return_boards[-1].char_list[j].ID)
                        
                    if(mouvment[x+1][y] == 1):
                        return_boards.append(board(previous_boards[i].board_ID+"/"+str(cpt),previous_boards[i].char_list,previous_boards[i].instruction_list,previous_boards[i].spell_list))
                        return_boards[-1].instruction_list += [[2,(x+1,y),(x,y)]]
                        return_boards[-1].char_list[0].position = (x+1,y)
                        cpt+=1
                        for j in range (len(return_boards[-1].char_list)):
                            if(return_boards[-1].char_list[j].position == (x,y)):
                                damage(return_boards[-1].char_list,return_boards[-1].char_list[0].atk+(0.6*return_boards[-1].char_list[0].armor),return_boards[-1].char_list[j].ID)
                    if(mouvment[x][y-1] == 1):
                        return_boards.append(board(previous_boards[i].board_ID+"/"+str(cpt),previous_boards[i].char_list,previous_boards[i].instruction_list,previous_boards[i].spell_list))
                        return_boards[-1].instruction_list += [[2,(x,y-1),(x,y)]]
                        return_boards[-1].char_list[0].position = (x,y-1)
                        cpt+=1
                        for j in range (len(return_boards[-1].char_list)):
                            if(return_boards[-1].char_list[j].position == (x,y)):
                                damage(return_boards[-1].char_list,return_boards[-1].char_list[0].atk+(0.6*return_boards[-1].char_list[0].armor),return_boards[-1].char_list[j].ID)
                    if(mouvment[x][y+1] == 1):
                        return_boards.append(board(previous_boards[i].board_ID+"/"+str(cpt),previous_boards[i].char_list,previous_boards[i].instruction_list,previous_boards[i].spell_list))
                        return_boards[-1].instruction_list += [[2,(x,y+1),(x,y)]]
                        return_boards[-1].char_list[0].position = (x,y+1)
                        cpt+=1
                        for j in range (len(return_boards[-1].char_list)):
                            if(return_boards[-1].char_list[j].position == (x,y)):
                                damage(return_boards[-1].char_list,return_boards[-1].char_list[0].atk+(0.6*return_boards[-1].char_list[0].armor),return_boards[-1].char_list[j].ID)

        if(len(return_boards) == 0):
            for x in range (7):
                for y in range (7):
                    if(mouvment[x][y]==1):
                        return_boards.append(board(previous_boards[i].board_ID+"/"+str(cpt),previous_boards[i].char_list,previous_boards[i].instruction_list,previous_boards[i].spell_list))
                        return_boards[-1].instruction_list += [[1,(x,y)]]
                        return_boards[-1].char_list[0].position = (x,y)
                        cpt+=1
                        
        return return_boards
    
def precast(board):
    for i in range(len(board.spell_list)):
        if(board.spell_list[i].extra_effect=="cost_reduce_melee"):
            board.spell_list[i].cost = board.spell_list[i].extra_effet[1]-melee_count(board.char_list[0].position,board.char_list,0)
            print(board.spell_list[i].cost)
        elif(board.spell_list[i].extra_effect=="dmg_equal_armor"):
            board.spell_list[i].dmg = board.char_list[0].armor

def cast_spell(board,target_ID,spell):
    board.char_list[0].PA -= spell.cost
    if (melee_count(board.char_list[0].position,board.char_list,0)>0) and (spell.extra_effect[0][-5:]=="melee"):
        if(spell.extra_effect[0] == "single_dmg_melee"):
            damage(board.char_list,spell.extra_effect[1]+spell.dmg,target_ID)
        else:
            if(spell.extra_effect[0] == "square_dmg_hero_melee"):
                for i in range (len (1,board.char_list)):
                    if(abs(board.char_list[i].position[0]-board.char_list[0].position[0])<=1) and (abs(board.char_list[i].position[1]-board.char_list[0].position[1])<=1):
                        damage(board.char_list,spell.extra_effect[1],i)
            elif(spell.extra_effect[0] == "heal_melee"):
                heal(board.char_list[0],spell.extra_effect[1])
            elif(spell.extra_effect[0] == "armor_melee"):
                board.char_list[0].armor += spell.extra_effect[1]
        #ne pas oublier de boost le sort de ces morts
    else:
         damage(board.char_list,spell.dmg,target_ID)
    
    board.char_list[0].PA -= spell.cost

def spell_simulation(current_boards):
    cpt = 1
    return_boards = []
    for i in range (len(current_boards)):
        precast(current_boards[i])
        for j in range (len(current_boards[i].spell_list)):
            if(current_boards[i].char_list[0].PA>=current_boards[i].spell_list[j].cost):
                for k in range (1,len(current_boards[i].char_list)):       
                    return_boards.append(board(current_boards[i].board_ID+"."+str(cpt),current_boards[i].char_list,current_boards[i].instruction_list,current_boards[i].spell_list))
                    return_boards[-1].instruction_list+=([[3,j,return_boards[-1].char_list[k].position]])
                    cast_spell(return_boards[-1],k,return_boards[-1].spell_list[j])
                    return_boards[-1].spell_list.pop(j)
                    for l in range (len(return_boards[-1].spell_list)):
                        if(return_boards[-1].char_list[0].PA>=return_boards[-1].spell_list[l].cost):
                            for m in range (1,len(current_boards[i].char_list)):       
                                return_boards.append(board(return_boards[-1].board_ID+"+"+str(cpt),return_boards[-1].char_list,return_boards[-1].instruction_list,return_boards[-1].spell_list))
                                return_boards[-1].instruction_list+=([[3,l,return_boards[-1].char_list[m].position]])
                                cast_spell(return_boards[-1],m,return_boards[-1].spell_list[l])
                                return_boards[-1].spell_list.pop(l)
    return return_boards
                



launch_simulation([[test_board]],1)