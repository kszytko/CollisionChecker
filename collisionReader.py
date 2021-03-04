from backupImporter import *

class CollisionReader:
    def __init__(self, backupImport, filesToLoad : list):
        self.robots = dict()  # Robots class
        self.backups = []    # Backup class
        self.collisionList = []
        self.stuckList = []

        # 1 Load files into backup class
        for file in filesToLoad:
            backup = backupImport(file)
            if backup.isLoaded:
                self.backups.append(backup)
                self.collisionList += backup.collisions

                # TODO co jeżeli robot już został załadowany?
                if backup.robotName not in self.robots:
                    self.robots[backup.robotName] = self.Robot(backup)
                else:
                    raise KeyError(backup.robotName, 'Robot duplicated!')

        self.robotsCount = len(self.robots)

        # 2 Check if r2 exists
        for robot in list(zip(*self.collisionList))[1]:
            if robot not in self.robots:
                raise ValueError('#E1', robot, 'not found!')

        # 3 Load collisions to class
        self.collisions = self.Collisions(self.collisionList)

        # 4 Main loop
        for robotName in self.robots:
            print('Start robot: ', robotName)
            self.collisions.restart()
            for robot in self.robots.values():
                robot.restart()

            if not self.robotCheck(robotName):
                stuck = []
                for robot in self.robots.values():
                    stuck.append((robot.name, robot.step))
                if stuck not in self.stuckList:
                    self.stuckList.append(stuck)

        # 5 Print stuck
        self.printStuck()

    def robotCheck(self, name: str):
        if name in self.robots:
            robot = self.robots[name]

            while not robot.finished:
                number, release = robot.getActualCollision()
                if release:
                    self.collisions.free(number, name)
                else:
                    if not self.collisions.take(number, name):  # zajmij jeżeli wolna
                        return False

                robot.move()
                self.robotCheck(self.collisions.nextRobot(number, name))
            return True
        else:
            #raise KeyError(name, 'not found.', self.robotCheck.__name__)
            print(name, 'not found.', self.robotCheck.__name__)
    # -----------------------------------
    def printStuck(self):
        for stuck in self.stuckList:
            print('----STUCK---')
            for i, robotName in enumerate(self.robots):
                self.robots[robotName].printStep(stuck[i])
            print()

    def printCollisions(self, dictionary: dict):
        t = PrettyTable()
        t.field_names = ('Coll', 'R1', 'R2')
        for key in dictionary:
            a = list(key)
            a.append(dictionary[key])
            t.add_row(a)
        print(t)

# ------------COLLISIONS CLASS ------------
    class Collisions:
        def __init__(self, dataList: list):
            self._robots = {(c, r1): r2 for c, r1, r2 in dataList}

            # TODO: Możliwość poprawienia tabeli kolizji
            # Check if collisions mirrored
            for c, r1, r2 in dataList:
                key = (c, r2)
                if key not in self._robots:
                    self._robots[key] = r1
                    print('#3', key, 'not exists! : Actual robot', r1, '. Key will be added.')
                elif self._robots[key] != r1:
                    print('#3', key, 'different! : Actual robot', r1, 'last robot', self._robots[key])

            self._status = dict.fromkeys(self._robots, True)

        def take(self, c, r) -> bool:
            self._validate(c, r)
            if self._status[c, r]:
                self._status[c, r] = self._status[c, self._robots[c, r]] = False
                return True
            return False

        def free(self, c, r):
            self._validate(c, r)
            self._status[c, r] = self._status[c, self._robots[c, r]] = True

        def check(self, c, r) -> bool:
            self._validate(c, r)
            return self._status[c, r]

        def restart(self):
            self._status = dict.fromkeys(self._status, True)

        def nextRobot(self, c, r):
            self._validate(c, r)
            return self._robots[c, r]

        def _validate(self, c, r):
            if (c, r) not in self._robots:
                raise KeyError('#E1', (c, r), 'not in status!')

# ------------ROBOT CLASS ------------
    class Robot:
        def __init__(self, backup: BackupImport):
            self._name = backup.robotName
            self._seq = backup.getSequences()[0]
            self._step = 0
            self._finished = False

        @property
        def step(self):
            return self._step

        @property
        def name(self):
            return self._name

        @property
        def finished(self):
            return self._finished

        def getActualCollision(self):
            return abs(self._seq[self._step]), self._seq[self._step] < 0

        def restart(self):
            self._step = 0
            self._finished = False

        def move(self):
            self._step += 1
            if self._step >= len(self._seq):
                self._finished = True

        def printStep(self, step=None):
            if not step: step = self._step
            print(self._name, *['[' + str(self._seq[i]) + ']' if i == step else ' ' + str(self._seq[i]) for i in range(len(self._seq))])
