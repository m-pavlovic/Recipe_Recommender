import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from pydantic import BaseModel

# Define a Pydantic model for the Recipe
class RecipeModel(BaseModel):
    id: int
    name: str
    ingredients: List[str]
    cuisine: str
    dietary_restrictions: List[str]

# Initialize the MongoDB database connection
mongodb_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = mongodb_client.fastAPIApp  # Use the desired database name here
print("Connected to the MongoDB database!")

# Get recipes from the database
async def get_recipes_from_database(
    ingredient: Optional[str] = None,
    dietary_restrictions: List[str] = [],
):

    # Fetch recipes from MongoDB
    recipes_cursor = db["recipes"].find({})
    recipes = [RecipeModel(**recipe) for recipe in await recipes_cursor.to_list(length=None)]

    # Filter recipes based on ingredient and dietary restrictions
    filtered_recipes = []
    for recipe in recipes:
        if not set(dietary_restrictions).difference(recipe.dietary_restrictions):
            if ingredient is None or ingredient in recipe.ingredients:
                filtered_recipes.append(recipe)
    return filtered_recipes
