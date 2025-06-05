from sqlalchemy.future import select
from models import User, Number
import random
import string

async def get_user_by_telegram_id(db, telegram_id: str):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_user(db, telegram_id: str, referred_by: str | None = None):
    # Генерируем уникальный реферальный код
    def gen_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    referral_code = gen_code()

    # Проверяем уникальность (упрощенно, в продакшене надо сделать проверку цикла)
    existing_user = await get_user_by_telegram_id(db, telegram_id)
    if existing_user:
        return existing_user

    user = User(telegram_id=telegram_id, referral_code=referral_code, referred_by=referred_by, balance=0)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def add_bonus_for_referrer(db, referred_by_code: str):
    result = await db.execute(select(User).where(User.referral_code == referred_by_code))
    referrer = result.scalars().first()
    if referrer:
        referrer.balance += 10  # например +10 бонусов
        await db.commit()
    return referrer
