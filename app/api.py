"""
Flask API for Cooking Assistant
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime

from app.agents.cooking_agent import CookingAssistantAgent, create_cooking_agent
from app.data.recipes import (
    RECIPES_DB, INGREDIENTS_DB, TECHNIQUES_DB,
    search_recipes, get_recipes_by_ingredient,
    Cuisine, Difficulty, DietaryTag
)


def create_app():
    app = Flask(__name__,
                static_folder='../static',
                template_folder='../templates')
    CORS(app)

    agents = {}

    def get_agent(session_id: str) -> CookingAssistantAgent:
        if session_id not in agents:
            agents[session_id] = create_cooking_agent()
        return agents[session_id]

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'cooking-assistant',
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.json
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        try:
            agent = get_agent(session_id)
            response = agent.chat(message)

            return jsonify({
                'response': response,
                'session_id': session_id
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/recipes', methods=['GET'])
    def list_recipes():
        """List all recipes."""
        recipes = []
        for key, recipe in RECIPES_DB.items():
            recipes.append({
                'id': key,
                'name': recipe.name,
                'cuisine': recipe.cuisine.value,
                'difficulty': recipe.difficulty.value,
                'prep_time': recipe.prep_time_min,
                'cook_time': recipe.cook_time_min,
                'servings': recipe.servings,
                'dietary_tags': [tag.value for tag in recipe.dietary_tags]
            })
        return jsonify({'recipes': recipes})

    @app.route('/api/recipes/<recipe_id>', methods=['GET'])
    def get_recipe(recipe_id):
        """Get a specific recipe."""
        recipe = RECIPES_DB.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        ingredients = []
        for ing in recipe.ingredients:
            ingredients.append({
                'name': ing.name,
                'amount': ing.amount,
                'unit': ing.unit,
                'notes': ing.notes,
                'substitutes': ing.substitutes
            })

        nutrition = None
        if recipe.nutrition:
            nutrition = {
                'calories': recipe.nutrition.calories,
                'protein_g': recipe.nutrition.protein_g,
                'carbs_g': recipe.nutrition.carbs_g,
                'fat_g': recipe.nutrition.fat_g,
                'fiber_g': recipe.nutrition.fiber_g,
                'sodium_mg': recipe.nutrition.sodium_mg
            }

        return jsonify({
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'cuisine': recipe.cuisine.value,
            'difficulty': recipe.difficulty.value,
            'prep_time': recipe.prep_time_min,
            'cook_time': recipe.cook_time_min,
            'servings': recipe.servings,
            'ingredients': ingredients,
            'instructions': recipe.instructions,
            'tips': recipe.tips,
            'dietary_tags': [tag.value for tag in recipe.dietary_tags],
            'nutrition': nutrition
        })

    @app.route('/api/recipes/search', methods=['GET'])
    def search_recipes_api():
        """Search recipes with filters."""
        query = request.args.get('q', '')
        cuisine = request.args.get('cuisine')
        difficulty = request.args.get('difficulty')
        dietary = request.args.getlist('dietary')
        max_time = request.args.get('max_time', type=int)

        # Convert parameters
        cuisine_enum = Cuisine(cuisine) if cuisine else None
        difficulty_enum = Difficulty(difficulty) if difficulty else None
        dietary_enums = [DietaryTag(d) for d in dietary] if dietary else None

        results = search_recipes(
            query=query,
            cuisine=cuisine_enum,
            difficulty=difficulty_enum,
            dietary_tags=dietary_enums,
            max_time_min=max_time
        )

        recipes = []
        for recipe in results:
            recipes.append({
                'id': recipe.id,
                'name': recipe.name,
                'cuisine': recipe.cuisine.value,
                'difficulty': recipe.difficulty.value,
                'total_time': recipe.prep_time_min + recipe.cook_time_min,
                'servings': recipe.servings,
                'dietary_tags': [tag.value for tag in recipe.dietary_tags]
            })

        return jsonify({'results': recipes, 'count': len(recipes)})

    @app.route('/api/techniques', methods=['GET'])
    def list_techniques():
        """List all cooking techniques."""
        techniques = []
        for key, tech in TECHNIQUES_DB.items():
            techniques.append({
                'id': key,
                'name': tech['name'],
                'description': tech['description'],
                'best_for': tech['best_for'],
                'tips': tech['tips']
            })
        return jsonify({'techniques': techniques})

    @app.route('/api/cuisines', methods=['GET'])
    def list_cuisines():
        """List all available cuisines."""
        cuisines = [c.value for c in Cuisine]
        return jsonify({'cuisines': cuisines})

    @app.route('/api/dietary-tags', methods=['GET'])
    def list_dietary_tags():
        """List all dietary tags."""
        tags = [t.value for t in DietaryTag]
        return jsonify({'dietary_tags': tags})

    @app.route('/api/convert', methods=['POST'])
    def convert_units():
        """Convert cooking measurements."""
        data = request.json
        amount = data.get('amount')
        from_unit = data.get('from_unit')
        to_unit = data.get('to_unit')

        if not all([amount, from_unit, to_unit]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Volume conversions to ml
        volume_to_ml = {
            "ml": 1, "l": 1000, "cup": 236.588, "cups": 236.588,
            "tbsp": 14.787, "tablespoon": 14.787,
            "tsp": 4.929, "teaspoon": 4.929,
            "fl_oz": 29.574, "fluid_ounce": 29.574
        }

        # Weight conversions to grams
        weight_to_g = {
            "g": 1, "gram": 1, "grams": 1,
            "kg": 1000, "kilogram": 1000,
            "oz": 28.3495, "ounce": 28.3495,
            "lb": 453.592, "pound": 453.592
        }

        from_clean = from_unit.lower().replace(" ", "_")
        to_clean = to_unit.lower().replace(" ", "_")

        # Try volume conversion
        if from_clean in volume_to_ml and to_clean in volume_to_ml:
            ml_value = amount * volume_to_ml[from_clean]
            result = ml_value / volume_to_ml[to_clean]
            return jsonify({
                'original': {'amount': amount, 'unit': from_unit},
                'converted': {'amount': round(result, 2), 'unit': to_unit},
                'type': 'volume'
            })

        # Try weight conversion
        if from_clean in weight_to_g and to_clean in weight_to_g:
            g_value = amount * weight_to_g[from_clean]
            result = g_value / weight_to_g[to_clean]
            return jsonify({
                'original': {'amount': amount, 'unit': from_unit},
                'converted': {'amount': round(result, 2), 'unit': to_unit},
                'type': 'weight'
            })

        return jsonify({'error': 'Unable to convert between these units'}), 400

    @app.route('/api/session/reset', methods=['POST'])
    def reset_session():
        data = request.json
        session_id = data.get('session_id', 'default')

        if session_id in agents:
            agents[session_id].reset()
            del agents[session_id]

        return jsonify({'status': 'reset', 'session_id': session_id})

    return app


app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
