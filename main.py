from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
import crud, models, schemas
import requests
import asyncio

app = FastAPI()

SMS_ACTIVATE_TOKEN = "9f8428741cA4d50cf8403e6d4d06bff9"

@app.on_event("startup")
async def startup():
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/register", response_model=schemas.UserRead)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_telegram_id(db, user.telegram_id)
    if existing:
        return existing

    if user.referral_code:
        await crud.add_bonus_for_referrer(db, user.referral_code)

    new_user = await crud.create_user(db, user.telegram_id, user.referral_code)
    return new_user

@app.get("/get_number")
async def get_number(telegram_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Запрос к SMS-Activate API
    url = f"https://sms-activate.org/stubs/handler_api.php?api_key={SMS_ACTIVATE_TOKEN}&action=getNumber&service=ot&country=0"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get number")

    # Пример ответа: ACCESS_NUMBER:1234567890:id
    if "ACCESS_NUMBER" not in response.text:
        raise HTTPException(status_code=500, detail="Failed to get number")

    parts = response.text.split(":")
    number = parts[1]

    # Сохраняем номер в БД
    db_number = models.Number(number=number, status="active", owner_id=user.id)
    db.add(db_number)
    await db.commit()
    await db.refresh(db_number)

    return {"number": number}
