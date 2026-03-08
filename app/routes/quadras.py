from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from ..models import Quadra, QuadraCreate, QuadraUpdate, HorariosSemanais, User
from ..database import get_database
from ..auth import get_current_active_user

router = APIRouter(prefix="/quadras", tags=["quadras"])

# Mapeia valores antigos de tipo_piso para os novos esportes
_TIPO_PISO_MAP = {
    "society": "futebol",
    "grama": "futebol",
    "salao": "futsal",
    "quadra": "futebol",
    "campo": "futebol",
    "areia": "beach_tenis",
    "beach_tenis": "beach_tenis",
    "futebolei": "volei",
    "futvolei": "volei",
    "futebol": "futebol",
    "futsal": "futsal",
    "tenis": "tenis",
    "tênis": "tenis",
    "padel": "padel",
    "volei": "volei",
    "vôlei": "volei",
    "basquete": "basquete",
}

def _norm_tipo(q: dict) -> str:
    raw = q.get("tipoPiso") or q.get("tipo_piso") or "futebol"
    return _TIPO_PISO_MAP.get(raw.lower().strip(), raw)

def _horarios_from_doc(q: dict) -> HorariosSemanais:
    from ..models import HorarioDia
    raw = q.get("horariosSemanais") or q.get("horarios_semanais")
    if raw and isinstance(raw, dict):
        dias = {}
        for key in ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]:
            dia = raw.get(key, {})
            if isinstance(dia, dict) and "slots" in dia:
                dias[key] = HorarioDia(slots=dia["slots"])
            else:
                dias[key] = HorarioDia(slots=[])
        return HorariosSemanais(**dias)
    return HorariosSemanais()

def _to_quadra(q: dict) -> Quadra:
    return Quadra(
        id=str(q["_id"]),
        nome=q["nome"],
        descricao=q["descricao"],
        endereco=q["endereco"],
        coordenadas=q["coordenadas"],
        precoPorHora=q.get("precoPorHora", q.get("preco_por_hora")),
        tipoPiso=_norm_tipo(q),
        cobertura=q.get("cobertura"),
        modalidade=q.get("modalidade", "aluguel"),
        imagemCapa=q.get("imagemCapa", q.get("imagem_capa")),
        imagens=q.get("imagens", []),
        avaliacao=q.get("avaliacao", 0.0),
        telefone=q.get("telefone"),
        owner_id=q.get("owner_id"),
        horariosSemanais=_horarios_from_doc(q),
        datasBloqueadas=q.get("datasBloqueadas", q.get("datas_bloqueadas", [])),
        created_at=q["created_at"],
        updated_at=q["updated_at"]
    )


@router.get("/minhas", response_model=List[Quadra])
async def list_minhas_quadras(
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    cursor = db.quadras.find({"owner_id": current_user.id})
    quadras = await cursor.to_list(length=200)
    return [_to_quadra(q) for q in quadras]


@router.get("/", response_model=List[Quadra])
async def list_quadras(
    skip: int = 0,
    limit: int = 100,
    tipo_piso: Optional[str] = None,
    cidade: Optional[str] = None,
    db=Depends(get_database)
):
    query = {}
    if tipo_piso and tipo_piso != "todos":
        query["$or"] = [{"tipo_piso": tipo_piso}, {"tipoPiso": tipo_piso}]
    if cidade:
        query["endereco.cidade"] = {"$regex": cidade, "$options": "i"}

    cursor = db.quadras.find(query).skip(skip).limit(limit)
    quadras = await cursor.to_list(length=limit)
    return [_to_quadra(q) for q in quadras]


@router.get("/{quadra_id}", response_model=Quadra)
async def get_quadra(quadra_id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    quadra = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not quadra:
        raise HTTPException(status_code=404, detail="Quadra not found")

    return _to_quadra(quadra)


@router.post("/", response_model=Quadra, status_code=status.HTTP_201_CREATED)
async def create_quadra(
    quadra: QuadraCreate,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime

    quadra_dict = quadra.dict(by_alias=True)
    quadra_dict["owner_id"] = current_user.id
    quadra_dict["created_at"] = datetime.utcnow()
    quadra_dict["updated_at"] = datetime.utcnow()

    result = await db.quadras.insert_one(quadra_dict)
    created = await db.quadras.find_one({"_id": result.inserted_id})
    return _to_quadra(created)


@router.put("/{quadra_id}", response_model=Quadra)
async def update_quadra(
    quadra_id: str,
    quadra_update: QuadraUpdate,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime

    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Quadra not found")

    if existing.get("owner_id") not in (current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Sem permissão para editar esta quadra")

    update_data = {k: v for k, v in quadra_update.dict(by_alias=True, exclude_unset=True).items()}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.quadras.update_one({"_id": ObjectId(quadra_id)}, {"$set": update_data})

    updated = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    return _to_quadra(updated)


@router.delete("/{quadra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quadra(
    quadra_id: str,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Quadra not found")

    if existing.get("owner_id") not in (current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Sem permissão para deletar esta quadra")

    await db.quadras.delete_one({"_id": ObjectId(quadra_id)})
    return None
