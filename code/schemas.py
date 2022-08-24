from pydantic import BaseModel, AnyUrl


class LogInResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class Link(BaseModel):
    id: int
    short: str
    target: AnyUrl
    counter: int
