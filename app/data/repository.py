"""
repository.py

Implements a generic asynchronous repository pattern for CRUD operations on SQLAlchemy models.
Provides a BaseRepository class for common operations (create, create_many, get_last, get_last_n,
delete_by_id, truncate) and a RepositoryFactory for instantiating repositories for specific models.

Key features:
- Async CRUD operations for any SQLAlchemy model.
- Batch creation of records with create_many.
- Table truncation logic to manage table size.
- Logging for all major operations and errors.
- Designed for use with async SQLAlchemy sessions.

Dependencies:
- SQLAlchemy (select, delete, func)
- app.config (for logger setup)
"""

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.config import setup_logger

logger = setup_logger("database", indent=6)

class BaseRepository:
    """
    Generic async repository for CRUD operations on a SQLAlchemy model.
    """
    def __init__(self, model, session: Session):
        """
        Initialize the repository.

        Args:
            model: SQLAlchemy model class.
            session (Session): SQLAlchemy async session.
        """
        self.model = model
        self.session = session

    # ===== Create =====

    async def create(self, upsert=False, **kwargs):
        """
        Create or upsert a new record.

        Args:
            upsert (bool): If True, update existing record with same id.
            **kwargs: Model fields.

        Returns:
            The created or updated model instance.
        """
        if upsert and 'id' in kwargs:
            existing = await self.session.execute(
                select(self.model).where(self.model.id == kwargs['id'])
            )
            existing_obj = existing.scalar_one_or_none()
            
            if existing_obj:
                for key, value in kwargs.items():
                    if key != 'id':
                        setattr(existing_obj, key, value)
                obj = existing_obj
                logger.info(f"Updated existing {self.model.__name__} with id={kwargs['id']}")
            else:
                obj = self.model(**kwargs)
                self.session.add(obj)
                logger.info(f"Created new {self.model.__name__} with id={kwargs['id']}")
        else:
            obj = self.model(**kwargs)
            self.session.add(obj)
            logger.info(f"Created new {self.model.__name__}")

        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def create_many(self, objs: list):
        """
        Create multiple records in a single batch.

        Args:
            objs (list): List of model instances to add.

        Returns:
            List of created model instances.
        """
        self.session.add_all(objs)
        await self.session.commit()
        for obj in objs:
            await self.session.refresh(obj)
        logger.info(f"Created {len(objs)} new {self.model.__name__} records in batch.")
        return objs
    
    # ===== Read =====
    
    async def get_last(self): 
        """
        Get the most recent record.

        Returns:
            The latest model instance or None.
        """
        statement = (
            select(self.model)
            .order_by(self.model.id.desc())
            .limit(1)
        )
        result = await self.session.execute(statement) 
        logger.info(f"Fetched last {self.model.__name__} entry.")
        return result.scalars().first()

    async def get_last_n(self, n: int):
        """
        Get the last n records.

        Args:
            n (int): Number of records to fetch.

        Returns:
            List of model instances.
        """
        statement = (
            select(self.model)
            .order_by(self.model.id.desc())
            .limit(n)
        )
        result = await self.session.execute(statement)
        logger.info(f"Fetched last {n} {self.model.__name__} entries.")
        return result.scalars().all()
    
    # ===== Delete =====

    async def delete_by_id(self, obj_id: int):
        """
        Delete a record by its id.

        Args:
            obj_id (int): The id of the record to delete.
        """
        statement = delete(self.model).where(self.model.id == obj_id)
        await self.session.execute(statement)
        await self.session.commit()
        logger.info(f"Deleted {self.model.__name__} with id={obj_id}")

    async def truncate(self, max_entries: int, keep_entries: int):
        """
        Truncate table if it has more than max_entries, keeping only the last keep_entries.

        Args:
            max_entries (int): Maximum number of entries allowed before truncation.
            keep_entries (int): Number of latest entries to keep after truncation.
        """
        # Count total entries
        count_statement = select(func.count(self.model.id))
        result = await self.session.execute(count_statement)
        total_count = result.scalar()
        logger.info(f"{self.model.__name__} table has {total_count} entries (max allowed: {max_entries}).")
        
        if total_count > max_entries:
            # Get the IDs of the entries to keep (last keep_entries)
            keep_ids_statement = (
                select(self.model.id)
                .order_by(self.model.id.desc())
                .limit(keep_entries)
            )
            result = await self.session.execute(keep_ids_statement)
            keep_ids = [row[0] for row in result.fetchall()]
            
            # Delete all entries except the ones to keep
            delete_statement = delete(self.model).where(self.model.id.not_in(keep_ids))
            await self.session.execute(delete_statement)
            await self.session.commit()
            logger.info(f"Truncated {self.model.__name__}: kept {keep_entries}, deleted {total_count - keep_entries} entries.")

class RepositoryFactory:
    """
    Factory for creating repositories for different models.
    """
    def __init__(self, session):
        """
        Args:
            session: SQLAlchemy async session.
        """
        self.session = session

    def get_repository(self, model):
        """
        Get a repository for the given model.

        Args:
            model: SQLAlchemy model class.

        Returns:
            BaseRepository instance.
        """
        return BaseRepository(model, self.session)