from enum import Enum
from datetime import datetime
from typing import List, TypedDict, Union, Optional

from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ServiceModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    description: str = Field(...)
    client_price: float = Field(...)
    real_price: float = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Mantenimiento",
                "description": "Mantenimiento preventivo y correctivo",
                "client_price": 522,
                "real_price": 200
            }
        }


class ServiceDictModel(TypedDict):
    _id: str
    name: str
    description: str
    client_price: float
    real_price: float


class ProductModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    list_price: float
    discount_price: float
    image: str
    stock_number: int
    brand: str
    product_id: int
    model: str
    sat_key: int
    weight: float

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProducDictModel(TypedDict):
    _id: str
    title: str
    list_price: float
    discount_price: float
    image: str
    stock_number: int
    brand: str
    product_id: int
    model: str
    sat_key: int
    weight: float


class Client(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    location: str = Field(...)
    email: str = Field(...)
    phone_number: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuoterModel(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    date: datetime
    subtotal: float
    iva: float
    total: float
    percentage_in_advance_pay: float
    revenue_percentage: float
    first_pay: float
    second_pay: float
    description: str
    client: Client
    services: Optional[List[ServiceModel]] = []
    products: Optional[List[ProductModel]] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuoterUpdateModel(BaseModel):
    name: Optional[str]
    date: Optional[datetime]
    subtotal: Optional[float]
    iva: Optional[float]
    total: Optional[float]
    percentage_in_advance_pay: Optional[float]
    revenue_percentage: Optional[float]
    first_pay: Optional[float]
    second_pay: Optional[float]
    description: Optional[str]
    client: Optional[Client]
    services: Optional[List[ServiceModel]]
    products: Optional[List[ProductModel]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuoterDictModel(TypedDict):
    name: str
    date: datetime
    subtotal: float
    iva: float
    total: float
    percentage_in_advance_pay: float
    revenue_percentage: float
    first_pay: float
    second_pay: float
    description: str
    client: Client
    services: List[ServiceDictModel]
    products: List[ProducDictModel]


class SellModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    date: datetime
    quoter_id: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SellDictModel(TypedDict):
    id: str
    date: datetime
    quoter_id: str


class QuoterIdModel(BaseModel):
    id: PyObjectId


class ExistenceModel(TypedDict):
    nuevo: int
    asterisco: dict


class PreciosModel(TypedDict):
    precio_1: float
    precio_especial: float
    precio_descuento: float
    precio_lista: float


class ProductResponseSearchModel(TypedDict):
    producto_id: int
    modelo: str
    total_existencia: int
    titulo: str
    marca: str
    sat_key: int
    img_portada: str
    link_privado: str
    categorias: list
    pvol: float
    marca_logo: str
    link: str
    iconos: list
    peso: float
    existencia: ExistenceModel
    unidad_de_medida: dict
    alto: int
    largo: int
    ancho: int
    precios: PreciosModel
    pagina: int
    paginas: int


class MessageType(Enum):
    quoter = "Quoter"
    sell = "Sale"


class MessageFormat(BaseModel):
    type: str
    content: Union[SellModel, QuoterModel]

    class Config:
        arbitrary_types_allowed = True
