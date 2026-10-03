"""
Bandhu AI - Government Schemes Knowledgebase & Rule Engine
=========================================================

Comprehensive, verified dataset of Maharashtra State & Central Government 
welfare schemes across Agriculture, Education, Women Welfare, and Health.
Derived from MyScheme.gov.in, MahaDBT, and PM-Kisan standards.
"""

SCHEMES_DATABASE = [
    # --- 1. AGRICULTURE / FARMER SCHEMES ---
    {
        "id": "pm_kisan_namo",
        "category": "farmer",
        "sub_category": "financial_aid",
        "name_mr": "पीएम किसान + नमो शेतकरी महासन्मान निधी",
        "name_hi": "पीएम किसान + नमो शेतकारी महासम्मान निधि",
        "name_en": "PM-Kisan + Namo Shetkari Sanman Nidhi",
        "tag": "आर्थिक मदत",
        "badge_color": "#E8F5E9",
        "badge_text_color": "#2E7D32",
        "benefit_amount": "₹१२,००० / दरवर्षी (₹६००० केंद्र + ₹६००० राज्य)",
        "benefit_summary_mr": "दर ४ महिन्यांनी ₹४००० चा हप्ता थेट बँक खात्यात (DBT द्वारे) जमा केला जातो.",
        "eligibility_rules": {
            "max_land_acres": None,
            "min_land_acres": 0.1,
            "must_have_aadhaar": True,
            "must_have_land_record": True
        },
        "eligibility_text_mr": "ज्या शेतकऱ्यांच्या नावावर स्वतःची शेतजमीन (७/१२ उतारा) आहे आणि आधार कार्ड बँक खात्याशी लिंक (e-KYC) आहे.",
        "documents": [
            "आधार कार्ड (Aadhaar Card)",
            "जमिनीचा ७/१२ उतारा व ८-अ (7/12 & 8A Extract)",
            "आधार लिंक बँक पासबुक (Aadhaar Linked Bank Passbook)",
            "मोबाईल नंबर (e-KYC साठी)"
        ],
        "portal_name": "PM-Kisan & MahaDBT",
        "apply_url": "https://pmkisan.gov.in",
        "how_to_apply_mr": "pmkisan.gov.in किंवा जवळच्या CSC केंद्रावर जाऊन e-KYC पूर्ण करा व अर्ज नोंदणी करा."
    },
    {
        "id": "kusum_solar_pump",
        "category": "farmer",
        "sub_category": "irrigation",
        "name_mr": "मागेल त्याला सौर कृषी पंप योजना (कुसुम योजना)",
        "name_hi": "कुसुम सोलर पंप योजना (MahaDBT)",
        "name_en": "MahaDBT Kusum Solar Agri Pump Scheme",
        "tag": "९०% ते ९५% अनुदान",
        "badge_color": "#FFF3E0",
        "badge_text_color": "#E65100",
        "benefit_amount": "३, ५ किंवा ७.५ HP सौर कृषी पंप (९०-९५% शासकीय अनुदान)",
        "benefit_summary_mr": "दिवसा वीज व खात्रीशीर पाणीपुरवठा. शेतकऱ्याला फक्त ५% ते १०% रक्कम भरावी लागते.",
        "eligibility_rules": {
            "max_land_acres": None,
            "min_land_acres": 0.5,
            "has_water_source": True
        },
        "eligibility_text_mr": "शाश्वत पाण्याचा स्त्रोत (विहीर, कूपनलिका, शेततळे) उपलब्ध असणारे आणि पारंपरिक वीज जोडणी नसलेले शेतकरी.",
        "documents": [
            "७/१२ उतारा व ८-अ (७/१२ वर पाण्याची नोंद आवश्यक)",
            "आधार कार्ड",
            "बँक पासबुक झेरॉक्स",
            "जातीचे प्रमाणपत्र (SC/ST शेतकऱ्यांसाठी अतिरिक्त सवलत)"
        ],
        "portal_name": "MahaDBT / MSEDCL Solar Portal",
        "apply_url": "https://mahadiscom.in/solar_mskpy/index_mr.html",
        "how_to_apply_mr": "महावितरण सौर कृषी पंप पोर्टलवर जाऊन ऑनलाइन अर्ज भरा व आवश्यक कागदपत्रे अपलोड करा."
    },
    {
        "id": "pm_fasal_bima",
        "category": "farmer",
        "sub_category": "insurance",
        "name_mr": "सर्वसमावेशक पीक विमा योजना (१ रुपयात पीक विमा)",
        "name_hi": "प्रधानमंत्री फसल बीमा योजना (१ रुपये में)",
        "name_en": "Pradhan Mantri Fasal Bima Yojana (₹1 Scheme)",
        "tag": "पीक संरक्षण",
        "badge_color": "#E3F2FD",
        "badge_text_color": "#1565C0",
        "benefit_amount": "नैसर्गिक आपत्ती, दुष्काळ किंवा अतिवृष्टीमुळे पिकाचे नुकसान झाल्यास पूर्ण भरपाई",
        "benefit_summary_mr": "शेतकऱ्यांना केवळ ₹१ भरून खरीप व रब्बी पिकांचा विमा उतरवता येतो, उर्वरित हप्ता शासन भरते.",
        "eligibility_rules": {
            "max_land_acres": None,
            "min_land_acres": 0.1
        },
        "eligibility_text_mr": "अधिसूचित क्षेत्रात अधिसूचित पिके घेणारे सर्व खातेदार शेतकरी व भाडेपट्ट्याने शेती करणारे शेतकरी.",
        "documents": [
            "आधार कार्ड",
            "चालू वर्षाचा पीक पेरा नोंद असलेला ७/१२ उतारा",
            "बँक पासबुक (IFSC कोडसह)",
            "स्वयंघोषणा पत्र (पीक पेरणीबाबत)"
        ],
        "portal_name": "PMFBY National Portal",
        "apply_url": "https://pmfby.gov.in",
        "how_to_apply_mr": "pmfby.gov.in पोर्टलवर किंवा जवळच्या आपले सरकार सेवा केंद्रावर जाऊन ₹१ शुल्क भरून पावती मिळवा."
    },
    {
        "id": "krishi_yantrikikaran",
        "category": "farmer",
        "sub_category": "machinery",
        "name_mr": "कृषी यांत्रिकीकरण योजना (ट्रॅक्टर व अवजारे अनुदान)",
        "name_hi": "कृषि यंत्रीकरण योजना (ट्रैक्टर अनुदान)",
        "name_en": "MahaDBT Farm Mechanization (Tractor Subsidy)",
        "tag": "५०% पर्यंत अनुदान",
        "badge_color": "#F3E5F5",
        "badge_text_color": "#7B1FA2",
        "benefit_amount": "ट्रॅक्टर, रोटाव्हेटर, पॉवर टिलर, पेरणीयंत्र खरेदीसाठी ५०% पर्यंत अनुदान (कमाल ₹१.२५ लाख)",
        "benefit_summary_mr": "शेतकऱ्यांना शेती कामात आधुनिक यंत्रसामग्री खरेदी करण्यासाठी थेट बँक खात्यात अनुदान.",
        "eligibility_rules": {
            "max_land_acres": None,
            "min_land_acres": 0.5
        },
        "eligibility_text_mr": "स्वतःच्या नावावर शेती असणारे शेतकरी. एका कुटुंबातील एकाच व्यक्तीला ट्रॅक्टरचा लाभ मिळतो.",
        "documents": [
            "७/१२ आणि ८-अ उतारा",
            "आधार कार्ड",
            "बँक पासबुक",
            "खरेदी करावयाच्या अवजाराचे कोटेशन (दुकानदाराचे दरपत्रक)"
        ],
        "portal_name": "MahaDBT Farmer Portal",
        "apply_url": "https://mahadbt.maharashtra.gov.in/Farmer/Login/Login",
        "how_to_apply_mr": "MahaDBT शेतकरी पोर्टलवर 'कृषी यांत्रिकीकरण' घटकाखाली लॉटरी पद्धतीसाठी अर्ज सादर करा."
    },

    # --- 2. EDUCATION / STUDENT SCHEMES ---
    {
        "id": "panjabrao_deshmukh_hostel",
        "category": "student",
        "sub_category": "hostel_aid",
        "name_mr": "डॉ. पंजाबराव देशमुख वसतिगृह निर्वाह भत्ता योजना",
        "name_hi": "डॉ. पंजाबराव देशमुख छात्रावास निर्वाह भत्ता",
        "name_en": "Dr. Panjabrao Deshmukh Hostel Allowance",
        "tag": "विद्यार्थी भत्ता",
        "badge_color": "#E8F5E9",
        "badge_text_color": "#2E7D32",
        "benefit_amount": "दरवर्षी ₹२०,००० ते ₹३०,००० पर्यंत वसतिगृह व भोजन भत्ता",
        "benefit_summary_mr": "अल्पभूधारक शेतकरी व शेतमजूर यांच्या मुलांना उच्च शिक्षणासाठी वसतिगृहाचा खर्च मिळतो.",
        "eligibility_rules": {
            "student_family_income_max": 800000,
            "parent_is_farmer_or_laborer": True
        },
        "eligibility_text_mr": "व्यावसायिक अभ्यासक्रमात (Engineering, Medical, Agri, Diploma) शिकणारे अल्पभूधारक शेतकरी किंवा नोंदणीकृत मजुरांचे पाल्य.",
        "documents": [
            "विद्यार्थ्याचे आधार कार्ड",
            "वडिलांचा अल्पभूधारक शेतकरी असल्याचा दाखला किंवा मजुरी दाखला",
            "सध्याच्या कॉलेजचे बोनाफाईड व फी पावती",
            "वसतिगृह किंवा भाडे करारनामा"
        ],
        "portal_name": "MahaDBT Post-Matric",
        "apply_url": "https://mahadbt.maharashtra.gov.in",
        "how_to_apply_mr": "MahaDBT पोर्टलवर उच्च व तंत्र शिक्षण विभागांतर्गत योजनेचा पर्याय निवडून कॉलेजमार्फत अर्ज करा."
    },
    {
        "id": "post_matric_scholarship",
        "category": "student",
        "sub_category": "scholarship",
        "name_mr": "महाडीबीटी मॅट्रिकोत्तर शिक्षण शुल्क शिष्यवृत्ती (Rajarshi Shahu)",
        "name_hi": "राजर्षि छत्रपति शाहू महाराज शिक्षण शुल्क प्रतिपूर्ति",
        "name_en": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh (EBC)",
        "tag": "५०% फी सवलत",
        "badge_color": "#E3F2FD",
        "badge_text_color": "#1565C0",
        "benefit_amount": "कॉलेजच्या ५०% ते १००% शिक्षण शुल्क (Tuition Fee) व परीक्षा शुल्क माफी",
        "benefit_summary_mr": "EWS / Open / OBC / SEBC प्रवर्गातील विद्यार्थ्यांना पदवी व पदविका शिक्षणासाठी आर्थिक मदत.",
        "eligibility_rules": {
            "student_family_income_max": 800000
        },
        "eligibility_text_mr": "कुटुंबाचे वार्षिक उत्पन्न ₹८ लाखांपेक्षा कमी असणारे आणि CAP राउंडद्वारे प्रवेश घेतलेले विद्यार्थी.",
        "documents": [
            "तहसीलदारांचा उत्पन्नाचा दाखला (वार्षिक उत्पन्न < ₹८ लाख)",
            "१०वी/१२वी गुणपत्रिका व CAP वाटप पत्र (Allotment Letter)",
            "डोमिसाईल प्रमाणपत्र (महाराष्ट्र रहिवासी)",
            "आधार लिंक बँक पासबुक"
        ],
        "portal_name": "MahaDBT Official",
        "apply_url": "https://mahadbt.maharashtra.gov.in",
        "how_to_apply_mr": "MahaDBT पोर्टलवर 'Rajarshi Chhatrapati Shahu Maharaj' शिष्यवृत्ती निवडून कागदपत्रे अपलोड करा."
    },

    # --- 3. WOMEN WELFARE SCHEMES ---
    {
        "id": "majhi_ladki_bahin",
        "category": "women",
        "sub_category": "direct_benefit",
        "name_mr": "मुख्यमंत्री माझी लाडकी बहीण योजना",
        "name_hi": "मुख्यमंत्री माझी लाडकी बहिन योजना",
        "name_en": "Mukhyamantri Majhi Ladki Bahin Yojana",
        "tag": "दरमहा ₹१,५००",
        "badge_color": "#FFEBEE",
        "badge_text_color": "#C62828",
        "benefit_amount": "दरमहा ₹१,५०० थेट लाभार्थी महिलेच्या आधार लिंक बँक खात्यात",
        "benefit_summary_mr": "महिलांचे आर्थिक स्वावलंबन आणि आरोग्य व पोषणात सुधारणा करण्यासाठी थेट मासिक सहाय्य.",
        "eligibility_rules": {
            "age_min": 21,
            "age_max": 65,
            "family_income_max": 250000
        },
        "eligibility_text_mr": "महाराष्ट्रातील २१ ते ६५ वयोगटातील विवाहित, विधवा, घटस्फोटित व निराधार महिला (कुटुंबाचे उत्पन्न ₹२.५ लाखांपर्यंत).",
        "documents": [
            "आधार कार्ड (मोबाईल नंबर लिंक आवश्यक)",
            "उत्पन्नाचा दाखला किंवा पिवळे/केशरी रेशन कार्ड",
            "महाराष्ट्र रहिवासी प्रमाणपत्र किंवा रेशन कार्ड",
            "आधार संलग्न बँक पासबुक"
        ],
        "portal_name": "Nari Shakti Doot / Ladki Bahin Portal",
        "apply_url": "https://ladkibahin.maharashtra.gov.in",
        "how_to_apply_mr": "लाडकी बहीण पोर्टलवर किंवा अंगणवाडी सेविका / सेतू केंद्रामार्फत ऑनलाइन नोंदणी करा."
    },

    # --- 4. HEALTH / MEDICAL SCHEMES ---
    {
        "id": "mjpjay_ayushman",
        "category": "health",
        "sub_category": "medical_cover",
        "name_mr": "महात्मा ज्योतिराव फुले जन आरोग्य + आयुष्मान भारत योजना",
        "name_hi": "महात्मा ज्योतिराव फुले जन आरोग्य योजना (आयुष्मान भारत)",
        "name_en": "MJPJAY + Ayushman Bharat PM-JAY",
        "tag": "₹५ लाख मोफत उपचार",
        "badge_color": "#E8F5E9",
        "badge_text_color": "#2E7D32",
        "benefit_amount": "प्रति कुटुंब दरवर्षी ₹५,००,००० पर्यंत मोफत कॅशलेस उपचार व शस्त्रक्रिया",
        "benefit_summary_mr": "१,३५६ हून अधिक गंभीर आजार, शस्त्रक्रिया, औषधोपचार व आयसीयू खर्च संलग्न शासकीय व खाजगी रुग्णालयात मोफत.",
        "eligibility_rules": {
            "is_maharashtra_resident": True
        },
        "eligibility_text_mr": "महाराष्ट्रातील सर्व शिधापत्रिकाधारक (रेशन कार्डधारक) कुटुंब या योजनेसाठी पात्र आहेत.",
        "documents": [
            "रेशन कार्ड (पिवळे, केशरी किंवा पांढरे)",
            "आधार कार्ड किंवा मतदान ओळखपत्र",
            "आयुष्मान भारत कार्ड (असल्यास)"
        ],
        "portal_name": "State Health Assurance Society (MJPJAY)",
        "apply_url": "https://www.jeevandayee.gov.in",
        "how_to_apply_mr": "कोणत्याही संलग्न रुग्णालयातील 'आरोग्य मित्र' कक्षात जाऊन रेशन कार्ड व आधार कार्ड दाखवून कॅशलेस उपचार मिळवा."
    }
]


