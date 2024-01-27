import dataclasses
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from app.database import db


@dataclasses.dataclass
class RgbColor:
    r: int
    g: int
    b: int


class Color(db.Model):
    __tablename__ = "colors_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    color: Mapped["RgbColor"] = composite(
        mapped_column("r"), mapped_column("g"), mapped_column("b")
    )

    def __repr__(self):
        return f"<Color: {self.color.r}, {self.color.g}, {self.color.b}>"


class ColorAssociation(db.Model):
    __tablename__ = "color_association_table"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profile_table.id"), primary_key=True
    )
    color_id: Mapped[int] = mapped_column(
        ForeignKey("colors_table.id"), primary_key=True
    )
    color: Mapped["Color"] = relationship()


class Profile(db.Model):
    __tablename__ = "profile_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    colors: Mapped[List["ColorAssociation"]] = relationship(
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Profile: {self.name}>"
