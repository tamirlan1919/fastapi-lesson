import httpx


async def get_weather_data(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/forecast/{city}")
        response.raise_for_status() # Вызовет ошибку, если статус не 2xx
        return response.json()
