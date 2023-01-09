from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    name: str = Field(..., max_length=255)
    diet: str = Field(..., max_length=255)
    ingredients: str = Field(..., max_length=255)
    instructions: str = Field(..., max_length=10000)
    cuisine: str = Field(..., max_length=255)
    cook_time: int = Field(..., ge=0)

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True