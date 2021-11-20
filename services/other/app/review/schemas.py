import datetime

from pydantic import BaseModel, Field, validator


class CreateReview(BaseModel):
    """ Review create """

    text: str
    appraisal: int = Field(default=1, gt=0, lt=6)


class GetReview(CreateReview):
    """ Get review """

    id: int
    user_id: int
    created_at: datetime.datetime

    @validator('created_at')
    def validate_created_at(cls, created_at: datetime.datetime):
        """ Validate created at """
        return f'{created_at}Z'.replace(' ', 'T')
