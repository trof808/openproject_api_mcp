"""OpenProject API Client."""

import json
from typing import Any
from urllib.parse import quote

import httpx

from .config import settings


class OpenProjectClient:
    """Client for OpenProject API v3."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.base_url = (base_url or settings.url).rstrip("/")
        self.api_key = api_key or settings.api_key
        self._client: httpx.AsyncClient | None = None

    @property
    def auth(self) -> tuple[str, str]:
        """Basic auth tuple for OpenProject API."""
        return ("apikey", self.api_key)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                auth=self.auth,
                headers={"Accept": "application/hal+json"},
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make API request."""
        client = await self._get_client()
        response = await client.request(method, f"/api/v3{path}", **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_query_order(self, query_id: int) -> list[str]:
        """Get work package IDs from a query's order.

        Returns list of work package IDs that belong to this query (board column).
        """
        data = await self._request("GET", f"/queries/{query_id}/order")
        return list(data.keys())

    async def get_work_packages(
        self,
        ids: list[str] | None = None,
        ai_dev_only: bool = False,
        filters: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Get work packages with optional filters.

        Args:
            ids: Filter by specific work package IDs
            ai_dev_only: Filter only tasks with ai_dev = true
            filters: Additional custom filters

        Returns:
            List of work package objects
        """
        query_filters = filters or []

        if ids:
            query_filters.append({
                "id": {"operator": "=", "values": ids}
            })

        if ai_dev_only:
            query_filters.append({
                settings.ai_dev_field: {"operator": "=", "values": ["t"]}
            })

        params = {}
        if query_filters:
            params["filters"] = json.dumps(query_filters)

        data = await self._request("GET", "/work_packages", params=params)
        return data.get("_embedded", {}).get("elements", [])

    async def get_work_package(self, work_package_id: int) -> dict[str, Any]:
        """Get a single work package by ID.

        Args:
            work_package_id: The work package ID

        Returns:
            Work package object with full details
        """
        return await self._request("GET", f"/work_packages/{work_package_id}")

    async def get_ai_ready_tasks(self) -> list[dict[str, Any]]:
        """Get tasks ready for AI development.

        Fetches tasks from "Баги" and "Готово к разработке" columns
        that have ai_dev = true.

        Returns:
            List of work packages ready for AI development
        """
        # Step 1: Get task IDs from both columns
        bugs_ids = await self.get_query_order(settings.query_id_bugs)
        ready_ids = await self.get_query_order(settings.query_id_ready)

        # Combine IDs from both columns
        all_ids = list(set(bugs_ids + ready_ids))

        if not all_ids:
            return []

        # Step 2: Filter by IDs and ai_dev = true
        return await self.get_work_packages(ids=all_ids, ai_dev_only=True)

    def get_task_url(self, work_package_id: int) -> str:
        """Get web URL for a work package."""
        return f"{self.base_url}/work_packages/{work_package_id}"

    def format_task_summary(self, wp: dict[str, Any]) -> dict[str, Any]:
        """Format work package into a summary dict.

        Args:
            wp: Work package object from API

        Returns:
            Simplified task summary with id, url, subject, description
        """
        wp_id = wp.get("id")
        return {
            "id": wp_id,
            "url": self.get_task_url(wp_id),
            "subject": wp.get("subject", ""),
            "description": wp.get("description", {}).get("raw", "") if wp.get("description") else "",
            "type": wp.get("_links", {}).get("type", {}).get("title", ""),
            "status": wp.get("_links", {}).get("status", {}).get("title", ""),
            "priority": wp.get("_links", {}).get("priority", {}).get("title", ""),
            "assignee": wp.get("_links", {}).get("assignee", {}).get("title", ""),
        }

