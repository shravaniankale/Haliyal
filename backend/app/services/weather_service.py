import logging
import requests
from typing import Dict, Any, Optional
from .district_service import get_district_info, DISTRICT_TALUKS

logger = logging.getLogger(__name__)

WEATHER_CODE_MAP = {
    0: ("Clear Sky", "ಸ್ವಚ್ಛ ಆಕಾಶ", "☀️"),
    1: ("Mainly Clear", "ಹೆಚ್ಚಾಗಿ ಸ್ವಚ್ಛ ಆಕಾಶ", "🌤️"),
    2: ("Partly Cloudy", "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ", "⛅"),
    3: ("Overcast", "ದಟ್ಟ ಮೋಡ ಕವಿದ ವಾತಾವರಣ", "☁️"),
    45: ("Foggy", "ಮಂಜು ಮುಸುಕಿದ ವಾತಾವರಣ", "🌫️"),
    51: ("Light Drizzle", "ಲಘು ತುಂತುರು ಮಳೆ", "🌦️"),
    53: ("Moderate Drizzle", "ಮಧ್ಯಮ ತುಂತುರು ಮಳೆ", "🌧️"),
    55: ("Dense Drizzle", "ದಟ್ಟ ತುಂತುರು ಮಳೆ", "🌧️"),
    61: ("Slight Rain", "ಹಗುರ ಮಳೆ", "🌦️"),
    63: ("Moderate Rain", "ಸಾಧಾರಣ ಮಳೆ", "🌧️"),
    65: ("Heavy Rain", "ಭಾರೀ ಮಳೆ", "⛈️"),
    80: ("Rain Showers", "ಮಳೆಯ ಸಿಂಚನ", "🌦️"),
    81: ("Moderate Showers", "ಮಳೆಯ ಝರಿ", "🌧️"),
    82: ("Violent Showers", "ಪ್ರಚಂಡ ಮಳೆ", "⛈️"),
    95: ("Thunderstorm", "ಗುಡುಗು ಸಹಿತ ಮಳೆ", "⚡")
}

class AgriculturalWeatherService:
    """
    Live and forecasted agro-meteorological service for Karnataka districts and taluks.
    Provides weather intelligence, spraying advisories, and irrigation recommendations.
    """

    @classmethod
    def get_live_weather(cls, district: str = "Belagavi", taluk: Optional[str] = None) -> Dict[str, Any]:
        info = get_district_info(district)
        lat = info.get("latitude", 15.8497)
        lon = info.get("longitude", 74.4977)

        # Default fallback representation
        result = {
            "district": info.get("name", district),
            "district_kn": info.get("name_kn", "ಬೆಳಗಾವಿ"),
            "taluk": taluk or district,
            "is_live": False,
            "temperature": 28.0,
            "humidity": 65.0,
            "wind_speed": 10.0,
            "condition": "Partly Cloudy",
            "condition_kn": "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ",
            "total_48h_rain": 0.0,
            "spraying_advisory_kn": "ಗಾಳಿಯ ವೇಗ ಮತ್ತು ಹವಾಮಾನ ಅನುಕೂಲಕರವಾಗಿದ್ದು, ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ಔಷಧಿ ಸಿಂಪಡಣೆ ಮಾಡಬಹುದು.",
            "spraying_advisory_en": "Wind and atmospheric conditions are suitable for foliar spraying in early morning or late evening.",
            "irrigation_advisory_kn": "ಒಣ ಹವೆ ಮುಂದುವರಿದಿದ್ದು, ಬೆಳೆಗಳಿಗೆ ಅಗತ್ಯಕ್ಕೆ ತಕ್ಕಂತೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿ.",
            "irrigation_advisory_en": "Dry conditions prevailing; provide regular protective irrigation as required by crop stage."
        }

        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
                f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
                f"&forecast_days=3&timezone=Asia%2FKolkata"
            )
            resp = requests.get(url, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                curr = data.get("current", {})
                daily = data.get("daily", {})

                temp = float(curr.get("temperature_2m", 28.0))
                hum = float(curr.get("relative_humidity_2m", 65.0))
                wind = float(curr.get("wind_speed_10m", 10.0))
                w_code = int(curr.get("weather_code", 1))

                cond_en, cond_kn, _ = WEATHER_CODE_MAP.get(w_code, ("Partly Cloudy", "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ", "⛅"))

                rain_sums = daily.get("precipitation_sum", [])
                rain_48h = sum([float(r) for r in rain_sums[:2]]) if rain_sums else 0.0

                result["is_live"] = True
                result["temperature"] = temp
                result["humidity"] = hum
                result["wind_speed"] = wind
                result["condition"] = cond_en
                result["condition_kn"] = cond_kn
                result["total_48h_rain"] = round(rain_48h, 1)

                if rain_48h > 10.0:
                    result["spraying_advisory_kn"] = f"ಮುಂದಿನ ೪೮ ಗಂಟೆಗಳಲ್ಲಿ ಮಳೆಯಾಗುವ ({rain_48h:.1f} ಮಿ.ಮೀ) ಸಾಧ್ಯತೆ ಇರುವುದರಿಂದ ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ."
                    result["spraying_advisory_en"] = f"Rainfall ({rain_48h:.1f} mm) predicted in the next 48 hours; postpone foliar pesticide/fungicide spraying."
                    result["irrigation_advisory_kn"] = "ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಇರುವುದರಿಂದ ಜಮೀನಿನಲ್ಲಿ ನೀರಾವರಿ ನಿಲ್ಲಿಸಿ ಮತ್ತು ಬಸಿದು ಹೋಗಲು ಕಾಲುವೆ ತೆರೆಯಿರಿ."
                    result["irrigation_advisory_en"] = "Suspended irrigation recommended as natural rainfall is anticipated."
                elif wind > 18.0:
                    result["spraying_advisory_kn"] = "ಗಾಳಿಯ ವೇಗ ಹೆಚ್ಚಾಗಿರುವುದರಿಂದ (೧೮ ಕಿ.ಮೀ/ಗಂಟೆಗಿಂತ ಹೆಚ್ಚು) ಸಿಂಪಡಣೆ ಮಾಡಿದರೆ ಔಷಧ ನಷ್ಟವಾಗುತ್ತದೆ. ಶಾಂತ ಗಾಳಿ ಇರುವಾಗ ಸಿಂಪಡಿಸಿ."
                    result["spraying_advisory_en"] = "High wind speeds detected; avoid spraying to prevent spray drift losses."
                else:
                    result["spraying_advisory_kn"] = "ವಾತಾವರಣವು ಶಾಂತವಾಗಿದ್ದು, ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ರೋಗ ಮತ್ತು ಕೀಟ ನಿರ್ವಹಣೆಗೆ ಸಿಂಪಡಿಸಲು ಸೂಕ್ತವಾಗಿದೆ."
                    result["spraying_advisory_en"] = "Calm winds and optimal humidity; excellent conditions for agricultural spraying."
        except Exception as e:
            logger.warning(f"Live weather fetch notice for {district}: {e}")

        return result

