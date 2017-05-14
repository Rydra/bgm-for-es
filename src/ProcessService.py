import os

class ProcessService:

    def findPid(self, processName):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.getProcessName(pid)
                if procname[:-1] == processName:
                    return pid
            except IOError:
                continue

        return -1

    def getProcessName(self, pid):
        return open(os.path.join('/proc', pid, 'comm'), 'rb').read()

    def processIsRunning(self, processName):
        return self.findPid(processName) != -1

    def processIsRunningByPid(self, pid):
        return os.path.exists("/proc/" + pid)

    def anyProcessIsRunning(self, processNames):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.getProcessName(pid)
                if procname[:-1] in processNames:
                    # print "Emulator found! " + procname + " Muting the music..."
                    return True

            except IOError:
                continue

        return False
