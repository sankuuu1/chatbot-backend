import datetime
import json
import logging
import urllib.request

logger = logging.getLogger("bandhu.weather")

WEATHER_CODE_MAP = {
    0: ("निरभ्र आकाश (Clear sky)", "☀️"),
    1: ("मुख्यतः निरभ्र (Mainly clear)", "🌤️"),
    2: ("अंशतः ढगाळ (Partly cloudy)", "⛅"),
    3: ("ढगाळ वातावरण (Overcast)", "☁️"),
    45: ("धुकं (Foggy)", "🌫️"),
    48: ("घट्ट धुकं (Depositing rime fog)", "🌫️"),
    51: ("हलकी रिमझिम (Light drizzle)", "🌦️"),
    53: ("मध्यम रिमझिम (Moderate drizzle)", "🌧️"),
    55: ("जोरदार रिमझिम (Dense drizzle)", "🌧️"),
    61: ("हलका पाऊस (Slight rain)", "🌦️"),
    63: ("मध्यम पाऊस (Moderate rain)", "🌧️"),
    65: ("मुसळधार पाऊस (Heavy rain)", "⛈️"),
    80: ("पावसाची सर (Rain showers)", "🌦️"),
    81: ("जोरदार पावसाची सर (Moderate showers)", "🌧️"),
    82: ("मुसळधार पावसाची सर (Violent showers)", "⛈️"),
    95: ("वादळी पाऊस (Thunderstorm)", "🌩️"),
    96: ("गडगडाटासह पाऊस (Thunderstorm with hail)", "⛈️"),
}

MARATHI_DAYS = ["सोम", "मंगळ", "बुध", "गुरु", "शुक्र", "शनि", "रवि"]


def get_weather_info(weather_code: int):
    return WEATHER_CODE_MAP.get(weather_code, ("ढगाळ वातावरण", "⛅"))


