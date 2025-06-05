from pydantic import BaseModel

class UserCreate(BaseModel):
    telegram_id: str
    referral_code: str | None = None  # код того, кто пригласил (если есть)

class UserRead(BaseModel):
    telegram_id: str
    referral_code: str
    referred_by: str | None
    balance: int

    class Config:
        orm_mode = True

class NumberRead(BaseModel):
    number: str
    status: str

    class Config:
        orm_mode = True
