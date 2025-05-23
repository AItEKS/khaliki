import httpx
from typing import List, Dict, Any


BASE_URL = "https://sonik.space/api/"

async def fetch(endpoint: str, params: dict = None) -> any:
    """Fetches JSON data asynchronously from a given API endpoint.

    Args:
        endpoint: The API endpoint to query (appended to BASE_URL).
        params: Optional dictionary of query parameters.

    Returns:
        The parsed JSON response from the API.

    Raises:
        httpx.HTTPStatusError: If the response status is not successful.
        httpx.RequestError: For network-related errors.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()


async def fetch_all_paginated(endpoint: str, params: dict = None, page_count: int = 10) -> List[Dict[str, Any]]:
    """Fetches all paginated JSON data, automatically following redirects."""
    all_data = []
    next_url = f"{BASE_URL}{endpoint}"
    initial_params = params or {}

    page_num = 0
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while next_url and page_num < page_count:
            page_num += 1
            response = await client.get(next_url, params=initial_params)
            response.raise_for_status()
            
            page_data = response.json()
            if isinstance(page_data, list):
                all_data.extend(page_data)
            else:
                all_data.append(page_data)
            
            link_header = response.headers.get("Link")
            if not link_header:
                break

            next_link = None
            for link in link_header.split(","):
                if 'rel="next"' in link:
                    next_link = link.split(";")[0].strip()[1:-1]
                    break

            next_url = next_link
            initial_params = None

    return all_data