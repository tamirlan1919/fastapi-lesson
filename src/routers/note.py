from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.repositories.note_repo import NoteRepository
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Optional
from src.database import get_notes_collection, client
from src.schemas import NoteResponse, NoteCreate

router = APIRouter(prefix='/notes', tags=['Заметки'])


def get_repo(col: AsyncIOMotorCollection = Depends(get_notes_collection)) -> NoteRepository:
    return NoteRepository(col)


@router.post('/', response_model=NoteResponse, status_code=201)
async def create_note(data: NoteCreate, repo: NoteRepository = Depends(get_repo)):
    return await repo.create(data)


@router.get('/', response_model=list[NoteResponse])
async def list_notes(
        tag: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        skip: int  = Query(0, ge=0),
        repo: NoteRepository = Depends(get_repo)
):
    return await repo.get_all(tag=tag, limit=limit, offset=skip)