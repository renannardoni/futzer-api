from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from ..models import Quadra, QuadraCreate, QuadraUpdate, User
from ..database import get_database
from ..auth import get_current_active_user

router = APIRouter(prefix="/quadras", tags=["quadras"])

@router.get("/", response_model=List[Quadra])
async def list_quadras(
    skip: int = 0,
    limit: int = 100,
    tipo_piso: str = None,
    cidade: str = None,
    db = Depends(get_database)
):
    query = {}
    if tipo_piso and tipo_piso != "todos":
        query["$or"] = [{"tipo_piso": tipo_piso}, {"tipoPiso": tipo_piso}]
    if cidade:
        query["endereco.cidade"] = {"$regex": cidade, "$options": "i"}
    
    cursor = db.quadras.find(query).skip(skip).limit(limit)
    quadras = await cursor.to_list(length=limit)
    
    return [
        Quadra(
            id=str(q["_id"]),
            nome=q["nome"],
            descricao=q["descricao"],
            endereco=q["endereco"],
            coordenadas=q["coordenadas"],
            precoPorHora=q.get("precoPorHora", q.get("preco_por_hora")),
            tipoPiso=q.get("tipoPiso", q.get("tipo_piso")),
            imagemCapa=q.get("imagemCapa", q.get("imagem_capa")),
            avaliacao=q.get("avaliacao", 0.0),
            owner_id=q.get("owner_id"),
            created_at=q["created_at"],
            updated_at=q["updated_at"]
        )
        for q in quadras
    ]

@router.get("/{quadra_id}", response_model=Quadra)
async def get_quadra(quadra_id: str, db = Depends(get_database)):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    quadra = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not quadra:
        raise HTTPException(status_code=404, detail="Quadra not found")
    
    return Quadra(
        id=str(quadra["_id"]),
        nome=quadra["nome"],
        descricao=quadra["descricao"],
        endereco=quadra["endereco"],
        coordenadas=quadra["coordenadas"],
        precoPorHora=quadra.get("precoPorHora", quadra.get("preco_por_hora")),
        tipoPiso=quadra.get("tipoPiso", quadra.get("tipo_piso")),
        imagemCapa=quadra.get("imagemCapa", quadra.get("imagem_capa")),
        avaliacao=quadra.get("avaliacao", 0.0),
        owner_id=quadra.get("owner_id"),
        created_at=quadra["created_at"],
        updated_at=quadra["updated_at"]
    )

@router.post("/", response_model=Quadra, status_code=status.HTTP_201_CREATED)
async def create_quadra(
    quadra: QuadraCreate,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_database)
):
    from datetime import datetime
    
    quadra_dict = quadra.dict(by_alias=True)
    quadra_dict["owner_id"] = str(current_user.id)
    quadra_dict["created_at"] = datetime.utcnow()
    quadra_dict["updated_at"] = datetime.utcnow()
    
    result = await db.quadras.insert_one(quadra_dict)
    created_quadra = await db.quadras.find_one({"_id": result.inserted_id})
    
    return Quadra(
        id=str(created_quadra["_id"]),
        nome=created_quadra["nome"],
        descricao=created_quadra["descricao"],
        endereco=created_quadra["endereco"],
        coordenadas=created_quadra["coordenadas"],
        precoPorHora=created_quadra.get("precoPorHora", created_quadra.get("preco_por_hora")),
        tipoPiso=created_quadra.get("tipoPiso", created_quadra.get("tipo_piso")),
        imagemCapa=created_quadra.get("imagemCapa", created_quadra.get("imagem_capa")),
        avaliacao=created_quadra.get("avaliacao", 0.0),
        owner_id=created_quadra.get("owner_id"),
        created_at=created_quadra["created_at"],
        updated_at=created_quadra["updated_at"]
    )

@router.put("/{quadra_id}", response_model=Quadra)
async def update_quadra(
    quadra_id: str,
    quadra_update: QuadraUpdate,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_database)
):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    existing_quadra = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing_quadra:
        raise HTTPException(status_code=404, detail="Quadra not found")
    
    if existing_quadra.get("owner_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this quadra")
    
    update_data = {k: v for k, v in quadra_update.dict(by_alias=True, exclude_unset=True).items()}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.quadras.update_one(
            {"_id": ObjectId(quadra_id)},
            {"$set": update_data}
        )
    
    updated_quadra = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    return Quadra(
        id=str(updated_quadra["_id"]),
        nome=updated_quadra["nome"],
        descricao=updated_quadra["descricao"],
        endereco=updated_quadra["endereco"],
        coordenadas=updated_quadra["coordenadas"],
        precoPorHora=updated_quadra["preco_por_hora"],
        tipoPiso=updated_quadra["tipo_piso"],
        imagemCapa=updated_quadra["imagem_capa"],
        avaliacao=updated_quadra.get("avaliacao", 0.0),
        owner_id=updated_quadra.get("owner_id"),
        created_at=updated_quadra["created_at"],
        updated_at=updated_quadra["updated_at"]
    )

@router.delete("/{quadra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quadra(
    quadra_id: str,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_database)
):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    existing_quadra = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing_quadra:
        raise HTTPException(status_code=404, detail="Quadra not found")
    
    if existing_quadra.get("owner_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this quadra")
    
    await db.quadras.delete_one({"_id": ObjectId(quadra_id)})
    return None
