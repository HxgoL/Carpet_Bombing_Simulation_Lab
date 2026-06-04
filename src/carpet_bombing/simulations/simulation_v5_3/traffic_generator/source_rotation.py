import random
import time


class SourceRotator:
    """Rotate spoofed source IPs at a controlled interval."""

    def __init__(self, src_ips: list[str], rotation_interval: float):
        self.src_ips = src_ips
        self.rotation_interval = rotation_interval
        self.current_src = random.choice(src_ips)
        self.next_rotation = time.time() + rotation_interval

    def get(self) -> str:
        now = time.time()
        if self.rotation_interval > 0 and now >= self.next_rotation:
            self.current_src = random.choice(self.src_ips)
            self.next_rotation = now + self.rotation_interval
        return self.current_src
