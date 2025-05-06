import httpx
from typing import List, Dict, Any, Optional

BASE_URL = "https://sonik.space/api/"


async def fetch(endpoint: str, params: Optional[dict] = None) -> Any:
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


async def fetch_all_paginated(
    endpoint: str, 
    params: Optional[dict] = None, 
    page_count: int = 10
) -> List[Dict[str, Any]]:
    """Fetches all paginated JSON data, automatically following redirects.
    
    Args:
        endpoint: The API endpoint to query (appended to BASE_URL).
        params: Optional dictionary of query parameters for the initial request.
        page_count: Maximum number of pages to fetch (default: 10).
        
    Returns:
        A list containing all combined data from paginated responses.
    """
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
            
            # Parse Link header to find next page URL
            link_header = response.headers.get("Link")
            if not link_header:
                break
                
            next_url = _extract_next_url(link_header)
            if not next_url:
                break
                
            # Clear params after first request as they're included in next_url
            initial_params = None
            
    return all_data


def _extract_next_url(link_header: str) -> Optional[str]:
    """Extract the 'next' URL from a Link header.
    
    Args:
        link_header: The Link header string to parse.
        
    Returns:
        The URL for the next page, or None if not found.
    """
    for link in link_header.split(","):
        if 'rel="next"' in link:
            return link.split(";")[0].strip()[1:-1]
    return None