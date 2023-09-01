from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import motor.motor_asyncio
from bson import ObjectId
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

MONGODB_URL = os.getenv("MONGODB_URL")
print(MONGODB_URL)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.plant_monitoring


class Plant(BaseModel):
    _id: ObjectId
    name: str
    type: str
    location: str
    description: str


@app.get("/")
def read_root():
    return {"MONGODB_URL": MONGODB_URL}


# GET endpoint to retrieve all plants
@app.get("/plants/", response_description="List all plants", response_model=List[Plant])
async def get_plants():
    try:
        plants_cursor = db["plants"].find()
        plants = await plants_cursor.to_list(length=None)
        return plants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
