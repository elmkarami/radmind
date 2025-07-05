from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.ext.asyncio import AsyncSession

registry = {}


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        registry[cls.__name__] = cls

    @classmethod
    def patch_session(cls, session: AsyncSession):
        for factory in registry.values():
            factory._meta.sqlalchemy_session = session
            factory._meta.sqlalchemy_session_persistence = "flush"
