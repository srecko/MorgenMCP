"""MCP tools for Morgen task operations."""

from typing import Any

from fastmcp.exceptions import ToolError

from morgenmcp.client import get_client
from morgenmcp.tools.utils import filter_none_values, handle_tool_errors


def _format_task(task: dict) -> dict:
    """Format a task object, filtering out null values."""
    return filter_none_values(
        {
            "id": task.get("id"),
            "title": task.get("title"),
            "description": task.get("description"),
            "taskListId": task.get("taskListId"),
            "due": task.get("due"),
            "timeZone": task.get("timeZone"),
            "estimatedDuration": task.get("estimatedDuration"),
            "priority": task.get("priority"),
            "progress": task.get("progress"),
            "position": task.get("position"),
            "tags": task.get("tags"),
            "relatedTo": task.get("relatedTo"),
            "created": task.get("created"),
            "updated": task.get("updated"),
        }
    )


@handle_tool_errors
async def list_tasks(
    limit: int | None = None,
    updated_after: str | None = None,
) -> dict:
    """List Morgen tasks, optionally filtered by update time."""
    client = get_client()
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if updated_after is not None:
        params["updatedAfter"] = updated_after
    response = await client.client.get("/tasks/list", params=params)
    client._handle_error(response)
    data = response.json()
    tasks = data.get("data", {}).get("tasks", [])
    return {"tasks": [_format_task(t) for t in tasks], "count": len(tasks)}


@handle_tool_errors
async def get_task(task_id: str) -> dict:
    """Retrieve a single task by its Morgen ID."""
    client = get_client()
    response = await client.client.get("/tasks", params={"id": task_id})
    client._handle_error(response)
    data = response.json()
    task = data.get("data", {}).get("task", {})
    return {"task": _format_task(task)}


@handle_tool_errors
async def create_task(
    title: str,
    description: str | None = None,
    due: str | None = None,
    time_zone: str | None = None,
    estimated_duration: str | None = None,
    task_list_id: str | None = None,
    priority: int | None = None,
    progress: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Create a new task in Morgen."""
    if not title:
        raise ToolError("Task title must be at least 1 character.")
    if priority is not None and not (0 <= priority <= 9):
        raise ToolError("Priority must be between 0 and 9.")
    if due is not None and len(due) != 19:
        raise ToolError("Due date must be exactly 19 chars: YYYY-MM-DDTHH:mm:ss")
    body = filter_none_values({"title": title, "description": description, "due": due,
        "timeZone": time_zone, "estimatedDuration": estimated_duration,
        "taskListId": task_list_id, "priority": priority, "progress": progress, "tags": tags})
    client = get_client()
    response = await client.client.post("/tasks/create", json=body)
    client._handle_error(response)
    task_id = response.json().get("data", {}).get("id")
    return {"success": True, "message": "Task created successfully.", "id": task_id}


@handle_tool_errors
async def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    due: str | None = None,
    time_zone: str | None = None,
    task_list_id: str | None = None,
    priority: int | None = None,
    progress: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Update an existing task. Only the fields you provide will be changed."""
    if priority is not None and not (0 <= priority <= 9):
        raise ToolError("Priority must be between 0 and 9.")
    if due is not None and len(due) != 19:
        raise ToolError("Due date must be exactly 19 chars: YYYY-MM-DDTHH:mm:ss")
    body = filter_none_values({"id": task_id, "title": title, "description": description,
        "due": due, "timeZone": time_zone, "taskListId": task_list_id,
        "priority": priority, "progress": progress, "tags": tags})
    client = get_client()
    response = await client.client.post("/tasks/update", json=body)
    client._handle_error(response)
    return {"success": True, "message": "Task updated successfully.", "taskId": task_id}


@handle_tool_errors
async def move_task(task_id: str, previous_id: str | None = None, parent_id: str | None = None) -> dict:
    """Reorder a task within its list or change its parent."""
    body: dict[str, Any] = {"id": task_id}
    if previous_id is not None:
        body["previousId"] = previous_id
    if parent_id is not None:
        body["parentId"] = parent_id
    client = get_client()
    response = await client.client.post("/tasks/move", json=body)
    client._handle_error(response)
    return {"success": True, "message": "Task moved successfully.", "taskId": task_id}


@handle_tool_errors
async def delete_task(task_id: str) -> dict:
    """Delete a task permanently."""
    client = get_client()
    response = await client.client.post("/tasks/delete", json={"id": task_id})
    client._handle_error(response)
    return {"success": True, "message": "Task deleted successfully.", "taskId": task_id}


@handle_tool_errors
async def close_task(task_id: str, occurrence_start: str | None = None) -> dict:
    """Mark a task as completed."""
    body = filter_none_values({"id": task_id, "occurrenceStart": occurrence_start})
    client = get_client()
    response = await client.client.post("/tasks/close", json=body)
    client._handle_error(response)
    return {"success": True, "message": "Task closed successfully.", "taskId": task_id}


@handle_tool_errors
async def reopen_task(task_id: str, occurrence_start: str | None = None) -> dict:
    """Mark a completed task as not completed."""
    body = filter_none_values({"id": task_id, "occurrenceStart": occurrence_start})
    client = get_client()
    response = await client.client.post("/tasks/reopen", json=body)
    client._handle_error(response)
    return {"success": True, "message": "Task reopened successfully.", "taskId": task_id}
