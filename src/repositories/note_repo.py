from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas import NoteCreate, NoteResponse, NoteUpdate, doc_to_response


class NoteRepository:
    def __init__(self, col: AsyncIOMotorCollection):
        self.col = col

    async def create(self, data: NoteCreate):
        doc = {
            **data.model_dump(),
            'created_at': datetime.now(timezone.utc)
        }
        result = await self.col.insert_one(doc)
        created_object = await self.col.find_one({'_id': result.inserted_id})
        return doc_to_response(created_object)

    async def get_by_id(self, note_id: str) -> Optional[NoteResponse]:
        try:
            oid = ObjectId(note_id)
        except Exception:
            return None
        doc = await self.col.find_one({'_id': oid})
        return doc_to_response(doc)

    async def get_all(self,
                      tag: Optional[str] = None,
                      limit: int = 20,
                      offset: int = 0) -> list[NoteResponse]:
        query = {'tags': tag} if tag else {}
        cursor = self.col.find(query).sort('created_at', -1).limit(limit)
        docs = await cursor.to_list()
        return [doc_to_response(d) for d in docs]
