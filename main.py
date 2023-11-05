from fastapi import FastAPI
from authentication import router as authentication_router
from plant_monitoring import router as plant_monitoring_router

app = FastAPI()

# Define tags for different groups of endpoints
tags_metadata = [
    {"name": "Authentication", "description": "Endpoints related to user authentication"},
    {"name": "Plant Monitoring", "description": "Endpoints related to Plant Monitoring"},
]

# ROOT ENDPOINT
@app.get("/")
def read_root():
    return {"Hello World": "Hello World"}

# Include the routers without path prefixes
app.include_router(authentication_router)
app.include_router(plant_monitoring_router)
