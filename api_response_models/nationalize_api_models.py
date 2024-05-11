from typing import List
from pydantic import BaseModel

class CountryPrediction(BaseModel):
  country_id: str
  probability: float

class NationalizeResponse(BaseModel):
  count: int
  name: str 
  country: List[CountryPrediction]

class ErrorResponse(BaseModel):
  error: str