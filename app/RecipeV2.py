from fastapi import FastAPI, Depends, HTTPException
import random
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import auth

import crud
import models
import schemas
from database import SessionLocal, engine
import os
if not os.path.exists('.\sqlitedb'):
    os.makedirs('.\sqlitedb')

#"sqlite:///./sqlitedb/sqlitedata.db"
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Recipe(BaseModel):
    id: int
    name: str
    diet: list
    ingredients: list[str]
    instructions: str
    cuisine: str
    cook_time: int


recipes = [
    Recipe(id=1, name="Spaghetti Carbonara", diet=["Meat"], ingredients=["egg", "spaghetti", "bacon", "pecorino"], instructions="1. Cook spaghetti according to package instructions. 2. In a separate pan, cook bacon over medium heat until crispy. 3. In a bowl, beat together egg and pecorino cheese. 4. Drain spaghetti, reserving 1 cup of the pasta water. 5. Transfer spaghetti to the pan with the bacon and add the egg mixture, stirring to coat the spaghetti. 6. If the sauce is too thick, add some of the reserved pasta water to thin it out. 7. Serve hot, garnished with additional pecorino cheese, if desired.", cuisine="Italian", cook_time=30),
    Recipe(id=2, name="Tomato Soup", diet=["Vegetarian"], ingredients=["tomatoes", "onions", "garlic", "vegetableBroth"], instructions="1. Heat a large pot over medium heat. Add diced onions and cook until translucent. 2. Add minced garlic and cook for an additional minute. 3. Add chopped tomatoes and vegetable broth to the pot. Bring to a boil, then reduce heat to low and simmer for 20-25 minutes. 4. Use an immersion blender to blend the soup until smooth. 5. Serve hot, garnished with croutons or basil, if desired.", cuisine="American", cook_time=45),
    Recipe(id=3, name="Grilled Cheese Sandwich", diet=["Dairy"], ingredients=["bread", "cheese", "butter"], instructions="1. Preheat a pan over medium heat. 2. Spread butter on one side of each slice of bread. 3. Place one slice of bread, butter-side-down, in the pan. Top with cheese, then the other slice of bread, butter-side-up. 4. Cook until the bread is golden brown and the cheese is melted, about 3-4 minutes per side. 5. Serve hot.", cuisine="American", cook_time=15),
    Recipe(id=4, name='Beef and Broccoli Stir Fry', diet=["Meat"], ingredients=['beef', 'broccoli', 'onions', 'garlic',  'olive oil', 'soy sauce', 'cornstarch'], instructions='In a small bowl, whisk together the soy sauce and cornstarch. Set aside. Heat the olive oil in a wok or large skillet over high heat. Add the beef and cook until browned, about 3 minutes. Add the broccoli, onions, and garlic and cook until the broccoli is tender, about 5 minutes. Stir in the soy sauce mixture and cook until the sauce has thickened, about 1 minute. Serve over rice.', cuisine='Chinese', cook_time=20),
    Recipe(id=5, name='Caprese Salad', diet=["Vegetarian", "Gluten free"], ingredients=['tomatoes', 'mozzarella', 'basil', 'olive oil', 'balsamic vinegar', 'salt', 'pepper'], instructions='Slice the tomatoes and mozzarella cheese into 1/4-inch thick slices. Arrange the slices on a platter, alternating between the tomatoes and mozzarella. Top with the fresh basil leaves. In a small bowl, whisk together the olive oil, balsamic vinegar, salt, and pepper. Drizzle the dressing over the salad. Serve immediately.', cuisine='Italian', cook_time=15),
    Recipe(id=6, name="Fettuccine Alfredo", diet=["Dairy"], ingredients=["fettuccine", "butter", "heavy cream", "Parmesan"], instructions="1. Cook fettuccine according to package instructions. 2. In a separate saucepan, melt butter over medium heat. Add heavy cream and grated Parmesan cheese, stirring until the cheese is melted. 3. Drain the fettuccine and add it to the saucepan with the Alfredo sauce. Toss to coat the noodles. 4. Serve hot, garnished with additional Parmesan cheese, if desired.", cuisine="Italian", cook_time=20),
    Recipe(id=7, name="Penne alla Vodka", diet=["Alcohol", "Dairy"], ingredients=["penne", "vodka", "tomatoes sauce", "heavy cream"], instructions="1. Cook penne according to package instructions. 2. In a separate saucepan, heat tomatoes sauce over medium heat. Add vodka and heavy cream, stirring to combine. 3. Drain the penne and add it to the saucepan with the vodka sauce. Toss to coat the noodles. 4. Serve hot, garnished with grated Parmesan cheese, if desired.", cuisine="Italian", cook_time=25),
    Recipe(id=8, name="Bucatini all'Amatriciana", diet=["Meat"], ingredients=["bucatini", "tomatoes sauce", "bacon", "pecorino"], instructions="1. Cook bucatini according to package instructions. 2. In a separate pan, cook bacon over medium heat until crispy. 3. Add tomatoes sauce to the pan with the bacon and simmer for 5 minutes. 4. Drain the bucatini and add it to the pan with the amatriciana sauce. Toss to coat the noodles. 5. Serve hot, garnished with grated pecorino cheese, if desired.", cuisine="Italian", cook_time=30),
    Recipe(id=9, name="Teriyaki Chicken", diet=["Meat"], ingredients=["chicken breasts", "teriyaki sauce", "ginger", "garlic", "rice", "carrot", "broccoli"], instructions="1. In a shallow dish, marinate the chicken breasts in teriyaki sauce, grated ginger, and minced garlic for at least 30 minutes. 2. Preheat the grill to medium heat. Grill the chicken for 6-8 minutes per side, or until cooked through. 3. Serve the chicken with rice and vegetables, garnished with sesame seeds and green onions, if desired.", cuisine="Japanese", cook_time=45),
    Recipe(id=10, name="Falafel Wraps", diet=["Vegetarian"], ingredients=["chickpeas", "herbs", "spices", "pita bread", "lettuce", "tomatoes", "tahini sauce"], instructions="1. In a food processor, pulse together chickpeas, herbs, and spices until well combined. Form the mixture into balls and fry in oil until browned on all sides. 2. Warm the pita bread. 3. Assemble the wraps by placing the falafel balls, lettuce, tomatoes, and tahini sauce inside the pita bread. 4. Serve hot.", cuisine="Middle Eastern", cook_time=30),
    Recipe(id=11, name="Beef Stroganoff", diet=["Meat"], ingredients=["beef", "mushrooms", "sour cream", "egg noodles"], instructions="1. Cut beef into thin strips and season with salt and pepper. 2. In a large pan, cook the beef over medium heat until it is browned. 3. Add sliced mushrooms to the pan and cook for an additional 5 minutes. 4. Stir in sour cream until the sauce is creamy. 5. Cook egg noodles according to package instructions. 6. Serve the beef stroganoff over the cooked noodles.", cuisine="Russian", cook_time=30),
    Recipe(id=12, name="Shakshuka", diet=["Vegetarian"], ingredients=["egg", "tomatoes", "onions", "spices"], instructions="1. In a large skillet, sauté diced onions over medium heat until they are softened. 2. Add diced tomatoes and spices to the skillet and simmer for 10 minutes. 3. Crack egg into the skillet and cover with a lid. Cook until the egg are set to your desired level of doneness. 4. Serve the shakshuka with pita bread or crusty bread for dipping.", cuisine="Middle Eastern", cook_time=20),
    Recipe(id=13, name="Taco Salad", diet=["Meat"], ingredients=["ground beef", "lettuce", "tomatoes", "cheddar cheese", "taco seasoning", "tortilla chips"], instructions="1. In a large pan, cook ground beef over medium heat until it is browned. 2. Add taco seasoning to the pan and stir to coat the beef. 3. In a large bowl, combine lettuce, diced tomatoes, and shredded cheddar cheese. 4. Top the salad with the seasoned ground beef and crushed tortilla chips. 5. Serve with your choice of dressing.", cuisine="Mexican", cook_time=20),
    Recipe(id=14, name="Chocolate Chip Cookies", diet=["Dairy"], ingredients=["flour", "baking soda", "salt", "butter", "sugar", "brown sugar", "egg", "vanilla extract", "chocolate chips"], instructions="1. Preheat the oven to 350°F (180°C). 2. In a medium bowl, whisk together flour, baking soda, and salt. 3. In a separate large bowl, cream together butter, sugar, and brown sugar until smooth. 4. Beat in egg, one at a time, followed by the vanilla extract. 5. Gradually add the dry ingredients to the wet ingredients and mix until well combined. 6. Stir in chocolate chips. 7. Drop the dough by rounded tablespoonfuls onto ungreased baking sheets. 8. Bake for 8-10 minutes, or until the edges are lightly golden. 9. Allow the cookies to cool on the baking sheet for a few minutes before removing them to a wire rack to cool completely.", cuisine="American", cook_time=10),
    Recipe(id=15, name="Baked Ziti", diet=["Meat", "Dairy"], ingredients=["ziti", "ground beef", "marinara sauce", "ricotta cheese", "mozzarella cheese"], instructions="1. Preheat the oven to 350°F. 2. Cook the ziti according to package instructions. 3. In a separate pan, cook the ground beef over medium heat until it is browned. 4. Stir in marinara sauce and simmer for 5 minutes. 5. In a large mixing bowl, combine the cooked ziti, ground beef mixture, and ricotta cheese. 6. Transfer the mixture to a baking dish and top with shredded mozzarella cheese. 7. Bake for 20 minutes, or until the cheese is melted and bubbly. 8. Serve hot.", cuisine="Italian", cook_time=60),
    Recipe(id=16, name="Quinoa Stir-Fry", diet=["Dairy free"], ingredients=["quinoa", "vegetables", "tofu", "soy sauce", "ginger"], instructions="1. Cook the quinoa according to package instructions. 2. In a separate pan, heat a small amount of oil over medium heat. Add your choice of vegetables and sauté until they are tender. 3. Add diced tofu to the pan and cook for an additional 5 minutes. 4. Stir in soy sauce and grated ginger. 5. Serve the stir-fry over the cooked quinoa.", cuisine="Asian", cook_time=30),
    Recipe(id=17, name="Quinoa and Black Bean Salad", diet=["Dairy free", "Gluten free"], ingredients=["quinoa", "black beans", "corn", "red pepper", "avocado", "lime juice", "cilantro"], instructions="1. Cook the quinoa according to package instructions. 2. In a large mixing bowl, combine the cooked quinoa, black beans, corn, diced red pepper, and diced avocado. 3. Squeeze the juice of one lime over the salad and add chopped cilantro. 4. Toss to combine and serve chilled or at room temperature.", cuisine="Mexican", cook_time=30),
    Recipe(id=18, name="Thai Green Curry with Tofu", diet=["Dairy free"], ingredients=["tofu", "green curry paste", "coconut milk", "bell peppers", "bamboo shoots", "basil"], instructions="1. Press the tofu to remove excess moisture. Cut the tofu into small cubes. 2. In a large pan, heat green curry paste over medium heat. Add coconut milk and stir to combine. 3. Add the tofu, bell peppers, and bamboo shoots to the pan. Simmer for 10 minutes. 4. Stir in basil leaves and serve the curry over rice.", cuisine="Thai", cook_time=30),
    Recipe(id=19, name="Peanut Noodles", diet=["Peanut"], ingredients=["noodles", "peanut butter", "soy sauce", "sriracha", "lime juice", "sugar", "garlic"], instructions="1. Cook noodles according to package instructions. 2. In a small saucepan, whisk together peanut butter, soy sauce, sriracha, lime juice, sugar, and minced garlic. Heat the sauce over medium heat until it is smooth and well combined. 3. Drain the noodles and toss them with the peanut sauce. 4. Serve the peanut noodles hot, garnished with chopped peanuts and green onions, if desired.", cuisine="Asian", cook_time=15),
    Recipe(id=20, name="Teriyaki Salmon", diet=["Seafood"], ingredients=["salmon", "teriyaki sauce", "brown sugar", "ginger", "garlic"], instructions="1. Preheat the oven to 400°F. Line a baking sheet with parchment paper. 2. In a small bowl, whisk together teriyaki sauce, brown sugar, minced ginger, and minced garlic. 3. Place the salmon on the prepared baking sheet and brush it with the teriyaki sauce mixture. 4. Bake the salmon for 10-12 minutes, or until it is cooked to your desired level of doneness. 5. Serve the salmon hot, garnished with sesame seeds and green onions, if desired.", cuisine="Asian", cook_time=15),
    Recipe(id=21, name="Lemon Garlic Shrimp", diet=["Seafood"], ingredients=["shrimp", "lemon", "garlic", "parsley", "olive oil"], instructions="1. Preheat a large skillet over medium heat. 2. Peel and devein the shrimp, leaving the tails on. 3. In a small bowl, whisk together the juice of 1 lemon, minced garlic, chopped parsley, and a drizzle of olive oil. 4. Add the shrimp to the hot skillet and pour the lemon garlic mixture over top. 5. Cook the shrimp for 2-3 minutes on each side, or until they are pink and opaque. 6. Serve the shrimp hot, garnished with additional lemon wedges and parsley, if desired.", cuisine="Italian", cook_time=15),
    Recipe(id=22, name="Quinoa and Black Bean Burger", diet=["Gluten free"], ingredients=["quinoa", "black beans", "egg", "onions", "cilantro", "cumin", "salt"], instructions="1. Rinse and drain the quinoa and black beans. 2. In a food processor, pulse the quinoa, black beans, egg, diced onions, cilantro, cumin, and salt until the mixture comes together. 3. Form the mixture into patties. 4. Heat a large skillet over medium heat. Add the patties to the skillet and cook for 4-5 minutes on each side, or until they are crispy and golden brown. 5. Serve the burgers on gluten-free buns with your choice of toppings.", cuisine="Mexican", cook_time=20),
    Recipe(id=23, name="Grilled Chicken with Mango Salsa", diet=["Gluten free"], ingredients=["chicken breasts", "mango", "red onions", "jalapeño", "cilantro", "lime juice", "olive oil", "salt"], instructions="1. Preheat a grill to medium-high heat. 2. In a small bowl, combine diced mango, diced red onions, minced jalapeño, chopped cilantro, the juice of 1 lime, and a drizzle of olive oil. Season the salsa with salt to taste. 3. Season the chicken breasts with salt and grill them for 6-8 minutes on each side, or until they are cooked through. 4. Serve the grilled chicken with the mango salsa on top.", cuisine="Mexican", cook_time=20)
]