def get_all_schemes(category: str = None) -> list[dict]:
    """Returns list of all schemes or filtered by category."""
    if not category or category == "all" or category == "सर्व":
        return SCHEMES_DATABASE
    return [s for s in SCHEMES_DATABASE if s["category"] == category]


def check_scheme_eligibility(user_profile: dict) -> list[dict]:
    """
    Evaluates user answers and returns eligible schemes.
    
    user_profile keys:
    - category: 'farmer' | 'student' | 'women' | 'health'
    - land_acres: float (e.g. 1.5, 4.0)
    - has_water_source: bool
    - income: int (e.g. 150000)
    - age: int (e.g. 35)
    """
    selected_cat = user_profile.get("category", "farmer")
    land_acres = float(user_profile.get("land_acres", 2.0) or 2.0)
    income = int(user_profile.get("income", 200000) or 200000)
    age = int(user_profile.get("age", 30) or 30)

    eligible = []

    for s in SCHEMES_DATABASE:
        # Match category or health
        if s["category"] != selected_cat and s["category"] != "health":
            continue

        rules = s.get("eligibility_rules", {})
        is_eligible = True

        # Check land rules
        if rules.get("min_land_acres") is not None and land_acres < rules["min_land_acres"]:
            is_eligible = False

        # Check income rules
        if rules.get("family_income_max") is not None and income > rules["family_income_max"]:
            is_eligible = False
        if rules.get("student_family_income_max") is not None and income > rules["student_family_income_max"]:
            is_eligible = False

        # Check age rules
        if rules.get("age_min") is not None and age < rules["age_min"]:
            is_eligible = False
        if rules.get("age_max") is not None and age > rules["age_max"]:
            is_eligible = False

        if is_eligible:
            eligible.append(s)

    return eligible or [s for s in SCHEMES_DATABASE if s["category"] == selected_cat]
