from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, json
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


# START OF ENDPOINTS AND CLASSES FOR PLANT

class Plant(BaseModel):
    id: str
    name: str
    type: str
    location: str
    description: str


class CreatePlant(BaseModel):
    _id: ObjectId
    name: str
    type: str
    location: str
    description: str


@app.get("/")
def read_root():
    return {"MONGODB_URL": MONGODB_URL}


# GET endpoint to retrieve all plants
@app.get("/GetPlants/", response_description="List all plants", response_model=List[Plant])
async def get_plants():
    try:
        # Use the aggregation framework to convert _id to string
        pipeline = [
            {
                "$project": {
                    "id": {
                        "$toString": "$_id"
                    },
                    "name": 1,
                    "type": 1,
                    "location": 1,
                    "description": 1
                }
            }
        ]

        # Apply the aggregation pipeline to the collection
        plants_cursor: motor.motor_asyncio.AsyncIOMotorCollection = db["plants"].aggregate(
            pipeline)

        plants = await plants_cursor.to_list(length=None)
        return plants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET endpoint to get a plant
@app.get("/GetPlant", response_description="Get a plant", response_model=Plant)
async def get_plant(request_body: dict):
    try:
        # Use the aggregation framework to convert _id to string
        plant_id = request_body.get("id")

        # Ensure that the plant_id is provided in the request body
        if not plant_id:
            return Response(content="Plant ID not provided in the request body", status_code=status.HTTP_400_BAD_REQUEST)

        # Convert the provided plant_id to an ObjectId
        plant_object_id = ObjectId(plant_id)

        pipeline = [
            {
                "$match": {
                    "_id": plant_object_id
                }
            },
            {
                "$project": {
                    "id": {
                        "$toString": "$_id"
                    },
                    "name": 1,
                    "type": 1,
                    "location": 1,
                    "description": 1
                }
            }
        ]

        try:
            plant = await db["plants"].aggregate(pipeline).next()
            return plant
        except:
            return Response(content="Plant not found", status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# PUT endpoint to update a plant
@app.put("/UpdatePlant/", response_description="Update a plant by ID", response_model=Plant)
async def update_plant(updated_plant: Plant):
    try:
        plant_id = updated_plant.id
        plant_object_id = ObjectId(plant_id)

        existing_plant = await db["plants"].find_one({"_id": plant_object_id})

        if existing_plant is None:
            return Response(content="Plant not found", status_code=status.HTTP_400_BAD_REQUEST)

        update_data = updated_plant.model_dump(exclude={"id"})

        # Update the plant with the provided data
        update_response = await db["plants"].update_one({"_id": plant_object_id}, {"$set": update_data})

        update_details = {
            "plant_id": plant_id,
            "matchedCount": update_response.matched_count,
            "modifiedCount": update_response.modified_count,
            "upsertedId": str(update_response.upserted_id),
            "acknowledged": update_response.acknowledged,
        }

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=update_details)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DELETE endpoint to delete a plant
@app.delete("/DeletePlant/", response_description="Delete a plant by ID")
async def delete_plant(request_body: dict):
    try:
        # Use the aggregation framework to convert _id to string
        plant_id = request_body.get("id")

        # Ensure that the plant_id is provided in the request body
        if not plant_id:
            return Response(content="Plant ID not provided in the request body", status_code=status.HTTP_400_BAD_REQUEST)

        # Convert the provided plant_id to an ObjectId
        plant_object_id = ObjectId(plant_id)

        # Check if the plant with the provided ID exists
        existing_plant = await db["plants"].find_one({"_id": plant_object_id})
        if existing_plant is None:
            return Response(content="Plant not found", status_code=status.HTTP_400_BAD_REQUEST)

        # Delete the plant with the provided ID
        delete_result = await db["plants"].delete_one({"_id": plant_object_id})

        # Check if the deletion was successful
        if delete_result.deleted_count == 1:
            delete_details = {
                "message": "Plant deleted successfully",
                "plant_id": plant_id,
                "acknowledged": delete_result.acknowledged,
                "deletedCount": delete_result.deleted_count
            }
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=delete_details)
        else:
            raise HTTPException(
                status_code=500, detail="Failed to delete plant")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST endpoint to add a new plant
@app.post("/CreatePlant/", response_description="Add a new plant", response_model=CreatePlant)
async def create_plant(plant: CreatePlant):
    try:
        plant = jsonable_encoder(plant)
        new_plant = await db["plants"].insert_one(plant)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"_id": str(new_plant.inserted_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# END OF ENDPOINTS AND CLASSES FOR PLANT
