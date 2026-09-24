import re

# Har sign ka metadata, simple description aur synonyms list
SIGN_DICTIONARY = {
    "NAMASTE": {
        "label": "Namaste",
        "description": "Dono haath chest level par aapas mein jude hue (Classic Indian respectful greeting).",
        "category": "Greeting",
        "icon": "namaste",
        "keywords": ["namaste", "pranam", "greetings", "welcome", "aadab"]
    },
    "HELLO": {
        "label": "Hello",
        "description": "Open hand with fingers spread facing forward, waving or saluting from temple.",
        "category": "Greeting",
        "icon": "wave",
        "keywords": ["hello", "hi", "hey", "greetings", "morning", "afternoon"]
    },
    "THANK YOU": {
        "label": "Thank You",
        "description": "Fingers of flat hand touch lips/chin and move outward toward listener (Shukriya).",
        "category": "Politeness",
        "icon": "heart-handshake",
        "keywords": ["thank", "thanks", "grateful", "gratitude", "appreciate", "shukriya", "dhanyawad"]
    },
    "YES": {
        "label": "Yes",
        "description": "Closed fist with thumb upright (Thumbs up / nodding motion).",
        "category": "Response",
        "icon": "thumbs-up",
        "keywords": ["yes", "yeah", "yep", "sure", "correct", "agree", "true", "haan"]
    },
    "NO": {
        "label": "No",
        "description": "Index and middle fingers snap down against thumb.",
        "category": "Response",
        "icon": "thumbs-down",
        "keywords": ["no", "nope", "not", "negative", "never", "disagree", "nahi"]
    },
    "PLEASE": {
        "label": "Please",
        "description": "Flat hand gently across the chest indicating politeness and request (Kripya).",
        "category": "Politeness",
        "icon": "heart",
        "keywords": ["please", "kindly", "request", "kripya"]
    },
    "WATER": {
        "label": "Water",
        "description": "Three middle fingers extended upward forming 'W', tapped near chin (Paani).",
        "category": "Need",
        "icon": "droplet",
        "keywords": ["water", "drink", "thirsty", "fluid", "beverage", "paani"]
    },
    "FOOD": {
        "label": "Food / Hungry",
        "description": "Fingertips pinched together touching lips repeatedly (Khaana / Bhookh).",
        "category": "Need",
        "icon": "utensils",
        "keywords": ["food", "eat", "hungry", "meal", "dinner", "lunch", "breakfast", "khana", "bhookh"]
    },
    "PAIN": {
        "label": "Pain / Hurt",
        "description": "Both index fingers pointing towards each other, twisting in front of chest (Dard).",
        "category": "Medical",
        "icon": "activity",
        "keywords": ["pain", "hurt", "ache", "injury", "wound", "sore", "bleeding", "dard"]
    },
    "DOCTOR": {
        "label": "Doctor / Medical",
        "description": "Fingertips tap pulse area of opposite wrist.",
        "category": "Medical",
        "icon": "cross",
        "keywords": ["doctor", "nurse", "hospital", "clinic", "physician", "medic", "ambulance", "ilaaj"]
    },
    "PEACE": {
        "label": "Peace",
        "description": "Index and middle finger extended upward in 'V' sign.",
        "category": "Social",
        "icon": "smile",
        "keywords": ["peace", "calm", "relax", "victory", "cool", "shanti"]
    },
    "I LOVE YOU": {
        "label": "I Love You",
        "description": "Thumb, index finger, and pinky finger extended simultaneously.",
        "category": "Social",
        "icon": "heart",
        "keywords": ["love", "affection", "care", "dear", "pyaar"]
    },
    "OK": {
        "label": "OK / Good",
        "description": "Index finger and thumb touching to form a circle, other three fingers upright.",
        "category": "Response",
        "icon": "check-circle",
        "keywords": ["ok", "okay", "fine", "alright", "good", "great", "badhiya"]
    }
}

# Do signs milkar natural sentence banate hain (Combinations)
INTENT_TEMPLATES = {
    ("NAMASTE", "THANK YOU"): "Namaste! Thank you very much for your time and kind support.",
    ("NAMASTE", "PLEASE"): "Namaste! Could you please assist me for a moment?",
    ("HELLO", "NAMASTE"): "Namaste and Hello! Warm welcome to everyone.",
    ("PLEASE", "WATER"): "Could I please get some drinking water?",
    ("PLEASE", "FOOD"): "Could I please have some food?",
    ("PLEASE", "DOCTOR"): "Could you please assist me in seeing a doctor?",
    ("PAIN", "DOCTOR"): "I am experiencing pain and would like to see a medical professional.",
    ("HELLO", "THANK YOU"): "Hello! Thank you very much for your kind support.",
    ("YES", "THANK YOU"): "Yes, that is correct! Thank you so much.",
    ("NO", "THANK YOU"): "No, thank you, but I appreciate your offer.",
    ("WATER", "FOOD"): "Could I please get some drinking water and food?",
    ("PLEASE", "THANK YOU"): "Please and thank you so much for your assistance!",
}

