from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlatformAdapter(ABC):
    platform: str

    @abstractmethod
    def validate_credentials(self) -> tuple[bool, str]:
        raise NotImplementedError

    @abstractmethod
    def format_payload(self, variant: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def dry_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def handle_response(self, response: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
