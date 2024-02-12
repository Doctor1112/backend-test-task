from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator, validator
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
    closed_at: datetime | None = None
    id: int
    
class ShiftTaskOutWithProducts(BaseShiftTask):

    products: list[str] = []
    
    @validator('products', pre=True)
    def convert_products(cls, value: list[Product]):
        return [product.id for product in value]
    
class ShiftTaskOptional(BaseModel):

    closing_status: bool | None = None
    task: str | None = None
    work_center: str | None = None
    shift: str | None = None
    brigade: str | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    nomenclature: str | None = None
    ekn_code: str | None = None
    work_center_id: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class ShiftTaskEdit(ShiftTaskOptional):

    @model_validator(mode='after')
    def check_start_time_end_time(self) -> 'ShiftTaskEdit':
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValueError('start time is later than end time')
        return self

    class Config:
        from_attributes = True

class ShiftTaskFilter(ShiftTaskOptional):
    id: int | None = None
    closed_at: datetime | None = None

class ProductCreate(BaseModel):

    id: str = Field(validation_alias="УникальныйКодПродукта")
    batch_number: int = Field(validation_alias="НомерПартии")
    batch_date: date = Field(validation_alias="ДатаПартии")

    model_config = ConfigDict(
        populate_by_name=True,
    )