def get_daily_info_payload(lat: float = 21.1458, lon: float = 79.0882, location_name: str = "नागपूर, महाराष्ट्र"):
    """Fetches live 5-day weather forecast from Open-Meteo API and formats for Marathi UI."""
    weather_data = {
        "location": location_name,
        "temperature": 30,
        "condition": "निरभ्र आकाश",
        "icon": "☀️",
        "rain_probability": 0,
        "humidity": 45,
        "wind_speed": 3.5,
    }

    forecast = []
    advisory = {
        "title": "शेतकऱ्यांसाठी सूचना",
        "text": "आज हवामान अनुकूल आहे. सिंचन व फवारणीची कामे पूर्ण करून घ्यावीत.",
    }

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            f"&timezone=Asia%2FKolkata&forecast_days=5"
        )
        with urllib.request.urlopen(url, timeout=4) as resp:
            raw = json.loads(resp.read().decode())
            curr = raw.get("current", {})
            daily = raw.get("daily", {})

            if curr.get("temperature_2m") is not None:
                weather_data["temperature"] = round(curr.get("temperature_2m"))
            if curr.get("relative_humidity_2m") is not None:
                weather_data["humidity"] = round(curr.get("relative_humidity_2m"))
            if curr.get("wind_speed_10m") is not None:
                weather_data["wind_speed"] = round(curr.get("wind_speed_10m"), 1)

            code = curr.get("weather_code", 0)
            condition_text, icon = get_weather_info(code)
            weather_data["condition"] = condition_text
            weather_data["icon"] = icon

            # 5-Day Forecast Mapping
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            codes = daily.get("weather_code", [])
            rain_probs = daily.get("precipitation_probability_max", [])

            if rain_probs:
                weather_data["rain_probability"] = rain_probs[0]

            for i in range(len(dates)):
                dt = datetime.datetime.strptime(dates[i], "%Y-%m-%d")
                if i == 0:
                    day_label = "आज"
                elif i == 1:
                    day_label = "उद्या"
                else:
                    day_label = MARATHI_DAYS[dt.weekday()]

                _, day_icon = get_weather_info(codes[i] if i < len(codes) else 0)
                high = round(max_temps[i]) if i < len(max_temps) else 32
                low = round(min_temps[i]) if i < len(min_temps) else 23

                forecast.append({
                    "day": day_label,
                    "date": dates[i],
                    "high": high,
                    "low": low,
                    "icon": day_icon,
                    "rain_probability": rain_probs[i] if i < len(rain_probs) else 0
                })

            # Dynamic Advisory based on live rain probability
            max_rain = weather_data["rain_probability"]
            if max_rain >= 60:
                advisory["text"] = "⚠️ आज मुसळधार पावसाची शक्यता आहे. फवारणी, खत व्यवस्थापन किंवा कापणी आज टाळावी."
            elif max_rain >= 30:
                advisory["text"] = "⛅ आज अंशतः पावसाची शक्यता आहे. शेतातील पाण्याचा निचरा व्यवस्थित ठेवा."
            else:
                advisory["text"] = "☀️ आज हवामान स्वच्छ आहे. फवारणी, सिंचन व शेतीची कामे करण्यासाठी उत्तम दिवस."

    except Exception as e:
        logger.warning("Failed to fetch live weather from Open-Meteo: %s", e)
        # Fallback 5-day forecast if API times out
        forecast = [
            {"day": "आज", "high": 31, "low": 23, "icon": "🌧️", "rain_probability": 70},
            {"day": "उद्या", "high": 30, "low": 23, "icon": "🌧️", "rain_probability": 60},
            {"day": "गुरु", "high": 32, "low": 24, "icon": "⛅", "rain_probability": 20},
            {"day": "शुक्र", "high": 30, "low": 22, "icon": "⛅", "rain_probability": 10},
        ]

    return {
        "location": weather_data["location"],
        "weather": {
            "temperature": weather_data["temperature"],
            "condition": weather_data["condition"],
            "icon": weather_data["icon"],
            "rain_probability": weather_data["rain_probability"],
            "humidity": weather_data["humidity"],
            "wind_speed": weather_data["wind_speed"],
            "unit": "अंश सेल्सिअस",
            "time_label": "आज",
        },
        "forecast": forecast,
        "advisory": advisory,
        "articles": [
            {
                "id": "1",
                "category": "शेती",
                "category_key": "farming",
                "tag_color": "#E8F5E9",
                "tag_text_color": "#2E7D32",
                "title": "सोयाबीनच्या बाजारभावात वाढ",
                "subtitle": "विदर्भातील बाजारभावात आज बदल",
                "time_ago": "२ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1599599810694-b5b37304c041?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "2",
                "category": "शिक्षण",
                "category_key": "education",
                "tag_color": "#F3E5F5",
                "tag_text_color": "#7B1FA2",
                "title": "शिष्यवृत्ती अर्ज करण्याची अंतिम तारीख वाढली",
                "subtitle": "अर्ज करण्याची नवीन तारीख ३१ जुलै",
                "time_ago": "४ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "3",
                "category": "सरकारी योजना",
                "category_key": "schemes",
                "tag_color": "#FFF3E0",
                "tag_text_color": "#E65100",
                "title": "पीएम किसान योजनेचा १६ वा हप्ता लवकरच",
                "subtitle": "लाभार्थ्यांच्या खात्यात थेट जमा",
                "time_ago": "६ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "4",
                "category": "स्थानिक",
                "category_key": "local",
                "tag_color": "#E3F2FD",
                "tag_text_color": "#1565C0",
                "title": "नागपूर विभागात पुढील ३ दिवस मुसळधार पावसाचा इशारा",
                "subtitle": "हवामान खात्याचा यलो अलर्ट जारी",
                "time_ago": "१ तासापूर्वी",
                "image_url": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "5",
                "category": "रोजगार",
                "category_key": "jobs",
                "tag_color": "#EFEBE9",
                "tag_text_color": "#4E342E",
                "title": "कृषी विभागात ५०० जागांसाठी नोकरभरती जाहीर",
                "subtitle": "ऑनलाइन अर्ज प्रक्रिया सुरू",
                "time_ago": "५ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=300&q=80",
            },
        ],
    }
