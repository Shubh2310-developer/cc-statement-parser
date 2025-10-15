"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100) -> List[ModelType]:
        """Get all records."""
        result = await self.session.execute(
            select(self.model).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update record."""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        """Delete record."""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False
