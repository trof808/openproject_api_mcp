"""MCP Server for OpenProject integration."""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import OpenProjectClient
from .config import settings

# Initialize MCP server
server = Server("openproject-mcp")

# Global client instance
_client: OpenProjectClient | None = None


def get_client() -> OpenProjectClient:
    """Get or create OpenProject client."""
    global _client
    if _client is None:
        # Debug: log configuration
        import sys
        print(f"DEBUG: URL={settings.url}, API_KEY={settings.api_key[:10]}..." if settings.api_key else "DEBUG: API_KEY is empty!", file=sys.stderr)
        _client = OpenProjectClient()
    return _client


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_ai_tasks",
            description=(
                "Get list of tasks ready for AI development from OpenProject. "
                "Returns tasks from 'Баги' and 'Готово к разработке' columns "
                "that have ai_dev flag set to true. "
                "Each task includes: id, url, subject, description, type, status, priority, assignee."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_task",
            description=(
                "Get detailed information about a specific task by its ID. "
                "Returns full task details including description, status, assignee, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The work package (task) ID in OpenProject",
                    },
                },
                "required": ["task_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    client = get_client()

    if name == "get_ai_tasks":
        return await handle_get_ai_tasks(client)
    elif name == "get_task":
        task_id = arguments.get("task_id")
        if task_id is None:
            return [TextContent(type="text", text="Error: task_id is required")]
        return await handle_get_task(client, task_id)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_get_ai_tasks(client: OpenProjectClient) -> list[TextContent]:
    """Handle get_ai_tasks tool call."""
    try:
        tasks = await client.get_ai_ready_tasks()

        if not tasks:
            return [TextContent(
                type="text",
                text="No AI-ready tasks found in 'Баги' or 'Готово к разработке' columns.",
            )]

        # Format tasks for output
        formatted_tasks = [client.format_task_summary(task) for task in tasks]

        result = {
            "count": len(formatted_tasks),
            "tasks": formatted_tasks,
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching AI tasks: {str(e)}")]


async def handle_get_task(client: OpenProjectClient, task_id: int) -> list[TextContent]:
    """Handle get_task tool call."""
    try:
        task = await client.get_work_package(task_id)
        formatted = client.format_task_summary(task)

        return [TextContent(
            type="text",
            text=json.dumps(formatted, ensure_ascii=False, indent=2),
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching task {task_id}: {str(e)}")]


async def run_server() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()

