from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import uuid as _uuid

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

class HorarioDia(BaseModel):
    slots: List[str] = Field(default_factory=list)  # horários disponíveis ex: ["08:00", "08:15", "08:30"]

class HorariosSemanais(BaseModel):
    seg: HorarioDia = Field(default_factory=HorarioDia)
    ter: HorarioDia = Field(default_factory=HorarioDia)
    qua: HorarioDia = Field(default_factory=HorarioDia)
    qui: HorarioDia = Field(default_factory=HorarioDia)
    sex: HorarioDia = Field(default_factory=HorarioDia)
    sab: HorarioDia = Field(default_factory=HorarioDia)
    dom: HorarioDia = Field(default_factory=HorarioDia)

# Quadra interna de uma Arena (ex: "Quadra 1", "Quadra 2")
class SubQuadra(BaseModel):
    id: str = Field(default_factory=lambda: str(_uuid.uuid4()))
    nome: str = "Quadra 1"
    tipoPiso: str = "futebol"
    cobertura: str = "descoberto"
    imagemCapa: Optional[str] = None
    horariosSemanais: HorariosSemanais = Field(default_factory=HorariosSemanais)

    class Config:
        populate_by_name = True

# Reserva de um horário em uma sub-quadra
class Reserva(BaseModel):
    id: str = Field(default_factory=lambda: str(_uuid.uuid4()))
    quadra_id: str
    data: str           # "2026-03-08"
    hora_inicio: str    # "08:00" (formato HH:MM)
    duracao: int = 60   # duração em minutos (múltiplo de 15)
    nome_cliente: str
    telefone: Optional[str] = None
    valor: Optional[float] = None              # valor negociado
    recorrencia: Optional[str] = None          # "mensalista"
    recorrencia_grupo_id: Optional[str] = None # UUID para agrupar reservas recorrentes

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
    cobertura: Optional[str] = Field(None, alias="cobertura")
    modalidade: Optional[str] = Field("aluguel", alias="modalidade")
    imagem_capa: str = Field(..., alias="imagemCapa")
    imagens: List[str] = Field(default_factory=list, alias="imagens")
    avaliacao: float = 0.0
    telefone: Optional[str] = None
    owner_id: Optional[str] = None
    ativo: bool = True
    mostrar_disponibilidade: bool = Field(False, alias="mostrarDisponibilidade")
    horarios_semanais: HorariosSemanais = Field(default_factory=HorariosSemanais, alias="horariosSemanais")
    datas_bloqueadas: List[str] = Field(default_factory=list, alias="datasBloqueadas")
    quadras_internas: List[SubQuadra] = Field(default_factory=list, alias="quadrasInternas")
    reservas: List[Reserva] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class QuadraCreate(QuadraBase):
    pass

class QuadraUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    endereco: Optional[Endereco] = None
    coordenadas: Optional[Coordenadas] = None
    preco_por_hora: Optional[float] = Field(None, alias="precoPorHora")
    tipo_piso: Optional[str] = Field(None, alias="tipoPiso")
    cobertura: Optional[str] = None
    modalidade: Optional[str] = Field(None, alias="modalidade")
    imagem_capa: Optional[str] = Field(None, alias="imagemCapa")
    imagens: Optional[List[str]] = Field(None, alias="imagens")
    avaliacao: Optional[float] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None
    mostrar_disponibilidade: Optional[bool] = Field(None, alias="mostrarDisponibilidade")
    horarios_semanais: Optional[HorariosSemanais] = Field(None, alias="horariosSemanais")
    datas_bloqueadas: Optional[List[str]] = Field(None, alias="datasBloqueadas")

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
