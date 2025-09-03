import logging
from typing import Any, Optional, List, Dict
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging at the beginning of the script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize FastMCP server
mcp = FastMCP("changedetection")

# Constants
CHANGEDETECTION_API_BASE = (
    "http://changedetection-lb-961880406.ca-central-1.elb.amazonaws.com"
)
API_KEY = "9208afcd1c039b69d78f28b2529416e4"  # Hardcoded for local development
USER_AGENT = "changedetection-mcp/1.0"


async def make_changedetection_request(
    url: str, method: str = "GET", json_data: dict = None, text_data: str = None
) -> dict[str, Any] | str | None:
    """Make a request to the Changedetection.io API with proper error handling."""
    logging.info(f"Making {method.upper()} request to {url}")
    headers = {
        "User-Agent": USER_AGENT,
        "x-api-key": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json" if json_data else "text/plain",
    }

    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"calling : {url} with {headers}")

            if method.upper() == "POST":
                if json_data:
                    response = await client.post(
                        url, headers=headers, json=json_data, timeout=30.0
                    )
                elif text_data:
                    headers["Content-Type"] = "text/plain"
                    response = await client.post(
                        url, headers=headers, content=text_data, timeout=30.0
                    )
                else:
                    response = await client.post(url, headers=headers, timeout=30.0)
            elif method.upper() == "PUT":
                response = await client.put(
                    url, headers=headers, json=json_data, timeout=30.0
                )
            elif method.upper() == "DELETE":
                if json_data:
                    response = await client.delete(
                        url, headers=headers, json=json_data, timeout=30.0
                    )
                else:
                    response = await client.delete(url, headers=headers, timeout=30.0)
            else:  # GET
                response = await client.get(url, headers=headers, timeout=30.0)

            response.raise_for_status()

            # Handle different response types
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                logging.info(f"Successfully received JSON response from {url}")
                return response.json()
            else:
                logging.warning(
                    f"Received non-JSON response from {url}. Content-Type: {content_type}"
                )
                return response.text

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP error occurred: {e.response.status_code} for URL {url}. Response: {e.response.text}"
            )
            return f"HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            logging.error(f"An unexpected error occurred for URL {url}: {str(e)}")
            return f"Request failed: {str(e)}"


