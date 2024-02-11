from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator, validator
from src.models import Product

alias_map = {
    "closing_status": "СтатусЗакрытия",
    "task": "ПредставлениеЗаданияНаСмену",
    "work_center": "Линия",
    "shift": "Смена",
    "brigade": "Бригада",
    "batch_number": "НомерПартии",
    "batch_date": "ДатаПартии",
    "nomenclature": "Номенклатура",
    "ekn_code": "КодЕКН",
    "work_center_id": "ИдентификаторРЦ",
    "start_time": "ДатаВремяНачалаСмены",
    "end_time": "ДатаВремяОкончанияСмены"
}

class BaseShiftTask(BaseModel):
    closing_status: bool
    task: str
    work_center: str
    shift: str
    brigade: str
    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    work_center_id: str
    start_time: datetime
    end_time: datetime

    @model_validator(mode='after')
    def check_start_time_end_time(self) -> 'BaseShiftTask':
        if self.start_time >= self.end_time:
            raise ValueError('start time is later than end time')
        return self

    class Config:
        from_attributes = True

class ShiftTaskCreate(BaseShiftTask):

    class Config:
        alias_generator= lambda x: alias_map[x]
    
class ShiftTaskOut(BaseShiftTask):

    closed_at: datetime | None
    products: list[str]
    
    @validator('products', pre=True)
    def convert_products(cls, value: list[Product]):
        return [product.id for product in value]
