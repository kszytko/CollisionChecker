from zipfile import ZipFile
from prettytable import PrettyTable


# TODO: Walidacja zajmowanych i zwalnianych kolizji
class BackupImport:
    MAX_LEVEL = 4

    def __init__(self, path: str):
        # TODO: raise loaded error if not ok
        self._isLoaded = True

        self.zipFilePath = path
        self.zipFile = ZipFile(path, 'r')
        self.fileList = self.zipFile.namelist()

        self._collisions = []
        self._robotName = self.readRobotName(path)  # zipFilePath[-11:-4] #find in files for future
        self.sequences = []
        self.sequencesInfo = []
        self.sequencesInfoPath = []
        self.sequencesInfoTest = []

        self._readPrograms()

    @property
    def robotName(self) -> str:
        return self._robotName

    @property
    def isLoaded(self):
        return self._isLoaded

    @property
    def collisions(self) -> list:
        return self._collisions

    def getCollisionsDict(self):
        return {(c, r1): r2 for c, r1, r2 in self._collisions}

    def getSequences(self) -> list:
        return self.sequences

    def getSequencesInfo(self, number=None) -> list:
        if number:
            return self.sequencesInfo[number]
        else:
            return self.sequencesInfo

    def _readPrograms(self):
        for path in self.fileList:
            if self.isPathProgram(path):
                print(self._robotName, path)
                sequence = []
                sequenceInfo = []
                self._readProgram(path, sequence, sequenceInfo)

                if sequence and sequence not in self.sequences:
                    self.sequences.append(sequence)  # , sum(list(zip(*sequence))[0]) == 0])
                    self.sequencesInfo.append(sequenceInfo)
                    self.sequencesInfoPath.append(path)
                    self.sequencesInfoTest.append(sum(sequence))
                else:
                    pass

    def _readProgram(self, filePath, sequence, sequenceInfo, level=0):
        if level > self.MAX_LEVEL:
            return

        path = filePath
        if filePath not in self.fileList:
            for path in self.fileList:
                if path.upper() == filePath.upper():
                    break
                path = None

        if path:
            file = self.zipFile.open(path)
            for i, line in enumerate(file.readlines()):
                collStep = self.readCollisionStep(line)
                collNumber, collRobot = self.readCollisionInfo(line)
                subProgramPath = self.readSubProgramPath(line)

                if collStep:
                    sequence.append(collStep)
                    sequenceInfo.append([self._getProgramFromPath(filePath), i])

                if collNumber and collRobot:
                    collision = (collNumber, self.robotName, collRobot)
                    if collision not in self._collisions:
                        self._collisions.append(collision)

                if subProgramPath:
                    self._readProgram(subProgramPath, sequence, sequenceInfo, level + 1)

            file.close()
        else:
            print(filePath, 'Not in zipfile', self.__name__)

    def _getProgramFromPath(self, path):
        pos = path.rfind("/")
        return path[pos + 1:-4]

    # Return if path is program
    def isPathProgram(self, path):
        return False

    # Return collision number to be set or free
    def readCollisionStep(self, line):
        return None

    # Return collision number and robot
    def readCollisionInfo(self, line):
        return None, None

    # return patch to subprogram
    def readSubProgramPath(self, line):
        return None

    @staticmethod
    def readRobotName(path):
        return None

    def printSequenceInfo(self):
        for i in range(len(self.sequences)):
            t = PrettyTable()
            print(self.robotName + ' >> ' + self.sequencesInfoPath[i])
            t.add_column('Sequence', self.sequences[i])
            t.add_column('Info1', self.sequencesInfo[i])
            print(t)

        # for i in range(len(self.sequences)):
        #   pp.pprint(list(zip(self.sequences[i],self.sequencesInfo[i])))



def SetToDict(data):
    return {(c, r1): r2 for c, r1, r2 in data}
