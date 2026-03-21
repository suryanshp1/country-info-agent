import httpx
import asyncio

async def fetch_country(country: str):
    url = f"https://restcountries.com/v3.1/name/{country}"

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                res.raise_for_status()
                data = res.json()
                
                # The API returns a list of substring matches.
                # Prioritize an exact match on common or official name to avoid returning territories.
                search_lower = country.lower()
                exact_match = next(
                    (c for c in data if 
                     c.get("name", {}).get("common", "").lower() == search_lower or 
                     c.get("name", {}).get("official", "").lower() == search_lower), 
                    None
                )
                
                return exact_match if exact_match else data[0]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Country '{country}' not found. Please check the spelling.")
            if attempt == 2:
                raise e
            await asyncio.sleep(1)
        except Exception as e:
            if attempt == 2:
                raise e
            await asyncio.sleep(1)
