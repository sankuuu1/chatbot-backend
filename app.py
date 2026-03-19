from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS — allow the deployed frontend or all origins in dev
frontend_url = os.getenv("FRONTEND_URL", "*")
CORS(app, resources={r"/*": {"origins": frontend_url}}, supports_credentials=True)

# --- LangChain Setup ---
# We try to initialize the model. If API key is missing, we flag it.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = None
init_error = None

if GOOGLE_API_KEY:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        # User requested Gemini 2.5 Flash Lite with NO RESTRICTIONS
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite", 
            google_api_key=GOOGLE_API_KEY,
            max_output_tokens=None
        )
        print("GenAI Model Initialized (Gemini 2.5 Flash Lite) - UNRESTRICTED")
    except Exception as e:
        init_error = f"Error initializing GenAI: {str(e)}"
        print(init_error)
else:
    init_error = "No GOOGLE_API_KEY found in environment variables."
    print("No GOOGLE_API_KEY found. Running in MOCK MODE.")


# --- Mock Service ---
def get_mock_response(message, category):
    # ... (rest of mock response function)
    message = message.lower()
    
    # default fallback
    text_response = "माफ करा, मला हे समजले नाही. कृपया पुन्हा सांगाल का?"
    rich_data = None

    if category == 'education' or "ganit" in message or "triangle" in message:
        text_response = "सुनिता ताई, त्रिकोणाचे क्षेत्रफळ काढणे खूप सोपे आहे! खालील माहिती नीट समजून घ्या:"
        rich_data = {
            "type": "education",
            "title": "त्रिकोणाचे क्षेत्रफळ (Area of a Triangle)",
            "diagram_type": "triangle", 
            "content": [
                {"label": "पाया (Base)", "desc": "त्रिकोणाची खालची बाजू."},
                {"label": "उंची (Height)", "desc": "खालच्या बाजूपासून वरच्या टोकापर्यंतचे उभे अंतर."}
            ],
            "formula": "१/२ × पाया × उंची"
        }
    
    elif category == 'farming' or "kapus" in message or "kid" in message:
        text_response = "सुनिता ताई, तुमच्या कपाशीवर 'पांढरी माशी' किंवा 'तुडतुडे' यांचा प्रादुर्भाव दिसतो आहे. यासाठी तुम्ही खालील उपाय करू शकता:"
        rich_data = {
            "type": "farming",
            "title": "कापसावरील कीड नियंत्रण",
            "points": [
                "पिवळे चिकट सापळे एकरी १० याप्रमाणे लावावेत.",
                "प्रादुर्भाव जास्त असल्यास निंबोळी अर्काची फवारणी करावी.",
                "कृषी केंद्रातून सल्ला घेऊनच रासायनिक औषधांचा वापर करा."
            ]
        }
        
    elif category == 'health':
         text_response = "तुमची लक्षणे सांगा, मी प्राथमिक तपासणी करू शकतो."
         rich_data = {
             "type": "health",
             "title": "आरोग्य सल्ला",
             "points": ["ताप आल्यास पाणी भरपूर प्या.", "विश्रांती घ्या."]
         }

    elif "hello" in message or "namaskar" in message:
        text_response = "नमस्कार! मी तुम्हाला कशी मदत करू शकते?"

    return text_response, rich_data

# --- Routes ---
@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    # Safe debug print for Windows consoles
    try:
        print(f"Received request: {str(request.json).encode('utf-8', errors='ignore')}")
    except:
        pass
    
    data = request.json
    user_message = data.get('message')
    category = data.get('category')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    if llm:
        # --- GenAI Mode ---
        try:
            # For now, just echo the message back from LLM
            # In a real app, you'd process the message and get a meaningful response
            # Improved Prompt Engineering to prevent echoing
            messages = [
                ("system", "You are a helpful Marathi assistant named Sunita Tai. Answer the user's question directly in Marathi. Do NOT repeat the user's message or the prompt headers."),
                ("human", f"Category: {category}. Question: {user_message}")
            ]
            response = llm.invoke(messages)
            text_response = response.content
            rich_data = None # Placeholder for rich data from LLM
            return jsonify({"response": text_response, "rich_data": rich_data})
        except Exception as e:
            print(f"Error during GenAI invocation: {str(e).encode('utf-8', errors='ignore')}")
            return jsonify({"error": f"GenAI processing failed: {str(e)}"}), 500
    else:
        # --- Mock Mode ---
        text_response, rich_data = get_mock_response(user_message, category)
        return jsonify({"response": text_response, "rich_data": rich_data})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "active", 
        "mode": "genai" if llm else "mock",
        "error": init_error,
        "env_key_present": bool(GOOGLE_API_KEY)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
