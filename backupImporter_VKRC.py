from backupImporter import BackupImport
import re


# specifying the zip file name

class VKRCImport(BackupImport):
    def __init__(self, zipFilePath):
        super().__init__(zipFilePath)

    def isPathProgram(self, path):
        if re.match('\S+folgen\/folge(\d{1,2})\.src', path, re.I):
            return True
        return False

    # Return collision number to be set or free
    def readCollisionStep(self, line):
        data = re.match(b' +\$OUT\[(\d{2})\] = TRUE', line, re.I)
        if data:
            number = int(data[1])
            if 40 < number <= 56:
                return (number - 40) * -1
            elif 80 < number <= 96:
                return number - 80
        return None

    # Return collision number and robot
    def readCollisionInfo(self, line):
        data = re.match(b' +M_COMMENT[\s\S]+blokace +(\d+)[\s\S]+ (\d+R\d+)', line, re.I)
        if data:
            return int(data[1]), self.readRobotName(data[2].decode())
        return None, None

    # return patch to subprogram
    def readSubProgramPath(self, line):
        data = re.match(b' +SEL_RES=SELECT\(#UP,(\d+)', line, re.I)
        if data:
            return 'KRC/R1/UPs/UP' + data[1].decode() + '.src'
        return None

    @staticmethod
    def readRobotName(path):
        data = re.match('(.+|)(\d{4}r\d{2})', path, re.I)
        if data:
            return data[2].upper()
        else:
            return 'WrongRobotName'
