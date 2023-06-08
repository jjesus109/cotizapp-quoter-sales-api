import logging
from typing import Optional

from app.config import Config
from app.connections import create_connection, create_producer
from app.infrastructure.repository import Repository
from app.adapters.gateway import Gateway
from app.entities.models import (
    QuoterIdModel,
    QuoterModel,
    QuoterUpdateModel
)

from app.errors import (
    ElementNotFoundError,
    DBConnectionError,
    SaleRelatedError
)

import uvicorn
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status

conf = Config()
app = FastAPI()
log = logging.getLogger(__name__)
nosql_connection = create_connection()
messaging_conn = create_producer()
gateway = Gateway(
    Repository(
        nosql_connection,
        messaging_conn
    )
)


async def get_quoters():
    try:
        quoters = await gateway.get_quoters()
    except (ElementNotFoundError, DBConnectionError) as e:
        log.error(f"Could not find the quoters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find the quoters"
        )
    except Exception as e:
        log.error(f"Could not find the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not search the quoters"
        )
    return quoters


@app.get("/api/v1/quoters")
async def search_quoter_by_content(content: Optional[str] = None):
    if not content:
        return await get_quoters()
    try:
        quoter = await gateway.search_quoter_by_content(content)
    except (ElementNotFoundError, DBConnectionError) as e:
        log.error(f"Could not find a proble in database: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find a quoter"
        )
    except Exception as e:
        log.error(f"Could not find a quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find a quoter"
        )
    return quoter


@app.get("/api/v1/quoters/{quoter_id}")
async def get_quoter(quoter_id: str):
    try:
        quoter = await gateway.get_quoter(quoter_id)
    except (ElementNotFoundError, DBConnectionError) as e:
        log.error(f"Could not find the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not finde the quoter"
        )
    except Exception as e:
        log.error(f"Could not find the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not search the quoter"
        )
    return quoter


@app.post(
        "/api/v1/quoters",
        response_description="Add new quoter",
        response_model=QuoterModel)
async def insert_quoter(quoter: QuoterModel):
    try:
        quoter = await gateway.insert_quoter(quoter)
    except (ElementNotFoundError, DBConnectionError) as e:
        log.error(f"Could not create the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could create the quoter"
        )
    except Exception as e:
        log.error(f"Could not create the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create the quoter"
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=quoter
    )


@app.post(
        "/api/v1/sales",
        response_description="Add new sale"
)
async def create_sell(quoter: QuoterIdModel):
    try:
        product = await gateway.create_sell(quoter)
    except (ElementNotFoundError, DBConnectionError) as e:
        log.error(f"Could not create the product: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could create the product"
        )
    except Exception as e:
        log.error(f"Could not create the product: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create the product"
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=product
    )


@app.patch("/api/v1/quoters/{quoter_id}")
async def update_quoter(quoter_id: str, quoter: QuoterUpdateModel):
    try:
        quoter = await gateway.updated_quoter(quoter_id, quoter)
    except (ElementNotFoundError, DBConnectionError) as e:
        log.error(f"Could not update the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could update the quoter"
        )
    except SaleRelatedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could update the quoter due to a sale related "
        )
    except Exception as e:
        log.error(f"Could not update the quoter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update the quoter"
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=quoter
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")
