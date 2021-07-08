import tkinter as tk
from collections import defaultdict
import operator
import pickle
import os.path


# Sorry, keine Funktionsbeschreibungen --> TO DO!
# (c) Zimmermann 10/2019

class kdb():
    learned = False
    x = []
    o = []
    end = False
    lock = False
    win = False

    @staticmethod
    def newWin():
        kdb.win = True

    @staticmethod
    def endTrue():
        kdb.end = True

    @staticmethod
    def addX(newX):
        kdb.x.append(newX)

    @staticmethod
    def addO(newO):
        kdb.o.append(newO)

    @staticmethod
    def setLock():
        kdb.lock = True

    @staticmethod
    def releaseLock():
        kdb.lock = False

    @staticmethod
    def newKnowledge():
        kdb.learned = True

    @staticmethod
    def newRound():
        kdb.learned = False
        kdb.x = []
        kdb.o = []
        kdb.end = False
        kdb.win = False


class counter():
    number = 0

    @staticmethod
    def next():
        counter.number += 1
        return counter.number

    @staticmethod
    def reset():
        counter.number = 0


class points():
    player = 0
    bot = 0
    lock = False

    @staticmethod
    def reset():
        points.bot = 0
        points.player = 0

    @staticmethod
    def botwin():
        if not points.lock:
            points.bot += 1
            print('Bot wins')
            points.lock = True

    @staticmethod
    def playerwin():
        if not points.lock:
            points.player += 1
            print('Player wins')
            points.lock = True

    @staticmethod
    def releaseLock():
        points.lock = False


class Button_Storage():

    def __init__(self, clicked, id, symbol, added):
        self.clicked = clicked
        self.id = id
        self.symbol = symbol
        self.added = added


class tic_button():
    clicked = False
    id = 0
    symbol = ''
    added = False

    def __init__(self, frame, row, column):
        self.btn = tk.Button(frame, command=self.btn_clicked)
        self.btn.grid(row=row, column=column)
        self.btn.config(height=5, width=10, font=('helvetica', 30, 'bold'))
        self.id = 2 ** counter.next()

    def btn_clicked(self):
        if not self.clicked:
            self.clicked = True
            if counter.next() % 2 is 0:
                self.btn.configure(text='x')
                self.symbol = 'x'
            else:
                self.btn.configure(text='o')
                self.symbol = 'o'

    def add(self):
        self.added = True

    def disable(self):
        self.btn.config(state='disabled')

    def enable(self):
        self.btn.config(state='active')

    def changeColor(self):
        self.btn.config(fg='green')

    def clear(self):
        self.btn.configure(text='', fg='black')
        self.symbol = ''
        self.clicked = False
        self.added = False


class findPosition():
    row = 0
    column = 0

    def findPos(self):
        self.pos = {'row': 0, 'column': 0}
        if self.row < 3 and self.column < 3:
            self.pos['row'] = self.row
            self.pos['column'] = self.column
            self.row += 1
        else:
            self.row = 0
            self.column += 1
            self.pos['row'] = self.row
            self.pos['column'] = self.column
            self.row += 1
        return self.pos


def getID(button):
    return button.id


def winners(buttons):
    for btn in buttons:
        btn.changeColor()
    main.update()


def getSum(buttons):
    sum = 0
    for button in buttons:
        sum += button.id
    return sum


def game():
    end = kdb.end
    if kdb.win is not True:
        for button in buttons:
            if button.clicked is True and button.added is not True:
                button.add()
                if button.symbol == 'x':
                    kdb.addX(button)
                else:
                    kdb.addO(button)
            if button.clicked is not True:
                button.clear()
        #################
        ocp = kdb.o[:]
        xcp = kdb.x[:]
        o = kdb.o[:]
        x = kdb.x[:]
        #################
        o.sort(key=getID, reverse=True)
        x.sort(key=getID, reverse=True)
        if len(o) >= 3 or len(x) >= 3:
            winner = findWinner(x, o)
            if winner is not None:
                kdb.newWin()
                if winner[0].symbol is 'x':
                    points.botwin()
                else:
                    points.playerwin()
                kdb.endTrue()
                end = kdb.end
                alreadyLearned = kdb.learned
                if alreadyLearned is not True:
                    addKnowledge(xcp, ocp, winner)
                    kdb.newKnowledge()
                winners(winner)
                # disableButtons()
            elif busyButtons() is True:
                kdb.endTrue()
                alreadyLearned = kdb.learned
                if alreadyLearned is not True:
                    if counter.number % 2 is not 0:
                        addKnowledgeTie(ocp, xcp)
                    else:
                        addKnowledgeTie(xcp, ocp)
                    kdb.newKnowledge()
        sum = getSum(ocp) + getSum(xcp)
        if counter.number % 2 is not 0 and end is not True and kdb.lock is not True:
            info.config(text='Computer\n Player ' + str(points.player) + ':' + str(points.bot) + ' Bot')
            next_button = findNextMove(sum, xcp, ocp)
            if next_button is not None:
                for button in buttons:
                    if button.id == next_button:
                        button.btn_clicked()
                        break
            elif end is not True and busyButtons() is not True:
                print("random guess")
                for button in buttons:
                    if button.clicked is not True:
                        button.btn_clicked()
                        break
        else:
            info.config(text='Your Turn \n Player ' + str(points.player) + ':' + str(points.bot) + ' Bot')

        if end is not True or busyButtons() is not True:
            main.after(200, func=game)


