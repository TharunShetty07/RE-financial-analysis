
"""
Prototype for isolating financial analysis data by client.

This is an in-process demonstration, not a production security boundary.
"""

from copy import deepcopy
from typing import Any


class ClientIsolationError(ValueError):
    """Raised when a client attempts to access another client's data."""


class ClientDataStore:
    """Store and retrieve separate in-memory datasets for fictional clients."""

    def __init__(self) -> None:
        self._client_data: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _validate_client_id(client_id: str) -> None:
        if not isinstance(client_id, str) or not client_id.strip():
            raise ClientIsolationError("A valid client ID is required.")

    def add_client(self, client_id: str, data: dict[str, Any]) -> None:
        """Register a client's dataset without overwriting an existing client."""
        self._validate_client_id(client_id)

        if client_id in self._client_data:
            raise ClientIsolationError(
                f"Client {client_id!r} is already registered."
            )

        if not isinstance(data, dict):
            raise ClientIsolationError("Client data must be a dictionary.")

        self._client_data[client_id] = deepcopy(data)

    def get_client_data(self, requesting_client_id: str,
                        target_client_id: str | None = None) -> dict[str, Any]:
        """
        Return data only when the requesting client matches the target.

        If no target is supplied, the requesting client's own data is returned.
        """
        self._validate_client_id(requesting_client_id)

        target = target_client_id or requesting_client_id
        self._validate_client_id(target)

        if requesting_client_id != target:
            raise ClientIsolationError(
                "Access denied: clients may only access their own data."
            )

        if target not in self._client_data:
            raise ClientIsolationError("Client not found.")

        # Return a copy so callers cannot mutate the stored dataset.
        return deepcopy(self._client_data[target])

    def client_count(self) -> int:
        """Return the number of registered clients."""
        return len(self._client_data)

    def list_client_ids(self) -> list[str]:
        """Return registered IDs for administrative testing only."""
        return sorted(self._client_data.keys())
