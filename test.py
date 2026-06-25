import httpx
import asyncio

async def fetch_posts():
    # Используем 'async with' для управления жизненным циклом клиента
    async with httpx.AsyncClient() as client:
        # 'await' приостанавливает выполнение, пока мы ждем ответа от сети
        response = await client.get("https://jsonplaceholder.typicode.com/posts/1")
        # Проверить, был ли запрос успешным (статус 2xx)
        response.raise_for_status()
        print(response.json())
        return response.json()


if __name__ == '__main__':
    asyncio.run(fetch_posts())