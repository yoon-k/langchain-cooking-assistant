# AI Cooking Assistant

LangChain-powered intelligent cooking assistant that helps you discover recipes, learn techniques, and master your kitchen.

## Live Demo

[**View Demo**](https://yoon-k.github.io/langchain-cooking-assistant/)

## Features

- **Recipe Search**: Find recipes by cuisine, ingredient, dietary requirements, or cooking time
- **Step-by-Step Instructions**: Detailed recipes with ingredients and cooking steps
- **Ingredient Substitutions**: Find alternatives when you're missing ingredients
- **Cooking Techniques**: Learn about sautéing, braising, roasting, and more
- **Unit Conversions**: Convert between cups, grams, tablespoons, and temperatures
- **Nutrition Calculator**: Get calorie and macro information for recipes
- **Meal Planning**: Generate weekly meal plans with variety
- **Cooking Times**: Get perfect timing for meats, eggs, and vegetables

## Architecture

```
langchain-cooking-assistant/
├── app/
│   ├── agents/
│   │   └── cooking_agent.py      # Main cooking assistant agent
│   ├── tools/
│   │   └── cooking_tools.py      # LangChain cooking tools
│   ├── data/
│   │   └── recipes.py            # Recipe and ingredient database
│   └── api.py                    # Flask API endpoints
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── index.html
└── requirements.txt
```

## LangChain Components

### Custom Tools
- `RecipeSearchTool`: Search recipes with multiple filters
- `RecipeDetailTool`: Get complete recipe with instructions
- `IngredientSubstituteTool`: Find ingredient alternatives
- `CookingTechniqueTool`: Learn cooking techniques
- `MealPlanTool`: Generate meal plans
- `UnitConversionTool`: Convert measurements
- `NutritionCalculatorTool`: Calculate recipe nutrition
- `TimerCalculatorTool`: Get cooking times

### Agent Architecture
```python
from app.agents.cooking_agent import create_cooking_agent

# Create agent
agent = create_cooking_agent()

# Chat with context awareness
response = agent.chat("Show me Italian recipes")
response = agent.chat("How do I make the Pasta Aglio e Olio?")
response = agent.chat("What can I substitute for Parmesan?")
```

### Recipe Database
```python
from app.data.recipes import RECIPES_DB, search_recipes, Cuisine

# Search recipes
italian_recipes = search_recipes(cuisine=Cuisine.ITALIAN)
quick_recipes = search_recipes(max_time_min=30)
vegan_recipes = search_recipes(dietary_tags=[DietaryTag.VEGAN])

# Get recipe details
recipe = RECIPES_DB["kimchi_fried_rice"]
print(recipe.instructions)
```

## Installation

```bash
# Clone repository
git clone https://github.com/yoon-k/langchain-cooking-assistant.git
cd langchain-cooking-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.api
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Main chat endpoint |
| `/api/recipes` | GET | List all recipes |
| `/api/recipes/<id>` | GET | Get recipe details |
| `/api/recipes/search` | GET | Search with filters |
| `/api/techniques` | GET | List cooking techniques |
| `/api/cuisines` | GET | List available cuisines |
| `/api/dietary-tags` | GET | List dietary options |
| `/api/convert` | POST | Convert measurements |

## Supported Cuisines

- Korean
- Japanese
- Chinese
- Italian
- Mexican
- American
- French
- Thai
- Indian
- Mediterranean

## Dietary Options

- Vegetarian
- Vegan
- Gluten-Free
- Dairy-Free
- Low-Carb
- High-Protein
- Keto
- Paleo

## Featured Recipes

- **Kimchi Fried Rice** - Korean comfort food
- **Pasta Aglio e Olio** - Classic Italian simplicity
- **Chicken Stir-Fry** - Quick and healthy
- **Tacos al Pastor** - Traditional Mexican
- **Vegetable Curry** - Rich Indian flavors
- **Pad Thai** - Thailand's famous noodles
- **Caesar Salad** - American classic
- **Miso Soup** - Japanese traditional
- **French Omelette** - Perfectly cooked
- **Greek Salad** - Mediterranean fresh

## Tech Stack

- **LangChain**: Agent framework and tool orchestration
- **Flask**: Backend API server
- **Python 3.9+**: Core language
- **Pydantic**: Data validation and tool input schemas

## Contributing

Contributions are welcome! Feel free to add new recipes, cuisines, or features.

## License

MIT License - feel free to use this project for learning and development.
