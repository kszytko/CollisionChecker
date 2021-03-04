'''
    t_names = ['','RB1','RB2', 'RB3', 'RB4']
    t_colls = ['1 1 2','2 1 2','3 2 3', '1 3 4']
    t_sequences = ['','1 -1 2 -2','1 2 -1 -2 3 -3','3 -3 1 -1', '1 -1']
'''

import pprint

pp = pprint.PrettyPrinter()

collisionDict = {}
collisionsStatus = {}
robotList = []

def getImportedData():
    pass


def main():
    global collisionDict
    global collisionsStatus

    t_names = ['', 'RB1', 'RB2', 'RB3', 'R4', 'R5']
    # Collision definition:   coll_number robot1_id robot2_id
    t_colls = ['1 1 2', '2 2 3', '3 1 3', '1 4 5', '2 5 4', '123 1 5']
    t_sequences = ['', '1 3 -3 -1 123 -123', '2 1 -2 -1 1 -1', '3 2 -3 3 -3 -2', '1 2 -2 -1 2 1 -1 -2', '1 2 -1 -2']

# Load Collisions to dictionaty(r1,coll) = r2
    for i in range(len(t_colls)):
        coll, r1, r2 = map(int, t_colls[i].split())
        if (r1, coll) in coll_robots or (r2, coll) in coll_robots:
            print('Collision exists!')
        else:
            coll_robots[r1, coll] = r2
            coll_robots[r2, coll] = r1

# Reset status of collisions
    coll_status = coll_robots.copy()
    for key in coll_status:
        coll_status[key] = True

# Generate robots list
    for i in range(len(t_names)):
        name, seq = t_names[i], t_sequences[i]
        robotList.append(cRobot(i, name, seq))

    # pp.pprint(t_sequences)
    # pp.pprint(coll_robots)

#MAIN FUNCTION
    for robot in robotList:
        if robot.id == 0: continue
        restart()
        print('-' * 30)
        print('Start robot: ', robot.name)
        finished = checkRobot(robot)
        if finished:
            print('FINISHED!')
        else:
            print('STUCK:')
            printStuck()

# Check Robot ----------------
def checkRobot(robot):
    while not robot.finished:
        coll, release = robot.getActualCollision()
        if release:
            freeColl(robot.id, coll)
            robot.move()
        else:
            if takeColl(robot.id, coll):  # zajmij jeżeli wolna
                robot.move()
            else:
                return 0
        checkRobot(getRobot(robot.id, coll))
    return 1

# CLASS ---------------------
class ccRobot(object):
    def __init__(self, i, name, seq):
        self.id = i
        self.name = name
        self.seq = list(map(int, seq.split()))
        self.step = 0
        self.finished = False

    def getColl(self):
        return abs(self.seq[self.step]), self.seq[self.step] < 0

    def restart(self):
        self.step = 0
        self.finished = False

    def move(self):
        self.step += 1
        if self.step >= len(self.seq):
            self.finished = True

    def printStep(self):
        print(*['[' + str(self.seq[i]) + ']' if i == self.step else ' ' + str(self.seq[i]) for i in range(len(self.seq))])


# -----------------------------------
def printStuck():
    for robot in robotList:
        robot.printStep()

def checkColl(r, c):
    if (r, c) in collisionsStatus:
        return collisionsStatus[r, c]
    else:
        print('checkColl error', r, c)
        return 0

def restart():
    for robot in robotList:
        robot.restart()
    for key in collisionsStatus:
        collisionsStatus[key] = True


def takeColl(r, c):
    if checkColl(r, c):
        collisionsStatus[r, c] = collisionsStatus[collisionDict[r, c], c] = False  # Normal + mirror
        # print(r, 'takeColl', c)
        return 1
    else:
        return 0


def freeColl(r, c):
    if (r, c) in collisionsStatus:
        collisionsStatus[r, c] = collisionsStatus[collisionDict[r, c], c] = True  # Normal + mirror
    else:
        print(r, 'free coll error', c)


def getRobot(r, c):
    if (r, c) in collisionDict:
        return robotList[collisionDict[r, c]]


main()