#Recipe endpoints

@app.get("/recipes")
def read_recipes():
    return recipes

@app.get("/recipes/{id}")
def read_recipe(id: int):
    for recipe in recipes:
        if recipe.id == id:
            return recipe
    return {"error": "Recipe not found"}

@app.get("/recipes/cuisine/{cuisine}")
def read_recipes_by_cuisine(cuisine: str):
    result = []
    for recipe in recipes:
        if recipe.cuisine.lower() == cuisine.lower():
            result.append(recipe)
    return result

@app.get("/recipes/diet/{diet}")
def read_recipes_by_diet(diet: str):
    result = []
    for recipe in recipes:
        if recipe.diet == diet:
            result.append(recipe)
    return result

@app.get("/recipes/ingredients/{ingredient}")
def read_ingredient(ingredient: str = None):
    result = []
    if ingredient is None:
        return recipes
    else:
        return [recipe for recipe in recipes if ingredient in recipe.ingredients]

@app.get("/recipes/cook_time/{max_time}")
def read_max_time(max_time: int):
    result = []
    for recipe in recipes:
        if recipe.cook_time <= max_time:
            result.append(recipe)
    return result


@app.post("/recipes")
def create_recipe(recipe: Recipe):
    new_recipe = {
        'id': len(recipes) + 1,
        'name': recipe.name,
        'diet': recipe.diet,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'cuisine': recipe.cuisine,
        'cook_time': recipe.cook_time
    }
    rec = Recipe(**new_recipe)
    recipes.append(rec)

    return new_recipe

@app.post("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: Recipe):
    for i, r in enumerate(recipes):
        if r.id == recipe_id:
            recipes[i] = recipe
            return {"id": recipe_id, "name": recipe.name}
    return {"error": "Recipe not found"}

@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: Recipe):
    existing_recipe = next((r for r in recipes if r.id == recipe_id), None)
    if existing_recipe is None:
        return {"error": "Recipe not found"}

    existing_recipe.name = recipe.name
    existing_recipe.diet = recipe.diet
    existing_recipe.ingredients = recipe.ingredients
    existing_recipe.instructions = recipe.instructions
    existing_recipe.cuisine = recipe.cuisine
    existing_recipe.cook_time = recipe.cook_time

    return existing_recipe


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):

    recipe = next((r for r in recipes if r.id == recipe_id), None)
    if recipe is None:
        return {"error": "Recipe not found"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user