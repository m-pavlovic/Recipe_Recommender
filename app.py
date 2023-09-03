from fastapi import FastAPI, Depends, status, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import List, Optional
import security
import models
from database import RecipeModel, get_recipes_from_database
from models import UserDb, UserIn



app = FastAPI()

# OAuth2 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Models
class User(UserIn):
    class Config:
        allow_population_by_field_name = True

# API: Auth & Users

async def authenticated(token: str = Depends(oauth2_scheme)):
    user = await security.authenticated(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await security.login(form.username, form.password)
    if user:
        return JSONResponse(content={"access_token": user["access_token"], "token_type": "bearer"})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.post("/users", response_model=User)
async def create_user(user: User):
    hashed_password = security.hash_password(user.password)
    user_db = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    new_user_id = await insert_user(user_db)
    created_user = await get_user(new_user_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

@app.get("/users/me", response_model=User)
async def get_me(current_user: User = Depends(authenticated)):
    return current_user

# API: Recipes
@app.get("/recipes", response_model=List[RecipeModel])
async def get_recipes(
    ingredient: Optional[str] = Query(None, title="Ingredient", description="Filter recipes by ingredient"),
    dietary_restrictions: List[str] = Query([], title="Dietary Restrictions", description="Filter recipes by dietary restrictions"),
):
    # Fetch and filter recipes from the database
    recipes = await get_recipes_from_database(ingredient, dietary_restrictions)
    return recipes
