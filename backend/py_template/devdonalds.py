from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re
import json

import logging

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
# cookbook = None
cookbook = {"recipes": {}, "ingredients": {}, "entries": []}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = recipeName.replace("-", " ")
	recipeName = recipeName.replace("_", " ")
	recipeName = re.sub("[^A-Za-z ]", "", recipeName).title()
	recipeName = re.sub(" {2,}", " ", recipeName.strip())
	if len(recipeName) > 0:
		return recipeName
	else:
		return None

def validate_cookbook_entry(entryDict: dict) -> bool:
	entryType = entryDict["type"]
	entryName = entryDict["name"]

	if entryName in cookbook["entries"]:
		return False
	if entryType not in ("recipe", "ingredient"):
		return False

	if entryType == "recipe":
		recipeItems = entryDict["requiredItems"]
		ingredients = [item["name"] for item in recipeItems]
		if len(set(ingredients)) != len(ingredients):
			return False
		ingredients = [RequiredItem(item["name"], item["quantity"]) for item in recipeItems]
		# cookbook["recipes"][entryName] = recipeItems
		cookbook["recipes"][entryName] = Recipe(name=entryName, required_items=ingredients)
	else:
		if entryDict["cookTime"] < 0:
			return False
		# cookbook["ingredients"][entryName] = entryDict["cookTime"]
		cookbook["ingredients"][entryName] = Ingredient(name=entryName, cook_time=entryDict["cookTime"])


	cookbook["entries"].append(entryName)
	return True

# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	if validate_cookbook_entry(request.json):
		return "", 200
	else:
		return "", 400
	# TODO: implement me
	# return 'not implemented', 500


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	recipeName = request.args["name"]
	try:
		recipe = cookbook["recipes"][recipeName]
		required_items = recipe.required_items
		cooking_time = sum([cookbook["ingredients"][item.name].cook_time * item.quantity for item in required_items])
		return jsonify({"name": recipeName, "cookTime": cooking_time, "ingredients": required_items}), 200
	except KeyError:
		return "", 400
	
	
	# TODO: implement me
	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
