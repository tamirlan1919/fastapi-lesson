from fastapi import APIRouter

from src.services.weather_service import get_weather_data

router = APIRouter(prefix='/weather', tags=['Weather'])


@router.get('/{city}')
async def check_weather(city: str):
    weather = await get_weather_data(city)
    return {
        'city': weather.name,
        'temp': weather.main.temp,
        'condition': weather.weather[0].description if weather.weather else 'неизвестно'
    }