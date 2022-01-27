from typing import List, Union

import psutil


class ProcessService:
    def find_pid(self, process_name: str) -> Union[str, int]:
        for process in psutil.process_iter():
            try:
                if process.name() == process_name:
                    return process.pid
            except OSError:
                continue

        return -1

    def process_is_running(self, process_name: str) -> bool:
        return self.find_pid(process_name) != -1

    def any_process_is_running(self, process_names: List[str]) -> bool:
        for process in psutil.process_iter():
            try:
                if process.name() in process_names:
                    return True
            except OSError:
                continue

        return False
