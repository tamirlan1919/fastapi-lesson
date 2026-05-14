import pytest
from unittest.mock import patch
from src.services.weather_service import get_weather_data

#
# @pytest.mark.asyncio # Обязательно для тестирования async функций
# @patch("src.services.weather_service.httpx.AsyncClient.get") # Указываем путь к методу, который хотим заменить
# async def test_get_weather_data_mocked(mock_get):
#     """ Тестируем функцию с замоканным httpx.get """
#     # Настраиваем mock-объект: что он должен вернуть
#     mock_response_payload = {"city": "London", "temp": 15}
#     # Моделируем успешный ответ
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.json.return_value = mock_response_payload
#
#     # Вызываем нашу функцию
#     result = await get_weather_data("London")
#
#     # Проверяем, что mock был вызван с правильным URL
#     mock_get.assert_called_once_with("https://api.weather.com/forecast/London")
#     # Проверяем, что функция вернула данные из mock-ответа
#     assert result == mock_response_payload