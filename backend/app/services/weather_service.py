from typing import Dict, Any, Optional
import httpx

WEATHER_CODE_MAP = {
    0: ("Clear Sky", "Optimal conditions for outdoor running, cycling, or walking!"),
    1: ("Mainly Clear", "Great weather for outdoor cardio and training."),
    2: ("Partly Cloudy", "Comfortable temperature for outdoor activity."),
    3: ("Overcast", "Cool and overcast; great for a brisk walk or outdoor run."),
    45: ("Foggy", "Low visibility; exercise caution if running outdoors, or consider gym training."),
    48: ("Depositing Rime Fog", "Chilly fog; recommend warm indoor workout."),
    51: ("Light Drizzle", "Light rain; consider a rain jacket or indoor session."),
    61: ("Slight Rain", "Wet conditions; indoor strength or cardio workout recommended."),
    63: ("Moderate Rain", "Rainy outdoors; perfect time for a focused indoor gym workout!"),
    65: ("Heavy Rain", "Heavy downpour; keep workouts indoors."),
    71: ("Slight Snow", "Cold and snowy; bundle up or train inside."),
    80: ("Rain Showers", "Intermittent showers; keep outdoor sessions brief or stay indoors."),
    95: ("Thunderstorm", "Thunderstorms; stay safely indoors for your fitness routine."),
}


class WeatherService:
    @staticmethod
    async def get_workout_weather(latitude: float = 40.7128, longitude: float = -74.0060) -> Dict[str, Any]:
        """
        Fetches current weather from Open-Meteo (free public API without API key requirement)
        and returns outdoor workout advisory.
        """
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current_weather": "true",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get("current_weather", {})
                    temp_c = current.get("temperature", 20.0)
                    temp_f = round((temp_c * 9 / 5) + 32, 1)
                    weather_code = int(current.get("weathercode", 0))
                    condition_text, workout_tip = WEATHER_CODE_MAP.get(
                        weather_code, ("Fair", "Enjoy your daily workout today!")
                    )

                    return {
                        "available": True,
                        "temperature_c": temp_c,
                        "temperature_f": temp_f,
                        "windspeed_kmh": current.get("windspeed", 0.0),
                        "condition": condition_text,
                        "workout_suggestion": workout_tip,
                        "is_outdoor_friendly": weather_code in (0, 1, 2, 3) and temp_c >= 5.0 and temp_c <= 32.0,
                    }
        except Exception:
            pass

        # Clean fallback when offline or timeout occurs
        return {
            "available": False,
            "temperature_c": 21.0,
            "temperature_f": 69.8,
            "windspeed_kmh": 10.0,
            "condition": "Mild / Indoor Friendly",
            "workout_suggestion": "Weather data currently offline. Ready for your gym or home training session!",
            "is_outdoor_friendly": True,
        }
