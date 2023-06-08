from typing import Any, List
from datetime import datetime
from dataclasses import dataclass

from app.entities.models import (
    QuoterDictModel,
    SellModel,
    QuoterModel,
    MessageType,
    QuoterIdModel
)
from app.config import Config
from app.adapters.gateway_i import GatewayInterface
from app.infrastructure.repository_i import RepositoryInterface
from app.errors import SaleRelatedError, ElementNotFoundError

from pydantic import BaseSettings
from fastapi.encoders import jsonable_encoder


@dataclass
class Gateway(GatewayInterface):

    repository: RepositoryInterface
    conf: BaseSettings = Config()

    async def search_quoter_by_content(
        self,
        content: str
    ) -> List[QuoterDictModel]:
        return await self.repository.search_quoter_by_content(content)

    async def get_quoters(self) -> List[QuoterDictModel]:
        return await self.repository.get_quoters()

    async def get_quoter(self, quoter_id: str) -> QuoterDictModel:
        return await self.repository.get_quoter(quoter_id)

    async def insert_quoter(self, quoter: QuoterModel) -> QuoterDictModel:
        if self.conf.stream_consume:
            product_type = MessageType.quoter
            await self.repository.notify(quoter, product_type)
            response = jsonable_encoder(quoter)
        else:
            response = await self.repository.insert_quoter(quoter)
        return response

    async def updated_quoter(
        self,
        quoter_id: str,
        quoter: Any
    ) -> QuoterDictModel:
        try:
            await self.repository.find_sell_by_quoter(quoter_id)
        except ElementNotFoundError:
            if self.conf.stream_consume:
                quoter_got = await self.repository.get_quoter(quoter_id)
                quoter_model = QuoterDictModel(**quoter_got)
                new_quoter_data = quoter.dict(exclude_unset=True)
                updated_quoter = quoter_model.copy(update=new_quoter_data)
                quoter_type = MessageType.quoter
                await self.repository.notify(
                    updated_quoter,
                    quoter_type
                )
                updated_quoter = jsonable_encoder(updated_quoter)
            else:
                await self.repository.update_quoter(
                    quoter_id,
                    quoter
                )
                updated_quoter = await self.repository.get_quoter(
                    quoter_id
                )
            return updated_quoter
        raise SaleRelatedError("Sale is related to this quoter")

    async def create_sell(self, quoter: QuoterIdModel):
        sell = SellModel(
            date=datetime.utcnow(),
            quoter_id=quoter.id.__str__()
        )
        if self.conf.stream_consume:
            product_type = MessageType.sell
            await self.repository.notify(sell, product_type)
            response = jsonable_encoder(sell)
        else:
            response = await self.repository.create_sell(sell)
        return response
