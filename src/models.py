from sqlalchemy import Boolean, Column, ForeignKey, ForeignKeyConstraint, Integer, String, Table, UniqueConstraint
from .db.init_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

class ShiftTask(Base):

    __tablename__ = "shift_task"

    id: Mapped[int] = mapped_column(primary_key=True)
    closing_status: Mapped[bool]
    task: Mapped[str]
    work_center: Mapped[str]
    shift: Mapped[str]
    brigade: Mapped[str]
    batch_number: Mapped[int]
    batch_date: Mapped[date]
    nomenclature: Mapped[str]
    ekn_code: Mapped[str]
    work_center_id: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    closed_at: Mapped[datetime | None]

    __table_args__ = (UniqueConstraint("batch_number", "batch_date", name="batch_number_date_unique"),)

class Product(Base):

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_aggregated: Mapped[bool] = mapped_column(default=False)
    aggregated_at: Mapped[datetime]
    batch_number: Mapped[int]
    batch_date: Mapped[date]
    shift_task: Mapped[ShiftTask] = relationship(backref="products", foreign_keys=["batch_number", "batch_date"])
    __table_args__ = (ForeignKeyConstraint(["batch_number", "batch_date"],
                                           [ShiftTask.batch_number, ShiftTask.batch_date]),)