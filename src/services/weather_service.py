import httpx
import os
from pydantic import ValidationError
from fastapi import HTTPException
from src.schemas import WeatherApiResponse
from pathlib import Path
from dotenv import load_dotenv


OPENWEATHER_API_KEY=os.getenv('OPENWEATHER_API_KEY', '')
OPENWEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

async def get_weather_data(city: str) -> WeatherApiResponse:
    params = {'q': city, 'appid': OPENWEATHER_API_KEY, 'units': 'metric'}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OPENWEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        raise HTTPException(status_code=504, detail='Cервис временно недоступен')

    try:
        return WeatherApiResponse(**data)
    except ValidationError as e:
        raise HTTPException(status_code=502, detail='Некорректный ответ от сервисы погоды')

