from typing import Any, List
from abc import ABC, abstractmethod


class RepositoryInterface(ABC):

    @abstractmethod
    async def search_quoter_by_content(self, content: str) -> List[Any]:
        """Search a quoter by the content of it

        Args:
            content (str): content word to search in quoters

        Returns:
            List[Any]: matches with the quoters
        """

    @abstractmethod
    async def get_quoters(self) -> List[Any]:
        """Get all quoters

        Returns:
            List[Any]: All quoters created
        """

    @abstractmethod
    async def get_quoter(self, quoter_id: str) -> Any:
        """Word to search into product catalog

        Args:
            quoter_id (str): quoter id to find

        Returns:
            Any: Quoter information found
        """

    @abstractmethod
    async def insert_quoter(self, quoter: Any) -> Any:
        """Insert quoter in database

        Args:
            quoter (Any): quoter to insert in DB

        Returns:
            Any: Quoter inserted
        """

    @abstractmethod
    async def update_quoter(self, quoter_id: str, quoter: Any) -> Any:
        """Update and existing quoter that are not related to a sell

        Args:
            quoter_id (str): quoter id to update
            quoter (Any): quoter data to update

        Returns:
            Any: Quoter data updated
        """

    @abstractmethod
    async def create_sell(self, quoter_id: str):
        """Create a sell in DB

        Args:
            quoter_id (str): quoter to mark as a sell

        """

    @abstractmethod
    async def find_sell_by_quoter(self, quoter_id: str) -> Any:
        """Get a sale by quoter id

        Args:
            quoter_id (str): Quoter to find in sales

        Returns:
            Any: Sale found
        """
    @abstractmethod
    async def notify(self, quoter_sell: Any, _type: str):
        """Notify quoter or sell into message system

        Args:
            quoter_sell (Any): quoter or sell data to notify
            _type (str): type of data to notify
        """
