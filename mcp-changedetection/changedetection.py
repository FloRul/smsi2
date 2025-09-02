import logging
from typing import Any, Optional, List
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging at the beginning of the script
# This will print logs to the console with a timestamp, log level, and message.
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
    url: str, method: str = "GET", json_data: dict = None
) -> dict[str, Any] | str | None:
    """Make a request to the Changedetection.io API with proper error handling."""
    logging.info(f"Making {method.upper()} request to {url}")
    headers = {
        "User-Agent": USER_AGENT,
        "x-api-key": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"calling : {url} with {headers}")
            if method.upper() == "POST":
                response = await client.post(
                    url, headers=headers, json=json_data, timeout=30.0
                )
            else:
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


def main():
    logging.info("Starting FastMCP server.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
