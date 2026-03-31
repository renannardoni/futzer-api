from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from ..models import Quadra, QuadraCreate, QuadraUpdate, HorariosSemanais, HorarioDia, SubQuadra, Reserva, User
from ..database import get_database
from ..auth import get_current_active_user

router = APIRouter(prefix="/quadras", tags=["quadras"])

_TIPO_PISO_MAP = {
    "society": "futebol", "grama": "futebol", "salao": "futsal",
    "quadra": "futebol", "campo": "futebol", "areia": "areia",
    "beach_tenis": "areia", "futebolei": "volei", "futvolei": "volei",
    "futebol": "futebol", "futsal": "futsal", "tenis": "tenis",
    "tênis": "tenis", "padel": "padel", "volei": "volei",
    "vôlei": "volei", "basquete": "basquete",
}

def _norm_tipo(q: dict) -> str:
    raw = q.get("tipoPiso") or q.get("tipo_piso") or "futebol"
    return _TIPO_PISO_MAP.get(raw.lower().strip(), raw)

def _normalize_slot(s) -> str:
    """Converte slot legado (int) para formato 'HH:MM'. Strings já em HH:MM passam direto."""
    if isinstance(s, int):
        return f"{s:02d}:00"
    return str(s)

def _horarios_from_doc(raw) -> HorariosSemanais:
    if raw and isinstance(raw, dict):
        dias = {}
        for key in ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]:
            dia = raw.get(key, {})
            if isinstance(dia, dict) and "slots" in dia:
                dias[key] = HorarioDia(slots=[_normalize_slot(s) for s in dia["slots"]])
            else:
                dias[key] = HorarioDia(slots=[])
        return HorariosSemanais(**dias)
    return HorariosSemanais()


def _slots_ocupados(hora_inicio: str, duracao: int) -> set:
    """Gera o conjunto de slots de 15 min ocupados por uma reserva."""
    h, m = map(int, hora_inicio.split(":"))
    total_min = h * 60 + m
    slots = set()
    for offset in range(0, duracao, 15):
        t = total_min + offset
        slots.add(f"{t // 60:02d}:{t % 60:02d}")
    return slots


def _has_conflict(reservas: list, quadra_id: str, data: str, hora_inicio: str, duracao: int) -> dict | None:
    """Retorna a reserva conflitante ou None."""
    new_slots = _slots_ocupados(hora_inicio, duracao)
    for r in reservas:
        if r.get("quadra_id") != quadra_id or r.get("data") != data:
            continue
        r_inicio = r.get("hora_inicio") or f"{r.get('hora', 0):02d}:00"
        r_dur = r.get("duracao", 60)
        if _slots_ocupados(r_inicio, r_dur) & new_slots:
            return r
    return None

def _subquadra_from_doc(d: dict) -> SubQuadra:
    return SubQuadra(
        id=d.get("id", ""),
        nome=d.get("nome", "Quadra"),
        tipoPiso=d.get("tipoPiso", "futebol"),
        cobertura=d.get("cobertura", "descoberto"),
        imagemCapa=d.get("imagemCapa"),
        horariosSemanais=_horarios_from_doc(d.get("horariosSemanais")),
    )

def _reserva_from_doc(d: dict) -> Reserva:
    # Retrocompatibilidade: campo legado 'hora' (int) → 'hora_inicio' (str)
    hora_inicio = d.get("hora_inicio")
    if not hora_inicio:
        hora_int = d.get("hora", 0)
        hora_inicio = f"{hora_int:02d}:00"
    return Reserva(
        id=d.get("id", ""),
        quadra_id=d.get("quadra_id", ""),
        data=d.get("data", ""),
        hora_inicio=hora_inicio,
        duracao=d.get("duracao", 60),
        nome_cliente=d.get("nome_cliente", ""),
        telefone=d.get("telefone"),
        recorrencia=d.get("recorrencia"),
        recorrencia_grupo_id=d.get("recorrencia_grupo_id"),
    )

