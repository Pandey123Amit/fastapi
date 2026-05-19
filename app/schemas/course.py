from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    max_marks: int = Field(default=100, ge=0, le=10000)
    professor_code: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    max_marks: int | None = Field(default=None, ge=0, le=10000)
    professor_code: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None


class CourseRead(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CourseList(BaseModel):
    items: list[CourseRead]
    total: int
    skip: int
    limit: int
