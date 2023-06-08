import asyncio
import logging
from typing import List, Union
from dataclasses import dataclass

from app.config import Config
from app.errors import (
    ElementNotFoundError,
    InsertionError,
    DBConnectionError
)
from app.entities.models import (
    MessageFormat,
    MessageType,
    QuoterDictModel,
    QuoterModel,
    SellModel
)
from app.infrastructure.repository_i import RepositoryInterface

from pydantic import BaseSettings
from confluent_kafka import Producer
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import (
    ConnectionFailure,
    ExecutionTimeout
)


log = logging.getLogger(__name__)
EMPTY_COUNT = 0


@dataclass
class Repository(RepositoryInterface):

    nosql_conn: AsyncIOMotorDatabase
    messaging_con: Producer
    config: BaseSettings = Config()

    async def search_quoter_by_content(
        self,
        content: str
    ) -> List[QuoterDictModel]:
        try:
            (
                name_match,
                description_match,
                services_match,
                products_match
            ) = await asyncio.gather(
                self.nosql_conn["quoters"].find(
                    {
                        "name": {
                            "$regex": content,
                            "$options": "mxsi"
                        }
                    }
                ).to_list(self.config.max_search_elements),
                self.nosql_conn["quoters"].find(
                    {
                        "description": {
                            "$regex": content,
                            "$options": "mxsi"
                        }
                    }
                ).to_list(self.config.max_search_elements),
                self.nosql_conn["quoters"].find(
                    {
                        "services.name": {
                            "$regex": content,
                            "$options": "mxsi"
                        }
                    }
                ).to_list(self.config.max_search_elements),
                self.nosql_conn["quoters"].find(
                    {
                        "products.title": {
                                "$regex": content,
                                "$options": "mxsi"
                        }
                    }
                ).to_list(self.config.max_search_elements)
            )
        except (ConnectionFailure, ExecutionTimeout):
            raise DBConnectionError(
                "Could not found service in DB"
            )
        return [
            *name_match,
            *description_match,
            *services_match,
            *products_match]

    async def get_quoters(self) -> List[QuoterDictModel]:
        try:
            quoters = await self.nosql_conn["quoters"].find().to_list(
                self.config.max_search_elements
            )
        except (ConnectionFailure, ExecutionTimeout):
            raise DBConnectionError(
                "Quoter not found in DB"
            )
        if quoters.__len__() == EMPTY_COUNT:
            raise ElementNotFoundError(
                "Quoter not found in DB"
            )
        return quoters

    async def get_quoter(self, quoter_id: str) -> QuoterDictModel:
        try:
            quoter = await self.nosql_conn["quoters"].find_one(
                {"_id": quoter_id}
            )
        except (ConnectionFailure, ExecutionTimeout):
            raise DBConnectionError(
                "Quoter not found in DB"
            )
        if not quoter:
            raise ElementNotFoundError(
                "Quoter not found in DB"
            )
        return quoter

    async def insert_quoter(self, quoter: QuoterModel) -> QuoterDictModel:
        quoter = jsonable_encoder(quoter)
        try:
            await self.nosql_conn["quoters"].insert_one(quoter)
        except (ConnectionFailure, ExecutionTimeout):
            raise InsertionError("Could not insert quoter in DB")
        return quoter

    async def update_quoter(self, quoter_id: str, quoter: QuoterModel):
        query = {"_id": quoter_id}
        values = {
            "$set": quoter.dict(exclude_unset=True)
        }
        try:
            await self.nosql_conn["quoters"].update_one(query, values)
        except (ConnectionFailure, ExecutionTimeout):
            raise InsertionError("Could not update quoter in DB")

    async def create_sell(self, sell: SellModel):
        sell = jsonable_encoder(sell)
        try:
            await self.nosql_conn["sales"].insert_one(sell)
        except (ConnectionFailure, ExecutionTimeout):
            raise InsertionError("Could not insert quoter in DB")
        return sell

    async def find_sell_by_quoter(self, quoter_id: str):
        try:
            quoter = await self.nosql_conn["sales"].find_one(
                {"quoter_id": quoter_id}
            )
        except (ConnectionFailure, ExecutionTimeout):
            raise DBConnectionError(
                "Quoter not found in DB"
            )
        if not quoter:
            raise ElementNotFoundError(
                "Quoter not found in DB"
            )
        return quoter

    async def notify(
        self,
        quoter_sell: Union[SellModel, QuoterModel],
        _type: MessageType
    ):
        message = MessageFormat(
            type=_type.value,
            content=quoter_sell)
        self.messaging_con.produce(
            self.config.kafka_topic,
            message.json(encoder=str).encode("utf-8")
        )
        self.messaging_con.flush()