def _to_quadra(q: dict, include_reservas: bool = True) -> Quadra:
    raw_horarios = q.get("horariosSemanais") or q.get("horarios_semanais")
    quadras_internas = [_subquadra_from_doc(sq) for sq in q.get("quadrasInternas", [])]
    reservas = [_reserva_from_doc(r) for r in q.get("reservas", [])] if include_reservas else []
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
        ativo=q.get("ativo", True),
        mostrarDisponibilidade=q.get("mostrarDisponibilidade", q.get("mostrar_disponibilidade", False)),
        horariosSemanais=_horarios_from_doc(raw_horarios),
        datasBloqueadas=q.get("datasBloqueadas", q.get("datas_bloqueadas", [])),
        quadrasInternas=quadras_internas,
        reservas=reservas,
        created_at=q["created_at"],
        updated_at=q["updated_at"],
    )


# ── Arena CRUD ─────────────────────────────────────────────────────────────────

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
    skip: int = 0, limit: int = 100,
    tipo_piso: Optional[str] = None, cidade: Optional[str] = None,
    include_inativos: bool = False,
    db=Depends(get_database)
):
    query: dict = {} if include_inativos else {"ativo": {"$ne": False}}
    if tipo_piso and tipo_piso != "todos":
        query["$or"] = [{"tipo_piso": tipo_piso}, {"tipoPiso": tipo_piso}]
    if cidade:
        query["endereco.cidade"] = {"$regex": cidade, "$options": "i"}
    cursor = db.quadras.find(query).skip(skip).limit(limit)
    quadras = await cursor.to_list(length=limit)
    return [_to_quadra(q, include_reservas=False) for q in quadras]


