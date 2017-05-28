import os


class ProcessService:
    def __init__(self):
        pass

    def find_pid(self, process_name):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.get_process_name(pid)
                if procname[:-1] == process_name:
                    return pid
            except IOError:
                continue

        return -1

    def get_process_name(self, pid):
        return open(os.path.join('/proc', pid, 'comm'), 'rb').read()

    def process_is_running(self, processName):
        return self.find_pid(processName) != -1

    def process_is_running_by_pid(self, pid):
        return os.path.exists("/proc/" + pid)

    def any_process_is_running(self, process_names):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.get_process_name(pid)
                if procname[:-1] in process_names:
                    return True

            except IOError:
                continue

        return False
