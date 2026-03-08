from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from pydantic import BaseModel, EmailStr
from ..models import User, UserCreate, Token
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, create_reset_token, verify_reset_token
from ..database import get_database
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db = Depends(get_database)):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    
    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    
    return User(
        id=str(created_user["_id"]),
        email=created_user["email"],
        nome=created_user["nome"],
        created_at=created_user["created_at"],
        is_active=created_user["is_active"]
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password", status_code=200)
async def forgot_password(body: ForgotPasswordRequest, db=Depends(get_database)):
    user = await db.users.find_one({"email": body.email})
    # Sempre retorna 200 para não vazar se o email existe
    if not user:
        return {"message": "Se este email estiver cadastrado, você receberá um link em breve."}

    token = create_reset_token(body.email)
    reset_url = f"{settings.frontend_url}/owner/reset-password?token={token}"

    if settings.resend_api_key:
        try:
            import resend
            resend.api_key = settings.resend_api_key
            resend.Emails.send({
                "from": settings.from_email,
                "to": [body.email],
                "subject": "Redefinir senha — Futzer",
                "html": f"""
                <div style="font-family:sans-serif;max-width:480px;margin:auto">
                  <h2 style="color:#16a34a">Futzer</h2>
                  <p>Recebemos um pedido para redefinir a senha da sua conta.</p>
                  <p>Clique no botão abaixo para criar uma nova senha. O link expira em <strong>1 hora</strong>.</p>
                  <a href="{reset_url}" style="display:inline-block;margin:20px 0;padding:12px 28px;background:#16a34a;color:white;border-radius:8px;text-decoration:none;font-weight:bold">
                    Redefinir senha
                  </a>
                  <p style="color:#888;font-size:12px">Se você não solicitou isso, ignore este email.</p>
                </div>
                """,
            })
        except Exception:
            pass  # Não expõe erro de envio ao cliente

    return {"message": "Se este email estiver cadastrado, você receberá um link em breve."}


@router.post("/reset-password", status_code=200)
async def reset_password(body: ResetPasswordRequest, db=Depends(get_database)):
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="A senha deve ter pelo menos 6 caracteres")

    email = verify_reset_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Link inválido ou expirado")

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    await db.users.update_one(
        {"email": email},
        {"$set": {"hashed_password": get_password_hash(body.new_password)}}
    )
    return {"message": "Senha redefinida com sucesso"}
