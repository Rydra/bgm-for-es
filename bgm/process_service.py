import os
from typing import List, Union


class ProcessService:
    def find_pid(self, process_name: str) -> Union[str, int]:
        pids = [pid for pid in os.listdir("/proc") if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.get_process_name(pid)
                if procname[:-1] == process_name:
                    return pid
            except IOError:
                continue

        return -1

    def get_process_name(self, pid: str) -> bytes:
        return open(os.path.join("/proc", pid, "comm"), "rb").read()

    def process_is_running(self, process_name: str) -> bool:
        return self.find_pid(process_name) != -1

    def process_is_running_by_pid(self, pid: str) -> bool:
        return os.path.exists("/proc/" + pid)

    def any_process_is_running(self, process_names: List[str]) -> bool:
        pids = [pid for pid in os.listdir("/proc") if pid.isdigit()]
        for pid in pids:
            try:
                procname = self.get_process_name(pid)
                if procname[:-1] in process_names:
                    return True

            except IOError:
                continue

        return False