@router.get("/{quadra_id}", response_model=Quadra)
async def get_quadra(quadra_id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    quadra = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not quadra:
        raise HTTPException(status_code=404, detail="Quadra not found")
    # Se disponibilidade pública está desligada, não expor reservas
    mostrar = quadra.get("mostrarDisponibilidade", quadra.get("mostrar_disponibilidade", False))
    return _to_quadra(quadra, include_reservas=mostrar)


@router.post("/", response_model=Quadra, status_code=status.HTTP_201_CREATED)
async def create_quadra(
    quadra: QuadraCreate, db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    quadra_dict = quadra.dict(by_alias=True)
    quadra_dict["owner_id"] = current_user.id
    quadra_dict["created_at"] = datetime.utcnow()
    quadra_dict["updated_at"] = datetime.utcnow()
    quadra_dict.setdefault("quadrasInternas", [])
    quadra_dict.setdefault("reservas", [])
    result = await db.quadras.insert_one(quadra_dict)
    created = await db.quadras.find_one({"_id": result.inserted_id})
    return _to_quadra(created)


@router.put("/{quadra_id}", response_model=Quadra)
async def update_quadra(
    quadra_id: str, quadra_update: QuadraUpdate,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    existing = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Quadra not found")
    if current_user.id != "admin" and existing.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    update_data = {k: v for k, v in quadra_update.dict(by_alias=True, exclude_unset=True).items()}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.quadras.update_one({"_id": ObjectId(quadra_id)}, {"$set": update_data})
    updated = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    return _to_quadra(updated)


@router.delete("/{quadra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quadra(
    quadra_id: str, db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    existing = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Quadra not found")
    if current_user.id != "admin" and existing.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    await db.quadras.delete_one({"_id": ObjectId(quadra_id)})


@router.patch("/{quadra_id}/toggle-ativo")
async def toggle_ativo(
    quadra_id: str, db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(quadra_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    existing = await db.quadras.find_one({"_id": ObjectId(quadra_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Quadra not found")
    if current_user.id != "admin" and existing.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    novo_ativo = not existing.get("ativo", True)
    await db.quadras.update_one(
        {"_id": ObjectId(quadra_id)},
        {"$set": {"ativo": novo_ativo, "updated_at": datetime.utcnow()}}
    )
    return {"ativo": novo_ativo}


# ── Sub-courts (quadras internas) ───────────────────────────────────────────

@router.post("/{arena_id}/courts", status_code=201)
async def add_court(
    arena_id: str, body: dict,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    import uuid
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")

    new_court = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome", "Nova Quadra"),
        "tipoPiso": body.get("tipoPiso", "futebol"),
        "cobertura": body.get("cobertura", "descoberto"),
        "imagemCapa": body.get("imagemCapa"),
        "horariosSemanais": body.get("horariosSemanais", {
            k: {"slots": []} for k in ["seg","ter","qua","qui","sex","sab","dom"]
        }),
    }
    await db.quadras.update_one(
        {"_id": ObjectId(arena_id)},
        {"$push": {"quadrasInternas": new_court}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return new_court


@router.put("/{arena_id}/courts/{court_id}")
async def update_court(
    arena_id: str, court_id: str, body: dict,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")

    update_fields = {"updated_at": datetime.utcnow()}
    for field in ["nome", "tipoPiso", "cobertura", "imagemCapa", "horariosSemanais"]:
        if field in body:
            update_fields[f"quadrasInternas.$[c].{field}"] = body[field]

    await db.quadras.update_one(
        {"_id": ObjectId(arena_id)},
        {"$set": update_fields},
        array_filters=[{"c.id": court_id}]
    )
    return {"ok": True}


@router.delete("/{arena_id}/courts/{court_id}", status_code=204)
async def delete_court(
    arena_id: str, court_id: str,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")
    await db.quadras.update_one(
        {"_id": ObjectId(arena_id)},
        {"$pull": {"quadrasInternas": {"id": court_id}},
         "$set": {"updated_at": datetime.utcnow()}}
    )


# ── Bookings (reservas) ─────────────────────────────────────────────────────

@router.post("/{arena_id}/bookings", status_code=201)
async def add_booking(
    arena_id: str, body: dict,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    import uuid
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")

    # Retrocompatibilidade: aceitar 'hora' (int legado) ou 'hora_inicio' (str novo)
    hora_inicio = body.get("hora_inicio")
    if not hora_inicio:
        hora_int = body.get("hora")
        if hora_int is not None:
            hora_inicio = f"{int(hora_int):02d}:00"
        else:
            raise HTTPException(400, "hora_inicio é obrigatório")
    duracao = body.get("duracao", 60)

    # Verificar conflito de horário
    conflito = _has_conflict(arena.get("reservas", []), body["quadra_id"], body["data"], hora_inicio, duracao)
    if conflito:
        raise HTTPException(409, f"Horário já reservado por {conflito.get('nome_cliente', 'outro cliente')}")

    new_booking = {
        "id": str(uuid.uuid4()),
        "quadra_id": body["quadra_id"],
        "data": body["data"],
        "hora_inicio": hora_inicio,
        "duracao": duracao,
        "nome_cliente": body["nome_cliente"],
        "telefone": body.get("telefone"),
        "valor": body.get("valor"),
    }
    await db.quadras.update_one(
        {"_id": ObjectId(arena_id)},
        {"$push": {"reservas": new_booking}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return new_booking


@router.delete("/{arena_id}/bookings/{booking_id}", status_code=204)
async def delete_booking(
    arena_id: str, booking_id: str,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")
    await db.quadras.update_one(
        {"_id": ObjectId(arena_id)},
        {"$pull": {"reservas": {"id": booking_id}},
         "$set": {"updated_at": datetime.utcnow()}}
    )


@router.put("/{arena_id}/bookings/{booking_id}")
async def update_booking(
    arena_id: str, booking_id: str, body: dict,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")

    update_fields = {}
    for field in ["nome_cliente", "telefone", "valor", "hora_inicio", "duracao"]:
        if field in body:
            update_fields[f"reservas.$.{field}"] = body[field]

    if not update_fields:
        raise HTTPException(400, "Nenhum campo para atualizar")

    update_fields["updated_at"] = datetime.utcnow()
    result = await db.quadras.update_one(
        {"_id": ObjectId(arena_id), "reservas.id": booking_id},
        {"$set": update_fields}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Reserva não encontrada")
    return {"ok": True}


@router.post("/{arena_id}/bookings/recurrent", status_code=201)
async def add_recurrent_booking(
    arena_id: str, body: dict,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    import uuid

    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")

    quadra_id = body["quadra_id"]
    hora_inicio = body.get("hora_inicio")
    if not hora_inicio:
        hora_int = body.get("hora")
        if hora_int is not None:
            hora_inicio = f"{int(hora_int):02d}:00"
        else:
            raise HTTPException(400, "hora_inicio é obrigatório")
    duracao = body.get("duracao", 60)
    nome_cliente = body["nome_cliente"]
    telefone = body.get("telefone")
    dias_semana = body.get("dias_semana", [])  # [0=seg, 1=ter, ..., 6=dom]
    if not dias_semana or not isinstance(dias_semana, list):
        raise HTTPException(400, "dias_semana é obrigatório (lista de 0-6)")
    for d in dias_semana:
        if d not in range(7):
            raise HTTPException(400, f"dia_semana inválido: {d}")
    data_inicio = body["data_inicio"]  # "2026-03-22"
    data_fim = body.get("data_fim")  # opcional, default 1 ano

    # Converter dias_semana (0=seg) para weekday do Python (0=monday)
    # Já são iguais: 0=seg=monday, 6=dom=sunday
    target_weekdays = set(dias_semana)

    grupo_id = str(uuid.uuid4())
    start = datetime.strptime(data_inicio, "%Y-%m-%d")
    end = datetime.strptime(data_fim, "%Y-%m-%d") if data_fim else start + relativedelta(years=1)

    existing_reservas = arena.get("reservas", [])

    bookings = []
    conflitos = []
    current = start
    while current < end:
        if current.weekday() in target_weekdays:
            data_str = current.strftime("%Y-%m-%d")
            if _has_conflict(existing_reservas, quadra_id, data_str, hora_inicio, duracao):
                conflitos.append(data_str)
            else:
                new_b = {
                    "id": str(uuid.uuid4()),
                    "quadra_id": quadra_id,
                    "data": data_str,
                    "hora_inicio": hora_inicio,
                    "duracao": duracao,
                    "nome_cliente": nome_cliente,
                    "telefone": telefone,
                    "valor": body.get("valor"),
                    "recorrencia": "mensalista",
                    "recorrencia_grupo_id": grupo_id,
                }
                bookings.append(new_b)
                existing_reservas.append(new_b)
        current += timedelta(days=1)

    if bookings:
        # Re-ler arena para pegar estado mais recente (evitar race condition)
        arena_fresh = await db.quadras.find_one({"_id": ObjectId(arena_id)})
        fresh_reservas = arena_fresh.get("reservas", [])
        final_bookings = []
        for b in bookings:
            if _has_conflict(fresh_reservas, b["quadra_id"], b["data"], b["hora_inicio"], b["duracao"]):
                conflitos.append(b["data"])
            else:
                final_bookings.append(b)
                fresh_reservas.append(b)
        bookings = final_bookings

    # Se TODOS conflitaram, rejeitar
    if not bookings and conflitos:
        raise HTTPException(409, {
            "detail": "Todos os horários já estão reservados",
            "conflitos": len(conflitos),
            "conflitos_datas": conflitos[:10],
        })

    if bookings:
        await db.quadras.update_one(
            {"_id": ObjectId(arena_id)},
            {"$push": {"reservas": {"$each": bookings}},
             "$set": {"updated_at": datetime.utcnow()}}
        )
    return {
        "grupo_id": grupo_id,
        "count": len(bookings),
        "conflitos": len(conflitos),
        "conflitos_datas": conflitos[:10],
        "bookings": bookings,
    }


@router.delete("/{arena_id}/bookings/group/{grupo_id}", status_code=204)
async def delete_booking_group(
    arena_id: str, grupo_id: str,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    if not ObjectId.is_valid(arena_id):
        raise HTTPException(400, "Invalid ID")
    arena = await db.quadras.find_one({"_id": ObjectId(arena_id)})
    if not arena:
        raise HTTPException(404, "Arena not found")
    if current_user.id != "admin" and arena.get("owner_id") != current_user.id:
        raise HTTPException(403, "Sem permissão")
    await db.quadras.update_one(
        {"_id": ObjectId(arena_id)},
        {"$pull": {"reservas": {"recorrencia_grupo_id": grupo_id}},
         "$set": {"updated_at": datetime.utcnow()}}
    )
