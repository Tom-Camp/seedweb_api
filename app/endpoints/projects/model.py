from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import db
from app.endpoints.profiles.model import Profile


class Project(db.Model):
    __tablename__ = "project_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    bed_id: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("profile_table.id"))
    profile: Mapped["Profile"] = relationship()
    start: Mapped[str] = mapped_column(String)
    end: Mapped[str] = mapped_column(String)
    data: Mapped[List["ProjectData"]] = relationship(
        back_populates="project", cascade="all, delete"
    )
    notes: Mapped[List["ProjectNotes"]] = relationship(
        back_populates="project", cascade="all, delete"
    )

    def __repr__(self):
        return f"Project: {self.name}"


class ProjectData(db.Model):
    __tablename__ = "project_data_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    sensor_data: Mapped[str] = mapped_column(String)
    project_id: Mapped[int] = mapped_column(ForeignKey("project_table.id"))
    project: Mapped["Project"] = relationship(back_populates="data")

    def __repr__(self):
        return f"Project Data: {self.id}"


class ProjectNotes(db.Model):
    __tablename__ = "project_notes_tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    note: Mapped[List[str]] = mapped_column(String)
    project_id: Mapped[int] = mapped_column(ForeignKey("project_table.id"))
    project: Mapped["Project"] = relationship(back_populates="notes")

    def __repr__(self):
        return f"Note: {self.id}"
