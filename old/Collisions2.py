from backupImporter_VKRC import ImportVKRC
from backupImporter import *
import tkinter as tk
from tkinter import filedialog

import pprint

pp = pprint.PrettyPrinter()

collisionDict = {}
collisionsStatus = {}
robotList = dict()


def main(ImportData: ImportType):
    global collisionDict
    global collisionsStatus
    global robotList


    root = tk.Tk()
    root.withdraw()

    files = filedialog.askopenfilenames(initialdir="/", title="Select file",
                                        filetypes=(("zip files", "*.zip"), ("all files", "*.*")))

    impRobotList = []
    collisionSet = set()

    for file in files:
        importedRobot = ImportData(file)
        if importedRobot:
            impRobotList.append(importedRobot)
            collisionSet.update(importedRobot.getCollisions())
            collisionDict.update(importedRobot.getCollisionsDict())

            # TODO co jeżeli robot już został załadowany?
            robotList[importedRobot.name] = cRobot(importedRobot)

    printCollisions(collisionDict)

    # Check if secound robots exists
    for collision, mainRobot, nextRobot in collisionSet:
        if nextRobot not in robotList:
            print('#2', nextRobot, 'not found!, Check the data in robot: ', mainRobot, 'collision: ', collision)

    # TODO: Możliwość poprawienia tabeli kolizji
    # Check if collisions mirrored
    for collision, mainRobot, nextRobot in collisionSet:
        key = (collision, nextRobot)
        if key not in collisionDict:
            collisionDict[key] = mainRobot
            print('#3', key, 'not exists! : Actual robot', mainRobot, '. Key will be added.')
        elif collisionDict[key] != mainRobot:
            print('#3', key, 'different! : Actual robot', mainRobot, 'last robot', collisionDict[key])

    printCollisions(collisionDict)
    # return

    # Reset status of collisions
    collisionsStatus = collisionDict.copy()
    for key in collisionsStatus:
        collisionsStatus[key] = True

    # MAIN FUNCTION
    stuckList = []
    for robotName in robotList:
        restart()
        print('-' * 30)
        print('Start robot: ', robotName)
        finished = checkRobot(robotName)
        if finished:
            print('FINISHED!')
        else:
            print('STUCK:')
            stuck = saveStuck()
            if stuck not in stuckList:
                stuckList.append(stuck)

    for stuck in stuckList:
        print('----STUCK---')
        for i, robotName in enumerate(robotList):
            robotList[robotName].printStep(stuck[i])
        print()

# CLASS ---------------------
class cRobot(object):
    def __init__(self, impRobot: ImportVKRC):
        self._name = impRobot.name
        self.seq = impRobot.getSequences()[0]
        self._step = 0
        self.finished = False

    @property
    def step(self):
        return self._step

    @property
    def name(self):
        return self._name

    def getActualCollision(self):
        return abs(self.seq[self._step]), self.seq[self._step] < 0

    def restart(self):
        self._step = 0
        self.finished = False

    def move(self):
        self._step += 1
        if self._step >= len(self.seq):
            self.finished = True

    def printActualStep(self):
        print(self._name, self.finished,
              *['[' + str(self.seq[i]) + ']' if i == self._step else ' ' + str(self.seq[i]) for i in
                range(len(self.seq))])

    def printStep(self, stepNum):
        print(self._name, self.finished,
              *['[' + str(self.seq[i]) + ']' if i == stepNum else ' ' + str(self.seq[i]) for i in range(len(self.seq))])




# Check Robot ----------------
def checkRobot(robotName: str):
    if robotName in robotList:
        robot = robotList[robotName]
        while not robot.finished:
            collision, release = robot.getActualCollision()
            if release:
                freeColl(collision, robotName)
                robot.move()
            else:
                if takeColl(collision, robotName):  # zajmij jeżeli wolna
                    robot.move()
                else:
                    return 0
            checkRobot(getCollidedRobot(collision, robotName))
        return True
    else:
        print(robotName, 'not found.', checkRobot.__name__)


# -----------------------------------
def printStuck():
    for robot in robotList.values():
        robot.printStep()


def saveStuck():
    stuck = []
    for robotName, robot in robotList.items():
        stuck.append(robot.step)
    return stuck


def restart():
    for robot in robotList.values():
        robot.restart()
    for key in collisionsStatus:
        collisionsStatus[key] = True


def checkColl(c, r):
    if (c, r) in collisionsStatus:
        return collisionsStatus[c, r]
    else:
        print('checkColl error', c, r)
        return 0


def takeColl(c, r):
    if checkColl(c, r):
        collisionsStatus[c, r] = collisionsStatus[c, collisionDict[c, r]] = False  # Normal + mirror
        # print(r, 'takeColl', c)
        return 1
    else:
        return 0


def freeColl(c, r):
    if (c, r) in collisionsStatus:
        collisionsStatus[c, r] = collisionsStatus[c, collisionDict[c, r]] = True  # Normal + mirror
    else:
        print('#4 Coll:', c, r, 'not found in collision status!')


def getRobot(robotName):
    return robotList[robotName]


def getCollidedRobot(c, r):
    if (c, r) in collisionDict:
        return collisionDict[c, r]


def printCollisions(dictionary: dict):
    t = PrettyTable()
    t.field_names = ('Coll', 'R1', 'R2')
    for key in dictionary:
        a = list(key)
        a.append(dictionary[key])
        t.add_row(a)
    print(t)

if __name__ == '__main__':
    main(ImportVKRC)

