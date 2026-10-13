from typing import List, Dict, Any, Optional
import httpx
from backend.app.config import settings

# Curated reference database of common foods with verified macronutrients (per 100g or standard serving)
CURATED_FOODS = [
    {"name": "Chicken Breast (Cooked)", "calories": 165.0, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "serving": "100g", "source": "USDA Database"},
    {"name": "Whole Egg (Large)", "calories": 72.0, "protein_g": 6.3, "carbs_g": 0.4, "fat_g": 4.8, "serving": "1 large egg (50g)", "source": "USDA Database"},
    {"name": "Egg White", "calories": 17.0, "protein_g": 3.6, "carbs_g": 0.2, "fat_g": 0.1, "serving": "1 egg white (33g)", "source": "USDA Database"},
    {"name": "Salmon Fillet (Baked)", "calories": 208.0, "protein_g": 22.0, "carbs_g": 0.0, "fat_g": 13.0, "serving": "100g", "source": "USDA Database"},
    {"name": "Oatmeal (Rolled Oats, Dry)", "calories": 389.0, "protein_g": 16.9, "carbs_g": 66.3, "fat_g": 6.9, "serving": "100g", "source": "USDA Database"},
    {"name": "Greek Yogurt (Nonfat, Plain)", "calories": 59.0, "protein_g": 10.0, "carbs_g": 3.6, "fat_g": 0.4, "serving": "100g", "source": "USDA Database"},
    {"name": "Banana", "calories": 89.0, "protein_g": 1.1, "carbs_g": 22.8, "fat_g": 0.3, "serving": "1 medium (118g)", "source": "USDA Database"},
    {"name": "Apple", "calories": 52.0, "protein_g": 0.3, "carbs_g": 13.8, "fat_g": 0.2, "serving": "1 medium (182g)", "source": "USDA Database"},
    {"name": "Brown Rice (Cooked)", "calories": 111.0, "protein_g": 2.6, "carbs_g": 23.0, "fat_g": 0.9, "serving": "100g", "source": "USDA Database"},
    {"name": "White Rice (Cooked)", "calories": 130.0, "protein_g": 2.7, "carbs_g": 28.2, "fat_g": 0.3, "serving": "100g", "source": "USDA Database"},
    {"name": "Broccoli (Steamed)", "calories": 35.0, "protein_g": 2.4, "carbs_g": 7.2, "fat_g": 0.4, "serving": "100g", "source": "USDA Database"},
    {"name": "Almonds", "calories": 579.0, "protein_g": 21.2, "carbs_g": 21.6, "fat_g": 49.9, "serving": "100g", "source": "USDA Database"},
    {"name": "Peanut Butter", "calories": 188.0, "protein_g": 8.0, "carbs_g": 6.0, "fat_g": 16.0, "serving": "2 tbsp (32g)", "source": "USDA Database"},
    {"name": "Sweet Potato (Baked)", "calories": 90.0, "protein_g": 2.0, "carbs_g": 20.7, "fat_g": 0.2, "serving": "100g", "source": "USDA Database"},
    {"name": "Whey Protein Powder", "calories": 120.0, "protein_g": 24.0, "carbs_g": 3.0, "fat_g": 1.5, "serving": "1 scoop (30g)", "source": "Standard Supplement"},
    {"name": "Tuna (Canned in Water)", "calories": 116.0, "protein_g": 26.0, "carbs_g": 0.0, "fat_g": 1.0, "serving": "100g", "source": "USDA Database"},
    {"name": "Avocado", "calories": 160.0, "protein_g": 2.0, "carbs_g": 8.5, "fat_g": 14.7, "serving": "100g", "source": "USDA Database"},
    {"name": "Tofu (Firm)", "calories": 76.0, "protein_g": 8.0, "carbs_g": 1.9, "fat_g": 4.8, "serving": "100g", "source": "USDA Database"},
    {"name": "Lean Ground Beef (90/10, Cooked)", "calories": 217.0, "protein_g": 26.1, "carbs_g": 0.0, "fat_g": 11.8, "serving": "100g", "source": "USDA Database"},
    {"name": "Whole Milk", "calories": 61.0, "protein_g": 3.2, "carbs_g": 4.8, "fat_g": 3.3, "serving": "100ml", "source": "USDA Database"},
]


class NutritionService:
    _cache: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    async def search_food(cls, query: str) -> List[Dict[str, Any]]:
        query_clean = query.strip().lower()
        if not query_clean:
            return CURATED_FOODS[:8]

        if query_clean in cls._cache:
            return cls._cache[query_clean]

        results = []

        # 1. Check if USDA API key is configured
        if settings.USDA_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.get(
                        "https://api.nal.usda.gov/fdc/v1/foods/search",
                        params={
                            "api_key": settings.USDA_API_KEY,
                            "query": query_clean,
                            "pageSize": 6,
                            "dataType": ["Survey (FNDDS)", "Foundation"],
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("foods", []):
                            nutrients = {n.get("nutrientName", "").lower(): n.get("value", 0.0) for n in item.get("foodNutrients", [])}
                            cals = next((v for k, v in nutrients.items() if "energy" in k or "calorie" in k), 0.0)
                            protein = next((v for k, v in nutrients.items() if "protein" in k), 0.0)
                            carbs = next((v for k, v in nutrients.items() if "carbohydrate" in k), 0.0)
                            fat = next((v for k, v in nutrients.items() if "lipid" in k or "total fat" in k), 0.0)

                            results.append({
                                "name": item.get("description", "").title(),
                                "calories": round(float(cals), 1),
                                "protein_g": round(float(protein), 1),
                                "carbs_g": round(float(carbs), 1),
                                "fat_g": round(float(fat), 1),
                                "serving": item.get("servingSizeUnit", "100g"),
                                "source": "USDA FoodData Central",
                            })
            except Exception:
                # Fall through gracefully to curated dataset on timeout or network issue
                pass

        # 2. Search curated reference dataset
        matching_curated = [
            f for f in CURATED_FOODS
            if query_clean in f["name"].lower()
        ]
        results.extend(matching_curated)

        # Fallback if nothing matched
        if not results:
            results = [f for f in CURATED_FOODS if any(w in f["name"].lower() for w in query_clean.split())]

        cls._cache[query_clean] = results
        return results
