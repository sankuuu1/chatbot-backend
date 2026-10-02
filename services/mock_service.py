"""
Bandhu AI - Mock Response Provider
==================================

Offline mock service providing structured fallback responses when external 
AI providers (Groq / Gemini) are unavailable or during local testing.
Supports Marathi, Hindi, and English.
"""


def get_mock_response(message: str, category: str, language: str = "mr") -> tuple[str, dict | None]:
    """Generates localized fallback response and optional rich_data payload.

    Args:
        message (str): User input text message.
        category (str): Query domain category key (farming, education, etc.).
        language (str): Target language code ('mr', 'hi', or 'en').

    Returns:
        tuple[str, dict | None]: Response text and rich_data dictionary (if applicable).
    """
    message = message.lower().strip()
    rich_data = None

    # --- 1. ENGLISH MOCK RESPONSES ---
    if language == "en":
        if any(w in message for w in ["scheme", "yojana", "pm kisan", "subsidy", "insurance"]):
            text_response = "Here are the key agricultural government schemes available:"
            rich_data = {
                "type": "farming",
                "title": "Major Government Schemes",
                "points": [
                    "PM Kisan Samman Nidhi: ₹6,000 yearly directly in bank account.",
                    "Comprehensive Crop Insurance Scheme: Compensation for natural disasters.",
                    "Solar Pump Scheme: Up to 95% subsidy on solar pumps."
                ]
            }
        elif category == "education" or any(w in message for w in ["triangle", "area", "math"]):
            text_response = "Here is the formula and concept for the area of a triangle:"
            rich_data = {
                "type": "education",
                "title": "Area of a Triangle",
                "diagram_type": "triangle",
                "content": [
                    {"label": "Base", "desc": "Bottom side of the triangle."},
                    {"label": "Height", "desc": "Perpendicular height from base to top vertex."}
                ],
                "formula": "1/2 × Base × Height"
            }
        else:
            text_response = "Hello! I am Bandhu. I can help you with farming, market prices, weather, schemes, or education. How can I assist you?"

    # --- 2. HINDI MOCK RESPONSES ---
    elif language == "hi":
        if any(w in message for w in ["योजना", "सरकारी", "yojana", "scheme", "पीएम किसान", "अनुदान", "बीमा"]):
            text_response = "प्रमुख किसान एवं कल्याणकारी सरकारी योजनाओं की जानकारी निम्नलिखित है:"
            rich_data = {
                "type": "farming",
                "title": "प्रमुख सरकारी योजनाएं (Government Schemes)",
                "points": [
                    "पीएम किसान सम्मान निधि: प्रति वर्ष ₹6,000 सीधे खाते में।",
                    "प्रधानमंत्री फसल बीमा योजना: प्राकृतिक आपदा पर फसल क्षतिपूर्ति।",
                    "सौर कृषि पंप योजना: 95% तक अनुदान पर सोलर पंप।"
                ]
            }
        elif category == "education" or any(w in message for w in ["त्रिभुज", "क्षेत्रफल", "गणित", "शिक्षण"]):
            text_response = "त्रिभुज का क्षेत्रफल निकालना बहुत आसान है! नीचे दी गई जानकारी समझें:"
            rich_data = {
                "type": "education",
                "title": "त्रिभुज का क्षेत्रफल (Area of a Triangle)",
                "diagram_type": "triangle",
                "content": [
                    {"label": "आधार (Base)", "desc": "त्रिभुज की निचली भुजा।"},
                    {"label": "ऊंचाई (Height)", "desc": "आधार से शीर्ष तक की लंबवत दूरी।"}
                ],
                "formula": "1/2 × आधार × ऊंचाई"
            }
        else:
            text_response = "नमस्ते! मैं बंधु हूँ। 🙏 बताइए, आज मैं आपकी क्या सहायता कर सकता हूँ? आप कृषि, योजना, मौसम या पढ़ाई के बारे में पूछ सकते हैं।"

    # --- 3. MARATHI MOCK RESPONSES (DEFAULT) ---
    else:
        if any(w in message for w in ["योजना", "सरकारी", "yojana", "scheme", "पीएम किसान", "नमो शेतकरी", "अनुदान", "विमा"]):
            text_response = "महाराष्ट्रातील प्रमुख शेतकरी व कल्याणकारी सरकारी योजनांची माहिती खालीलप्रमाणे आहे:"
            rich_data = {
                "type": "farming",
                "title": "प्रमुख सरकारी योजना (Government Schemes)",
                "points": [
                    "नमो शेतकरी महासन्मान निधी: वर्षाला ₹६,००० थेट खात्यात जमा.",
                    "१ रुपयात सर्वसमावेशक पीक विमा योजना: नैसर्गिक आपत्तीत नुकसानभरपाई.",
                    "मागेल त्याला विहीर / सौर कृषी पंप योजना: ९५% अनुदानावर सौर पंप.",
                    "महाडीबीटी (MahaDBT): ट्रॅक्टर व औजारांवर ५०% पर्यंत अनुदान."
                ]
            }
        elif category == "education" or any(w in message for w in ["ganit", "triangle", "क्षेत्रफळ", "गणित", "शिक्षण"]):
            text_response = "त्रिकोणाचे क्षेत्रफळ काढणे खूप सोपे आहे! खालील सूत्र व माहिती नीट समजून घ्या:"
            rich_data = {
                "type": "education",
                "title": "त्रिकोणाचे क्षेत्रफळ (Area of a Triangle)",
                "diagram_type": "triangle",
                "content": [
                    {"label": "पाया (Base)", "desc": "त्रिकोणाची खालची बाजू."},
                    {"label": "उंची (Height)", "desc": "खालच्या बाजूपासून वरच्या टोकापर्यंतचे उभे अंतर."},
                ],
                "formula": "१/२ × पाया × उंची",
            }
        else:
            text_response = f"मी '{message}' या विषयावर तुम्हाला मदत करू शकतो! कृपया शेती, सरकारी योजना, हवामान, बाजारभाव किंवा शिक्षणाबद्दल विचारून पहा."

    return text_response, rich_data