def disableButtons():
    for button in buttons:
        button.disable()


def enableButtons():
    for button in buttons:
        button.enable()


def busyButtons():
    for button in buttons:
        if button.symbol == '':
            return False
    return True


def addKnowledge(xcp, ocp, winner):
    if winner[0].symbol == 'x':
        knowledge.append((xcp, ocp))
    else:
        knowledge.append((ocp, xcp))
    blanko_knowledge = []
    for os, xs in knowledge:
        x_buttons = []
        o_buttons = []
        for o in os:
            one_button = [o.clicked, o.id, o.symbol, o.added]
            o_buttons.append(one_button)
        for x in xs:
            one_button = [x.clicked, x.id, x.symbol, x.added]
            x_buttons.append(one_button)

        blanko_knowledge.append((o_buttons, x_buttons))
        with open('kdbrain.pkl', 'wb') as brain:
            pickle.dump(blanko_knowledge, brain)
    print(f'Brain IQ length: {len(knowledge)}')


# clicked = False
#     id = 0
#     symbol = ''
#     added = False

def addKnowledgeTie(first, second):
    knowledge_tie.append((first, second))
    blanko_knowledge = []
    for os, xs in knowledge_tie:
        x_buttons = []
        o_buttons = []
        for o in os:
            one_button = [o.clicked, o.id, o.symbol, o.added]
            o_buttons.append(one_button)
        for x in xs:
            one_button = [x.clicked, x.id, x.symbol, x.added]
            x_buttons.append(one_button)

        blanko_knowledge.append((o_buttons, x_buttons))
        with open('kdbrain_tie.pkl', 'wb') as brain_tie:
            pickle.dump(blanko_knowledge, brain_tie)
    print(f'Brain [TIE] IQ length: {len(knowledge_tie)}')


def findNextMove(sum, current, player):
    pButtons = [2 ** i for i in range(1, 10)]
    pButtons.reverse()
    currentActive = []
    temp = sum
    if sum is not 0:
        for i in range(0, len(pButtons)):
            if pButtons[i] <= temp:
                temp -= pButtons[i]
                currentActive.append(pButtons[i])
                if temp is 0:
                    break
        prognose_win = 0
        for b in range(0, len(pButtons) - 1):
            if pButtons[b] not in currentActive:
                for button in buttons:
                    current2 = current[:]
                    if button.id == pButtons[b]:
                        current2.append(button)
                        current2.sort(key=getID, reverse=True)
                        isWinner = findWinner(current2, [])
                        if isWinner is not None:
                            prognose_win = button.id
                            break
        if prognose_win is not 0:
            print('win: ' + str(prognose_win))
            return prognose_win

    currentActive = []
    temp = sum
    if sum is not 0:
        for i in range(0, len(pButtons)):
            if pButtons[i] <= temp:
                temp -= pButtons[i]
                currentActive.append(pButtons[i])
                if temp is 0:
                    break
        prognose_block = 0
        for b in range(0, len(pButtons) - 1):
            if pButtons[b] not in currentActive:
                for button in buttons:
                    player2 = player[:]
                    if button.id == pButtons[b]:
                        player2.append(button)
                        player2.sort(key=getID, reverse=True)
                        isWinner = findWinner(player2, [])
                        if isWinner is not None:
                            prognose_block = button.id
                            break
        if prognose_block is not 0:
            print('block player win: ' + str(prognose_block))
            return prognose_block

    goodNumber = []
    for winners, losers in knowledge:
        wlength = len(winners)
        llength = len(losers)
        csum = 0
        if wlength == llength:
            # loser started
            for round in range(0, len(losers)):
                csum += losers[round].id
                if csum == sum:
                    goodNumber.append(winners[round].id)
                    break
                else:
                    csum += winners[round].id
        elif wlength > llength:
            if csum == sum:
                goodNumber.append(winners[0].id)
            else:
                csum += winners[0].id
                for round in range(0, len(losers)):
                    csum += losers[round].id
                    if csum == sum:
                        goodNumber.append(winners[round + 1].id)
                        break
                    else:
                        csum += winners[round + 1].id
    if len(goodNumber) is not 0:
        ddict = defaultdict(int)
        for number in goodNumber:
            ddict[number] = ddict[number] + 1
        ai = max(ddict.items(), key=operator.itemgetter(1))[0]
        print('OZ logic says: ' + str(ai) + ' (' + str(ddict[ai]) + ')')
        return ai

    tieNumber = []
    for first, second in knowledge_tie:
        wlength = len(first)
        llength = len(second)
        csum = 0
        if wlength > llength:
            csum += first[0].id
            for round in range(0, len(second)):
                if csum == sum:
                    tieNumber.append(second[round].id)
                    break
                csum += second[round].id
                if csum == sum:
                    tieNumber.append(first[round + 1].id)
                    break
                else:
                    csum += first[round + 1].id
    if len(tieNumber) is not 0:
        ddict = defaultdict(int)
        for number in tieNumber:
            ddict[number] = ddict[number] + 1
        ai = max(ddict.items(), key=operator.itemgetter(1))[0]
        print('OZ tie logic says: ' + str(ai) + ' (' + str(ddict[ai]) + ')')
        return ai


