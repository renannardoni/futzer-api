from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

class Coordenadas(BaseModel):
    lat: float
    lng: float

class Endereco(BaseModel):
    rua: str
    cidade: str
    estado: str
    cep: str

class QuadraBase(BaseModel):
    nome: str
    descricao: str
    endereco: Endereco
    coordenadas: Coordenadas
    preco_por_hora: Optional[float] = Field(None, alias="precoPorHora")
    tipo_piso: str = Field(..., alias="tipoPiso")
    imagem_capa: str = Field(..., alias="imagemCapa")
    avaliacao: float = 0.0
    telefone: Optional[str] = None
    owner_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "nome": "Arena Premium Sports",
                "descricao": "Quadra de futebol society",
                "endereco": {
                    "rua": "Rua das Acácias, 123",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "cep": "01234-567"
                },
                "coordenadas": {"lat": -23.5505, "lng": -46.6333},
                "precoPorHora": 150.00,
                "tipoPiso": "society",
                "imagemCapa": "https://example.com/image.jpg",
                "avaliacao": 4.8
            }
        }

class QuadraCreate(QuadraBase):
    pass

class QuadraUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    endereco: Optional[Endereco] = None
    coordenadas: Optional[Coordenadas] = None
    preco_por_hora: Optional[float] = Field(None, alias="precoPorHora")
    tipo_piso: Optional[str] = Field(None, alias="tipoPiso")
    imagem_capa: Optional[str] = Field(None, alias="imagemCapa")
    avaliacao: Optional[float] = None
    telefone: Optional[str] = None

    class Config:
        populate_by_name = True

class QuadraInDB(QuadraBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Quadra(QuadraBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class UserBase(BaseModel):
    email: EmailStr
    nome: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
    id: str
    created_at: datetime
    is_active: bool

    class Config:
        json_encoders = {ObjectId: str}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
