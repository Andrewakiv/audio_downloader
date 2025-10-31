import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    UPLOADING = "UPLOADING"
    DONE = "DONE"
    FAILED = "FAILED"


class AudioJob(Base):
    __tablename__ = "audio_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[str]
    user_id: Mapped[str | None]
    link: Mapped[str]
    celery_task_id: Mapped[str | None]
    # status: Mapped[JobStatus] = mapped_column(default=JobStatus.PENDING)
    filepath: Mapped[str | None]
    telegram_file_id: Mapped[str | None]
    error: Mapped[str | None]
    # created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
