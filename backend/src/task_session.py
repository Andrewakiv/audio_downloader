import celery
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from common.settings import config

ENGINE = create_engine(
    config.sync_db_url,
    pool_size=10,
    max_overflow=10
)
SessionFactory = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, expire_on_commit=False)


class TaskFactory(celery.Task):
    _SessionFactory: sessionmaker = SessionFactory

    def __call__(self, *args, **kwargs):
        self.request._db_session = self._SessionFactory()
        try:
            return self.run(*args, **kwargs)
        except SQLAlchemyError:
            self.request._db_session.rollback()
            raise
        except Exception:
            try:
                self.request._db_session.rollback()
            except Exception:
                pass
            raise
        finally:
            self.request._db_session.close()
            del self.request._db_session

    @property
    def session(self) -> Session:
        try:
            return self.request._db_session
        except AttributeError:
            raise RuntimeError("DB session is not initialized for this task execution")
