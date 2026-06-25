from pathlib import Path
from dotenv import load_dotenv
from fastapi import HTTPException
import httpx
import os
import json
import io
import csv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

YANDEX_TOKEN = os.getenv('YANDEX_DISK_TOKEN', '')
YANDEX_API = 'https://cloud-api.yandex.net/v1/disk/resources/'



async def _get_upload_url(filename: str) -> str:
    headers = {'Authorization': f'OAuth {YANDEX_TOKEN}'}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f'{YANDEX_API}upload',
            headers=headers,
            params={'path': f'/{filename}', 'overwrite': 'true'}
        )
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail='Токен Яндекс диска недействителен')
        resp.raise_for_status()
    return resp.json()['href']


async def export_tasks_to_json(tasks_data: list[dict], user_id: int) -> dict:
    filename = f'tracker_user_{user_id}_tasks.json'
    upload_url = await _get_upload_url(filename)

    content = json.dumps(tasks_data, ensure_ascii=False, indent=2)
    async with httpx.AsyncClient(timeout=30) as client:
        put_resp = await client.put(upload_url, content=content.encode('utf-8'))
        put_resp.raise_for_status()

    return {
        'filename': filename,
        'rows': len(tasks_data),
        'disk_path': f'disk:/{filename}'
    }


async def export_tasks_to_csv(tasks_data: list[dict], user_id: int) -> dict:
    filename = f'tracker_user_{user_id}_tasks.csv'
    upload_url = await _get_upload_url(filename)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'title', 'priority', 'is_done', 'created_at'
    ])
    for task in tasks_data:
        writer.writerow([
            task.get('id'), task.get('title'),
            task.get('priority'), task.get('is_done'),
            task.get('created_at'),

        ])
    async with httpx.AsyncClient(timeout=30) as client:
        put_resp = await client.put(
            upload_url,
            content=output.getvalue().encode('utf-8'),
            headers={'Content-Type': 'text/csv; charset=utf-8'}
        )
        put_resp.raise_for_status()

    return {
        'filename': filename,
        'rows': len(tasks_data),
        'disk_path': f'disk:/{filename}'
    }