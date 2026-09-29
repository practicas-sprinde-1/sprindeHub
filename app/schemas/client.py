from pydantic import BaseModel, Field, ConfigDict


class ClientBase(BaseModel):
    name:str = Field(
        min_length=1,
        max_length=120,
    )

    cif:str|None = Field(
        max_length=120,
        default=None,
    )

    phone:str = Field(
        min_length=1,
        max_length=120
    )


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name:str| None = Field(
        default=None,
        min_length=1,
        max_length=120
    )

    cif:str|None=Field(
        default=None,
        max_length=120
    )

    phone:str|None = Field(
        default=None,
        min_length=1,
        max_length=120
    )

class ClientRead(ClientBase):
    id:int

    #Permite crear el DTO desde un objeto con atributos
    # dto = ClientRead.model_validate(product_orm)
    model_config = ConfigDict(
        from_attributes=True
    )