# Single sign ke liye sweet and natural sentence
SINGLE_SIGN_TEMPLATES = {
    "NAMASTE": "Namaste! Welcome and heartfelt greetings to you.",
    "HELLO": "Hello! Wishing you a peaceful and pleasant day.",
    "THANK YOU": "Thank you so much! Truly appreciate your kind support.",
    "YES": "Yes, absolutely correct.",
    "NO": "No, thank you.",
    "PLEASE": "Please, I kindly request this.",
    "WATER": "Could I please have a glass of drinking water?",
    "FOOD": "I am feeling hungry, could you please provide some food?",
    "PAIN": "I am experiencing some physical discomfort or pain.",
    "DOCTOR": "Could you please connect me with a doctor or medical professional?",
    "PEACE": "Peace, calmness, and goodwill to all!",
    "I LOVE YOU": "I love and appreciate you deeply!",
    "OK": "All is well, everything is completely okay."
}

def analyze_sentiment_and_urgency(tokens, raw_text=""):
    """Text aur detected signs ko dekhkar emotion aur priority score nikalte hain."""
    combined = " ".join(tokens).upper() + " " + raw_text.upper()
    
    medical_keywords = ["PAIN", "DOCTOR", "HURT", "AMBULANCE", "MEDICINE", "DARD"]
    need_keywords = ["WATER", "FOOD", "HUNGRY", "THIRSTY", "NEED", "PLEASE", "PAANI", "KHANA"]
    positive_keywords = ["THANK", "LOVE", "PEACE", "OK", "GOOD", "GREAT", "HELLO", "YES", "NAMASTE", "SHUKRIYA"]

    medical_hits = [k for k in medical_keywords if k in combined]
    need_hits = [k for k in need_keywords if k in combined]
    positive_hits = [k for k in positive_keywords if k in combined]

    if medical_hits:
        urgency = "MODERATE"
        urgency_score = min(0.7, 0.4 + 0.1 * len(medical_hits))
        sentiment = "Medical Attention"
        emotion = "Care Requested"
    elif need_hits:
        urgency = "NORMAL"
        urgency_score = 0.2
        sentiment = "Request / Need"
        emotion = "Polite Request"
    elif positive_hits:
        urgency = "NORMAL"
        urgency_score = 0.1
        sentiment = "Positive / Friendly"
        emotion = "Warm & Grateful"
    else:
        urgency = "NORMAL"
        urgency_score = 0.05
        sentiment = "Neutral"
        emotion = "Conversational"

    return {
        "urgency": urgency,
        "urgency_score": round(urgency_score, 2),
        "sentiment": sentiment,
        "emotion": emotion
    }

def reconstruct_sentence_from_signs(sign_tokens):
    """Raw detected signs ko jodkar smooth, respectful English sentence banana."""
    if not sign_tokens:
        return "No signs detected yet."
    
    clean_signs = []
    for s in sign_tokens:
        s_upper = s.strip().upper()
        if s_upper in SIGN_DICTIONARY and (not clean_signs or clean_signs[-1] != s_upper):
            clean_signs.append(s_upper)
            
    if not clean_signs:
        return " ".join(sign_tokens).capitalize() + "."

    # Pehle 2-sign intent templates check karo
    for i in range(len(clean_signs) - 1):
        pair = (clean_signs[i], clean_signs[i+1])
        if pair in INTENT_TEMPLATES:
            return INTENT_TEMPLATES[pair]

    # Agar sirf 1 sign hai
    if len(clean_signs) == 1:
        sign = clean_signs[0]
        return SINGLE_SIGN_TEMPLATES.get(sign, f"Expressing: {sign.capitalize()}.")

    # Multi-sign reconstruction logic: Greetings, requests aur needs ko grammatically jodte hain
    phrases = []
    has_namaste = "NAMASTE" in clean_signs
    has_greeting = "HELLO" in clean_signs
    has_please = "PLEASE" in clean_signs
    has_thanks = "THANK YOU" in clean_signs
    has_pain = "PAIN" in clean_signs
    has_doctor = "DOCTOR" in clean_signs
    has_water = "WATER" in clean_signs
    has_food = "FOOD" in clean_signs

    if has_namaste:
        phrases.append("Namaste")
    elif has_greeting:
        phrases.append("Hello")

    if has_please:
        phrases.append("please")

    needs = []
    if has_water:
        needs.append("drinking water")
    if has_food:
        needs.append("some food")
    if has_doctor:
        needs.append("a doctor")
    if has_pain:
        needs.append("pain relief")

    if needs:
        phrases.append(f"could I get {' and '.join(needs)}")

    if has_thanks:
        phrases.append("thank you so much")

    if phrases:
        sentence = ", ".join(phrases)
        return sentence[0].upper() + sentence[1:] + "."

    return " ".join([s.capitalize() for s in clean_signs]) + "."

def text_to_signs(user_text):
    """Spoken words ko identify karke visual sign sequence cards mein map karta hai."""
    if not user_text:
        return []

    words = re.findall(r"\b[A-Za-z']+\b", user_text.lower())
    matched_signs = []
    seen = set()

    for word in words:
        for sign_id, info in SIGN_DICTIONARY.items():
            if word in info["keywords"]:
                if sign_id not in seen:
                    matched_signs.append({
                        "id": sign_id,
                        "label": info["label"],
                        "description": info["description"],
                        "category": info["category"],
                        "icon": info["icon"],
                        "trigger_word": word
                    })
                    seen.add(sign_id)
                break

    return matched_signs
