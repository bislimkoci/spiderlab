from __future__ import annotations

import os
import time


class LinuxSystemStats:
    def __init__(self) -> None:
        self.started_at = time.monotonic()
        self._last_cpu_total: int | None = None
        self._last_cpu_idle: int | None = None

    def snapshot(self) -> dict:
        memory = self._memory()
        return {
            "cpu_percent": self._cpu_percent(),
            "cpu_temp_c": self._cpu_temperature(),
            "memory": memory,
            "process": self._process(),
            "load_average": self._load_average(),
            "uptime_seconds": round(time.monotonic() - self.started_at),
        }

    def _cpu_percent(self) -> float | None:
        try:
            with open("/proc/stat", "r", encoding="utf-8") as stat_file:
                values = [int(value) for value in stat_file.readline().split()[1:]]
        except (OSError, ValueError):
            return None

        idle = values[3] + values[4]
        total = sum(values)

        if self._last_cpu_total is None or self._last_cpu_idle is None:
            self._last_cpu_total = total
            self._last_cpu_idle = idle
            return None

        total_delta = total - self._last_cpu_total
        idle_delta = idle - self._last_cpu_idle
        self._last_cpu_total = total
        self._last_cpu_idle = idle

        if total_delta <= 0:
            return None

        return round(100 * (1 - idle_delta / total_delta), 1)

    def _cpu_temperature(self) -> float | None:
        for path in (
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/devices/virtual/thermal/thermal_zone0/temp",
        ):
            try:
                with open(path, "r", encoding="utf-8") as temp_file:
                    return round(int(temp_file.read().strip()) / 1000, 1)
            except (OSError, ValueError):
                continue
        return None

    def _memory(self) -> dict:
        values: dict[str, int] = {}
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as meminfo:
                for line in meminfo:
                    key, raw_value = line.split(":", 1)
                    values[key] = int(raw_value.strip().split()[0]) * 1024
        except (OSError, ValueError):
            return {
                "total_mb": None,
                "used_mb": None,
                "available_mb": None,
                "percent": None,
            }

        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        if not total or available is None:
            return {
                "total_mb": None,
                "used_mb": None,
                "available_mb": None,
                "percent": None,
            }

        used = total - available
        return {
            "total_mb": round(total / 1024 / 1024),
            "used_mb": round(used / 1024 / 1024),
            "available_mb": round(available / 1024 / 1024),
            "percent": round(used / total * 100, 1),
        }

    def _process(self) -> dict:
        try:
            with open("/proc/self/statm", "r", encoding="utf-8") as statm:
                resident_pages = int(statm.readline().split()[1])
            page_size = os.sysconf("SC_PAGE_SIZE")
        except (OSError, ValueError):
            return {"rss_mb": None}

        return {"rss_mb": round(resident_pages * page_size / 1024 / 1024, 1)}

    def _load_average(self) -> dict:
        try:
            one, five, fifteen = os.getloadavg()
        except OSError:
            return {"one": None, "five": None, "fifteen": None}

        return {
            "one": round(one, 2),
            "five": round(five, 2),
            "fifteen": round(fifteen, 2),
        }
