from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(1, ge=1, le=5)
    is_done: bool = False
    deadline: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_trash(cls, value: str) -> str:
        forbidden_words = ['спам', 'реклама', 'казино']

        lower_value = value.lower()

        for word in forbidden_words:
            if word in lower_value:
                raise ValueError(f'Название не может содержать {value}')

        return value.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_done: Optional[bool] = None
    deadline: Optional[datetime] = None


class TaskToDone(BaseModel):
    is_done: Optional[bool] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    priority: int
    is_done: bool
    created_at: datetime
    updated_at: datetime
    deadline: Optional[datetime] = None


class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=30)

    @field_validator('username')
    @classmethod
    def username_must_be_clean(cls, value: str) -> str:
        if ' ' in value:
            raise ValueError('Username не должен содержать пробелы')

        return value.lower()


class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    role: str = 'user'


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str


class UserListResponse(BaseModel):
    users: list[UserResponse]


class Token(BaseModel):
    access_token: str
    token_type: str = 'Bearer'


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    tags: Optional[list[str]] = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: Optional[str]
    tags: list[str]
    created_at: datetime


def doc_to_response(doc: dict) -> NoteResponse:
    return NoteResponse(
        id=str(doc['_id']),
        title=doc['title'],
        content = doc.get('content'),
        tags = doc.get('tags', []),
        created_at = doc.get('created_at')
    )


class WeatherDescription(BaseModel):
    main: str
    description: str


class MainWeatherData(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int


class WeatherApiResponse(BaseModel):
    weather: list[WeatherDescription]
    main: MainWeatherData
    name: str