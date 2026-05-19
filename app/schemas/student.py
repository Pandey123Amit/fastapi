from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: str = Field(default="student", max_length=100)
    model_name: ModelName = Field(default=ModelName.alexnet)
    experience: int = Field(default=0, ge=0)
    is_active: bool = True
    skills: list[str] = Field(default_factory=list)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    role: str | None = Field(default=None, max_length=100)
    model_name: ModelName | None = None
    experience: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    skills: list[str] | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class StudentList(BaseModel):
    items: list[StudentRead]
    total: int
    skip: int
    limit: int
