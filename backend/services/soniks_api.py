import httpx


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