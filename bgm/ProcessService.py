import os


class ProcessService:
    def __init__(self):
        pass

    def findPid(self, process_name):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.getProcessName(pid)
                if procname[:-1] == process_name:
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

    def anyProcessIsRunning(self, process_names):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.getProcessName(pid)
                if procname[:-1] in process_names:
                    return True

            except IOError:
                continue

        return False
