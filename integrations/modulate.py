"""Modulate Velma-2 API wrapper — placeholder for emotion detection."""
from __future__ import annotations
import httpx
from core.config import settings

MODULATE_BASE_URL = "https://api.modulate.ai/v1"


class ModulateClient:
    """Thin wrapper around Modulate Velma-2. Usage deferred to Phase 4."""

    def __init__(self) -> None:
        self._api_key = settings.modulate_api_key if hasattr(settings, "modulate_api_key") else ""
        self._headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def analyze_emotion(self, audio_bytes: bytes) -> dict:
        """Send audio to Velma-2 for emotion classification. Returns emotion label + confidence."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MODULATE_BASE_URL}/analyze",
                headers=self._headers,
                content=audio_bytes,
            )
            response.raise_for_status()
            return response.json()

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio to text via Velma-2."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MODULATE_BASE_URL}/transcribe",
                headers=self._headers,
                content=audio_bytes,
            )
            response.raise_for_status()
            return response.json().get("text", "")
