"""Tiny path router with ``{param}`` segments."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass
class Route:
    method: str
    pattern: str
    handler: Callable
    regex: re.Pattern


class Router:
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add(self, method: str, pattern: str, handler: Callable) -> None:
        regex = re.compile("^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", pattern) + "$")
        self.routes.append(Route(method.upper(), pattern, handler, regex))

    def match(self, method: str, path: str) -> tuple[Callable | None, dict, bool]:
        """Return (handler, params, path_exists)."""
        path_exists = False
        for route in self.routes:
            found = route.regex.match(path)
            if not found:
                continue
            path_exists = True
            if route.method == method.upper():
                return route.handler, found.groupdict(), True
        return None, {}, path_exists