def findWinner(x, o):
    winner = [896, 584, 546, 292, 168, 146, 112, 14]
    winnero = False
    winnerx = False
    for winners in winner:
        if winnero:
            break
        owin = 0
        osum = getSum(o)
        if osum >= winners:
            osum -= winners
            owin = winners
            if osum is 0:
                winnero = True
            else:
                for os in o:
                    if os.id <= osum:
                        osum -= os.id;
                        if osum is 0:
                            winnero = True
    if winnero:
        winnerbuttons = winnerButtons(owin, o)
        return winnerbuttons

    for winners in winner:
        if winnerx:
            break
        xwin = 0
        xsum = getSum(x)
        if xsum >= winners:
            xsum -= winners
            xwin = winners
            if xsum is 0:
                winnerx = True
            else:
                for xs in x:
                    if xs.id <= xsum:
                        xsum -= xs.id;
                        if xsum is 0:
                            winnerx = True
    if winnerx:
        winnerbuttons = winnerButtons(xwin, x)
        return winnerbuttons
    else:
        return None


def winnerButtons(winsum, buttons):
    winners = []
    for button in buttons:
        if button.id <= winsum:
            winsum -= button.id;
            winners.append(button)
            if winsum is 0:
                return winners


def clearAll():
    for button in buttons:
        button.clear()
        main.update()
    points.releaseLock()
    kdb.newRound()
    kdb.setLock()
    main.update()
    game()
    kdb.releaseLock()
    # enableButtons()
    print("\nnew round\n*********************\n")


main = tk.Tk()
main.title('Tik Tak Toe')
frame = tk.Frame(main)
pos = findPosition()
positions = []
buttons = []
knowledge = []
knowledge_tie = []

try:
    with open('kdbrain.pkl', 'rb') as brain:
        b = pickle.load(brain)
        for os, xs in b:
            os_btn_list = []
            for o in os:
                # print(f'{o[0]}, {o[1]}, {o[2]}, {o[3]}')
                o_symbol = o[0]
                o_id = o[1]
                o_clicked = o[2]
                o_added = o[3]
                button = Button_Storage(o_clicked, o_id, o_symbol, o_added)
                os_btn_list.append(button)
            xs_btn_list = []
            for x in xs:
                x_symbol = x[0]
                x_id = x[1]
                x_clicked = x[2]
                x_added = x[3]
                button = Button_Storage(x_clicked, x_id, x_symbol, x_added)
                xs_btn_list.append(button)
            ox = (os_btn_list, xs_btn_list)
            knowledge.append(ox)
except:
    print('No brain.')


try:
    with open('kdbrain_tie.pkl', 'rb') as brain_tie:
        b = pickle.load(brain_tie)
        for os, xs in b:
            os_btn_list = []
            for o in os:
                o_symbol = o[0]
                o_id = o[1]
                o_clicked = o[2]
                o_added = o[3]
                button = Button_Storage(o_clicked, o_id, o_symbol, o_added)
                os_btn_list.append(button)
            xs_btn_list = []
            for x in xs:
                x_symbol = x[0]
                x_id = x[1]
                x_clicked = x[2]
                x_added = x[3]
                button = Button_Storage(x_clicked, x_id, x_symbol, x_added)
                xs_btn_list.append(button)
            ox = (os_btn_list, xs_btn_list)
            knowledge_tie.append(ox)
except:
    print('No tie brain.')

print(f'Brain (TIE and WIN Strategy) IQ Length: {len(knowledge) + len(knowledge_tie)}')

for i in range(0, 9):
    positions = pos.findPos()
    btn = tic_button(frame, positions.get('row'), positions.get('column'))
    buttons.append(btn)

exitbtn = btn = tk.Button(frame, text='Exit', command=main.destroy)
exitbtn.grid(row=3, column=0)
exitbtn.config(height=2, width=10, font=('helvetica', 20, 'bold'))

info = btn = tk.Button(frame, state='disabled')
info.grid(row=3, column=1)
info.config(height=2, width=15, font=('helvetica', 15, 'italic'))

clearbtn = btn = tk.Button(frame, text='New', command=clearAll)
clearbtn.grid(row=3, column=2)
clearbtn.config(height=2, width=10, font=('helvetica', 20, 'bold'))

main.minsize(main.winfo_width(), main.winfo_height())
main.update()
frame.pack()
main.after(500, func=game)
main.mainloop()
