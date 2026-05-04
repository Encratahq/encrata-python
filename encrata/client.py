from __future__ import annotations

import json
from typing import Any, Sequence
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    InvalidRequestError,
    RateLimitError,
)
from .types import BreachReport, Person, Validation

__all__ = ["Encrata"]

_DEFAULT_BASE_URL = "https://api.encrata.com"

# Short field codes accepted by the API
FIELDS = {
    "name": "n",
    "email": "e",
    "company": "co",
    "role": "role",
    "industry": "ind",
    "location": "loc",
    "birthplace": "bloc",
    "current_location": "cloc",
    "bio": "bio",
    "age": "age",
    "gender": "g",
    "education": "edu",
    "phone": "ph",
    "photo": "pic",
    "validity": "v",
    "socials": "s",
    "breaches": "b",
    "registered_services": "reg",
    "news": "news",
    "publications": "pub",
}


class Encrata:
    """Encrata API client.

    Usage::

        from encrata import Encrata

        client = Encrata("enc_live_...")

        person = client.lookup("elon@tesla.com")
        print(person.name, person.company)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
    ) -> None:
        if not api_key:
            raise AuthenticationError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ── Public methods ────────────────────────────────

    def lookup(
        self,
        email: str,
        *,
        fields: Sequence[str] | None = None,
        nocache: bool = False,
    ) -> Person:
        """Look up a person by email address.

        Args:
            email: The email address to look up.
            fields: Optional list of fields to return. Use short codes
                    (``"n"``, ``"co"``) or long names (``"name"``, ``"company"``).
                    Omit to return all fields.
            nocache: If ``True``, bypass the cache and run a fresh lookup.

        Returns:
            A :class:`Person` with the enrichment results.

        Raises:
            InsufficientCreditsError: If the account has no credits.
            AuthenticationError: If the API key is invalid.
        """
        params = ""
        if fields:
            codes = [FIELDS.get(f, f) for f in fields]
            params += f"?fields={','.join(codes)}"
            if nocache:
                params += "&nocache=1"
        elif nocache:
            params += "?nocache=1"

        data = self._post(f"/api/agent/lookup{params}", {"e": email})
        return Person.from_dict(data)

    def validate(self, email: str) -> Validation:
        """Validate an email address (free — no credits used).

        Returns:
            A :class:`Validation` with ``validity`` (``"valid"``, ``"invalid"``,
            ``"disposable"``, or ``"unknown"``) and a human-readable ``message``.
        """
        data = self._post("/api/agent/validate", {"e": email})
        return Validation.from_dict(data)

    def breaches(self, email: str) -> BreachReport:
        """Check data breach exposure for an email (free — no credits used).

        Returns:
            A :class:`BreachReport` with breach count, affected services,
            and types of exposed data.
        """
        data = self._post("/api/agent/breaches", {"e": email})
        return BreachReport.from_dict(data)

    # ── Internals ─────────────────────────────────────

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        payload = json.dumps(body).encode()

        req = Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "encrata-python/0.1.0",
            },
            method="POST",
        )

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            body_bytes = e.read()
            try:
                err = json.loads(body_bytes)
            except (json.JSONDecodeError, ValueError):
                err = {}

            msg = err.get("m") or err.get("error") or e.reason
            code = e.code

            if code == 401:
                raise AuthenticationError(msg, status_code=code) from e
            if code == 402:
                raise InsufficientCreditsError(msg, status_code=code) from e
            if code == 400:
                raise InvalidRequestError(msg, status_code=code) from e
            if code == 429:
                raise RateLimitError(msg, status_code=code) from e
            raise APIError(msg, status_code=code) from e
        except URLError as e:
            raise APIConnectionError(f"Connection error: {e.reason}") from e