@mcp.tool()
async def create_watch(
    url: str,
    title: Optional[str] = None,
    paused: bool = False,
    method: str = "GET",
    fetch_backend: str = "html_requests",
    notification_urls: Optional[List[str]] = None,
    check_interval_seconds: Optional[int] = None,
    tag: Optional[str] = None,
) -> str:
    """Create a new web page change monitor (watch) on Changedetection.io."""
    logging.info(f"Attempting to create watch for URL: {url}")

    # Prepare the request data
    watch_data = {
        "url": url,
        "paused": paused,
        "method": method,
        "fetch_backend": fetch_backend,
    }

    # Add optional parameters
    if title:
        watch_data["title"] = title
    if tag:
        watch_data["tag"] = tag
    if notification_urls:
        watch_data["notification_urls"] = notification_urls
    if check_interval_seconds:
        watch_data["time_between_check"] = {"seconds": check_interval_seconds}

    logging.info(f"Sending watch data to API: {watch_data}")

    # Make the API request
    create_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch"
    result = await make_changedetection_request(
        create_url, method="POST", json_data=watch_data
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            logging.error(f"Failed to create watch for {url}: {result}")
            return f"Failed to create watch: {result}"
        else:
            logging.info(f"Watch created successfully for {url}. Result: {result}")
            return f"Watch created successfully! Watch ID: {result}"

    logging.info(f"Watch for {url} created with unexpected response type: {result}")
    return f"Watch created with response: {result}"


@mcp.tool()
async def list_watches(tag: Optional[str] = None, recheck_all: bool = False) -> str:
    """List all web page change monitors (watches) from Changedetection.io."""
    logging.info(f"Listing watches with tag='{tag}' and recheck_all={recheck_all}")

    # Build query parameters
    params = []
    if tag:
        params.append(f"tag={tag}")
    if recheck_all:
        params.append("recheck_all=1")

    query_string = "?" + "&".join(params) if params else ""
    list_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch{query_string}"

    result = await make_changedetection_request(list_url)

    if isinstance(result, str):
        logging.error(f"Failed to list watches: {result}")
        return f"Failed to list watches: {result}"

    if not result:
        logging.info("No watches found or API returned empty list.")
        return "No watches found or unable to fetch watch list."

    logging.info(f"Found {len(result)} watches.")

    # Format the watch list
    watch_summaries = []
    for watch_id, watch_data in result.items():
        summary = f"""
Watch ID: {watch_id}
URL: {watch_data.get('url', 'Unknown')}
Title: {watch_data.get('title', 'No title')}
Status: {'Paused' if watch_data.get('paused', False) else 'Active'}
Last Checked: {watch_data.get('last_checked', 'Never')}
Last Changed: {watch_data.get('last_changed', 'Never')}
"""
        watch_summaries.append(summary.strip())

    return "\n---\n".join(watch_summaries)


@mcp.tool()
async def get_watch(
    watch_id: str,
    recheck: bool = False,
    paused: Optional[str] = None,
    muted: Optional[str] = None,
) -> str:
    """Get detailed information about a specific watch, optionally modify its status."""
    logging.info(f"Getting watch {watch_id}")

    # Build query parameters
    params = []
    if recheck:
        params.append("recheck=1")
    if paused in ["paused", "unpaused"]:
        params.append(f"paused={paused}")
    if muted in ["muted", "unmuted"]:
        params.append(f"muted={muted}")

    query_string = "?" + "&".join(params) if params else ""
    get_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch/{watch_id}{query_string}"

    result = await make_changedetection_request(get_url)

    if isinstance(result, str):
        logging.error(f"Failed to get watch {watch_id}: {result}")
        return f"Failed to get watch: {result}"

    if isinstance(result, dict):
        # Format the watch details
        return f"""
Watch Details:
ID: {result.get('uuid', watch_id)}
URL: {result.get('url', 'Unknown')}
Title: {result.get('title', 'No title')}
Status: {'Paused' if result.get('paused', False) else 'Active'}
Muted: {result.get('muted', False)}
Method: {result.get('method', 'GET')}
Backend: {result.get('fetch_backend', 'html_requests')}
Check Interval: {result.get('time_between_check', 'Default')}
Last Checked: {result.get('last_checked', 'Never')}
Last Changed: {result.get('last_changed', 'Never')}
Last Error: {result.get('last_error', 'None')}
Tags: {', '.join(result.get('tags', []))}
"""

    return f"Watch retrieved: {result}"


@mcp.tool()
async def update_watch(
    watch_id: str,
    url: Optional[str] = None,
    title: Optional[str] = None,
    paused: Optional[bool] = None,
    muted: Optional[bool] = None,
    method: Optional[str] = None,
    fetch_backend: Optional[str] = None,
    notification_urls: Optional[List[str]] = None,
    check_interval_seconds: Optional[int] = None,
) -> str:
    """Update an existing watch with new settings."""
    logging.info(f"Updating watch {watch_id}")

    # Prepare update data - only include fields that are provided
    update_data = {}
    if url is not None:
        update_data["url"] = url
    if title is not None:
        update_data["title"] = title
    if paused is not None:
        update_data["paused"] = paused
    if muted is not None:
        update_data["muted"] = muted
    if method is not None:
        update_data["method"] = method
    if fetch_backend is not None:
        update_data["fetch_backend"] = fetch_backend
    if notification_urls is not None:
        update_data["notification_urls"] = notification_urls
    if check_interval_seconds is not None:
        update_data["time_between_check"] = {"seconds": check_interval_seconds}

    update_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch/{watch_id}"
    result = await make_changedetection_request(
        update_url, method="PUT", json_data=update_data
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to update watch: {result}"
        return f"Watch {watch_id} updated successfully!"

    return f"Watch updated: {result}"


@mcp.tool()
async def delete_watch(watch_id: str) -> str:
    """Delete a watch and all its related history."""
    logging.info(f"Deleting watch {watch_id}")

    delete_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch/{watch_id}"
    result = await make_changedetection_request(delete_url, method="DELETE")

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to delete watch: {result}"
        return f"Watch {watch_id} deleted successfully!"

    return f"Watch deleted: {result}"


@mcp.tool()
async def get_watch_history(watch_id: str) -> str:
    """Get the history of all snapshots for a watch."""
    logging.info(f"Getting history for watch {watch_id}")

    history_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch/{watch_id}/history"
    result = await make_changedetection_request(history_url)

    if isinstance(result, str):
        return f"Failed to get history: {result}"

    if isinstance(result, dict):
        if not result:
            return f"No history found for watch {watch_id}"

        # Format the history
        history_entries = []
        for timestamp, path in result.items():
            history_entries.append(f"Timestamp: {timestamp} - Path: {path}")

        return f"History for watch {watch_id}:\n" + "\n".join(history_entries)

    return f"History retrieved: {result}"


@mcp.tool()
async def get_watch_snapshot(
    watch_id: str, timestamp: str = "latest", html: bool = False
) -> str:
    """Get a specific snapshot from a watch's history. Use 'latest' for most recent."""
    logging.info(f"Getting snapshot for watch {watch_id}, timestamp: {timestamp}")

    # Build query parameters
    params = []
    if html:
        params.append("html=1")

    query_string = "?" + "&".join(params) if params else ""
    snapshot_url = f"{CHANGEDETECTION_API_BASE}/api/v1/watch/{watch_id}/history/{timestamp}{query_string}"

    result = await make_changedetection_request(snapshot_url)

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to get snapshot: {result}"
        # Return the actual content
        return f"Snapshot content:\n{result}"

    return f"Snapshot retrieved: {result}"


@mcp.tool()
async def search_watches(
    query: str, tag: Optional[str] = None, partial: bool = True
) -> str:
    """Search web page change monitors (watches) by URL or title text."""
    logging.info(
        f"Searching for watches with query='{query}', tag='{tag}', partial={partial}"
    )

    # Build query parameters
    params = [f"q={query}"]
    if tag:
        params.append(f"tag={tag}")
    if partial:
        params.append("partial=true")

    query_string = "?" + "&".join(params)
    search_url = f"{CHANGEDETECTION_API_BASE}/api/v1/search{query_string}"

    result = await make_changedetection_request(search_url)

    if isinstance(result, str):
        logging.error(f"Failed to search watches: {result}")
        return f"Failed to search watches: {result}"

    if not result:
        logging.info(f"No search results found for query '{query}'.")
        return f"No watches found matching '{query}'."

    logging.info(f"Found {len(result)} matches for query '{query}'.")

    # Format the search results
    match_summaries = []
    for watch_id, watch_data in result.items():
        summary = f"""
Watch ID: {watch_id}
URL: {watch_data.get('url', 'Unknown')}
Title: {watch_data.get('title', 'No title')}
Status: {'Paused' if watch_data.get('paused', False) else 'Active'}
Tags: {', '.join(watch_data.get('tags', []))}
"""
        match_summaries.append(summary.strip())

    return f"Found {len(result)} matches for '{query}':\n\n" + "\n---\n".join(
        match_summaries
    )


@mcp.tool()
async def list_tags() -> str:
    """List all available tags/groups."""
    logging.info("Listing all tags")

    tags_url = f"{CHANGEDETECTION_API_BASE}/api/v1/tags"
    result = await make_changedetection_request(tags_url)

    if isinstance(result, str):
        return f"Failed to list tags: {result}"

    if isinstance(result, dict):
        if not result:
            return "No tags found."

        # Format the tags list
        tag_summaries = []
        for tag_id, tag_data in result.items():
            summary = f"""
Tag ID: {tag_id}
Title: {tag_data.get('title', 'No title')}
Notification URLs: {', '.join(tag_data.get('notification_urls', []))}
Muted: {tag_data.get('notification_muted', False)}
"""
            tag_summaries.append(summary.strip())

        return f"Found {len(result)} tags:\n\n" + "\n---\n".join(tag_summaries)

    return f"Tags retrieved: {result}"


@mcp.tool()
async def create_tag(title: str, notification_urls: Optional[List[str]] = None) -> str:
    """Create a new tag/group."""
    logging.info(f"Creating tag with title: {title}")

    tag_data = {"title": title}
    if notification_urls:
        tag_data["notification_urls"] = notification_urls

    create_url = f"{CHANGEDETECTION_API_BASE}/api/v1/tag"
    result = await make_changedetection_request(
        create_url, method="POST", json_data=tag_data
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to create tag: {result}"
        return f"Tag '{title}' created successfully!"

    if isinstance(result, dict) and "uuid" in result:
        return f"Tag '{title}' created successfully! Tag ID: {result['uuid']}"

    return f"Tag created: {result}"


@mcp.tool()
async def get_tag(
    tag_id: str, muted: Optional[str] = None, recheck: bool = False
) -> str:
    """Get tag information, optionally set mute status or recheck all watches in tag."""
    logging.info(f"Getting tag {tag_id}")

    # Build query parameters
    params = []
    if muted in ["muted", "unmuted"]:
        params.append(f"muted={muted}")
    if recheck:
        params.append("recheck=true")

    query_string = "?" + "&".join(params) if params else ""
    get_url = f"{CHANGEDETECTION_API_BASE}/api/v1/tag/{tag_id}{query_string}"

    result = await make_changedetection_request(get_url)

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to get tag: {result}"
        return f"Tag operation completed: {result}"

    if isinstance(result, dict):
        return f"""
Tag Details:
ID: {result.get('uuid', tag_id)}
Title: {result.get('title', 'No title')}
Notification URLs: {', '.join(result.get('notification_urls', []))}
Muted: {result.get('notification_muted', False)}
"""

    return f"Tag retrieved: {result}"


@mcp.tool()
async def update_tag(
    tag_id: str,
    title: Optional[str] = None,
    notification_urls: Optional[List[str]] = None,
    notification_muted: Optional[bool] = None,
) -> str:
    """Update an existing tag."""
    logging.info(f"Updating tag {tag_id}")

    # Prepare update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if notification_urls is not None:
        update_data["notification_urls"] = notification_urls
    if notification_muted is not None:
        update_data["notification_muted"] = notification_muted

    update_url = f"{CHANGEDETECTION_API_BASE}/api/v1/tag/{tag_id}"
    result = await make_changedetection_request(
        update_url, method="PUT", json_data=update_data
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to update tag: {result}"
        return f"Tag {tag_id} updated successfully!"

    return f"Tag updated: {result}"


@mcp.tool()
async def delete_tag(tag_id: str) -> str:
    """Delete a tag/group and remove it from all watches."""
    logging.info(f"Deleting tag {tag_id}")

    delete_url = f"{CHANGEDETECTION_API_BASE}/api/v1/tag/{tag_id}"
    result = await make_changedetection_request(delete_url, method="DELETE")

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to delete tag: {result}"
        return f"Tag {tag_id} deleted successfully!"

    return f"Tag deleted: {result}"


@mcp.tool()
async def get_notifications() -> str:
    """Get the list of global notification URLs."""
    logging.info("Getting notification URLs")

    notifications_url = f"{CHANGEDETECTION_API_BASE}/api/v1/notifications"
    result = await make_changedetection_request(notifications_url)

    if isinstance(result, str):
        return f"Failed to get notifications: {result}"

    if isinstance(result, dict) and "notification_urls" in result:
        urls = result["notification_urls"]
        if not urls:
            return "No notification URLs configured."
        return f"Notification URLs:\n" + "\n".join(f"- {url}" for url in urls)

    return f"Notifications retrieved: {result}"


@mcp.tool()
async def add_notifications(notification_urls: List[str]) -> str:
    """Add one or more notification URLs to the global configuration."""
    logging.info(f"Adding notification URLs: {notification_urls}")

    data = {"notification_urls": notification_urls}
    add_url = f"{CHANGEDETECTION_API_BASE}/api/v1/notifications"
    result = await make_changedetection_request(add_url, method="POST", json_data=data)

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to add notifications: {result}"
        return "Notification URLs added successfully!"

    return f"Notifications added: {result}"


@mcp.tool()
async def replace_notifications(notification_urls: List[str]) -> str:
    """Replace all notification URLs with the provided list."""
    logging.info(f"Replacing notification URLs with: {notification_urls}")

    data = {"notification_urls": notification_urls}
    replace_url = f"{CHANGEDETECTION_API_BASE}/api/v1/notifications"
    result = await make_changedetection_request(
        replace_url, method="PUT", json_data=data
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to replace notifications: {result}"
        return "Notification URLs replaced successfully!"

    return f"Notifications replaced: {result}"


@mcp.tool()
async def delete_notifications(notification_urls: List[str]) -> str:
    """Delete one or more notification URLs from the configuration."""
    logging.info(f"Deleting notification URLs: {notification_urls}")

    data = {"notification_urls": notification_urls}
    delete_url = f"{CHANGEDETECTION_API_BASE}/api/v1/notifications"
    result = await make_changedetection_request(
        delete_url, method="DELETE", json_data=data
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to delete notifications: {result}"
        return "Notification URLs deleted successfully!"

    return f"Notifications deleted: {result}"


@mcp.tool()
async def import_watches(
    urls: List[str],
    tag: Optional[str] = None,
    tag_uuids: Optional[str] = None,
    proxy: Optional[str] = None,
    dedupe: bool = True,
) -> str:
    """Import multiple URLs for monitoring."""
    logging.info(f"Importing {len(urls)} URLs")

    # Build query parameters
    params = []
    if tag:
        params.append(f"tag={tag}")
    if tag_uuids:
        params.append(f"tag_uuids={tag_uuids}")
    if proxy:
        params.append(f"proxy={proxy}")
    if not dedupe:
        params.append("dedupe=false")

    query_string = "?" + "&".join(params) if params else ""
    import_url = f"{CHANGEDETECTION_API_BASE}/api/v1/import{query_string}"

    # Send URLs as plain text, line-separated
    urls_text = "\n".join(urls)
    result = await make_changedetection_request(
        import_url, method="POST", text_data=urls_text
    )

    if isinstance(result, str):
        if result.startswith("HTTP error") or result.startswith("Request failed"):
            return f"Failed to import URLs: {result}"
        return f"Successfully imported URLs: {result}"

    if isinstance(result, list):
        return f"Successfully imported {len(result)} watches. IDs: {', '.join(result)}"

    return f"Import completed: {result}"


@mcp.tool()
async def get_system_info() -> str:
    """Get system information about the changedetection.io instance."""
    logging.info("Getting system information")

    info_url = f"{CHANGEDETECTION_API_BASE}/api/v1/systeminfo"
    result = await make_changedetection_request(info_url)

    if isinstance(result, str):
        return f"Failed to get system info: {result}"

    if isinstance(result, dict):
        return f"""
System Information:
Watch Count: {result.get('watch_count', 'Unknown')}
Tag Count: {result.get('tag_count', 'Unknown')}
Uptime: {result.get('uptime', 'Unknown')}
Version: {result.get('version', 'Unknown')}
"""

    return f"System info retrieved: {result}"


def main():
    logging.info("Starting FastMCP server.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
