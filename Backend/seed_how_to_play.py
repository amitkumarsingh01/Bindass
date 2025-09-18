#!/usr/bin/env python3
"""
Script to seed How to Play content in multiple languages.
Run this script to populate the database with the provided content.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the Backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_database

# Content in three languages
HOW_TO_PLAY_CONTENT = {
    "english": """How to Play – Bindass Grand App
English Version

Welcome to Bindass Grand, where fun meets fortune! Follow these simple steps to start playing and win exciting prizes.

1. Choose Your Contest

Contests start from ₹100, ₹200, ₹300, and so on.

Pick the contest you want to participate in based on your preference and budget.

2. Select Vehicle Category

After choosing the contest, you will select a vehicle category range.

The categories are like 1 – 1000, 1001 – 2000, and so on, up to 10,000.

Each category contains 10,000 slots.

3. Pick Your Number

Each slot represents a unique number.

Select the number you want to play with.

The price will be charged based on the contest amount you chose.

4. Lock Your Number

Once you purchase a number, it gets locked.

Nobody else can select the same number once it is bought.

5. Wait for the Contest to Complete

When all 10,000 slots in a category are filled, the contest will be completed.

The result will be announced.

6. Win and Withdraw

Based on the result, winners will be selected.

The prize amount will be credited to the user's account.

You can withdraw the prize within 48 hours.

Additional Information

Make sure to double-check your selected number before purchasing.

Keep your account details safe.

Play responsibly and enjoy the excitement!

Support is available if you face any issues during the game.

Get ready to play, have fun, and win big with Bindass Grand!""",

    "hindi": """हिंदी संस्करण – कैसे खेलें

Bindass Grand में आपका स्वागत है! यहाँ मज़ा और जीत का शानदार मौका है। नीचे दिए गए आसान चरणों का पालन करें और पुरस्कार जीतें।

1. अपना कंटेस्ट चुनें

कंटेस्ट ₹100, ₹200, ₹300 आदि से शुरू होते हैं।

अपनी पसंद और बजट के अनुसार कोई कंटेस्ट चुनें।

2. वाहन श्रेणी चुनें

कंटेस्ट चुनने के बाद वाहन श्रेणी चुनें।

श्रेणियाँ 1 – 1000, 1001 – 2000 और इसी तरह 10,000 तक उपलब्ध हैं।

प्रत्येक श्रेणी में 10,000 स्लॉट्स होते हैं।

3. अपना नंबर चुनें

प्रत्येक स्लॉट एक अलग नंबर को दर्शाता है।

जिस नंबर पर खेलना चाहते हैं उसे चुनें।

चयनित कंटेस्ट के अनुसार राशि आपके खाते से कटेगी।

4. नंबर लॉक करें

नंबर खरीदते ही लॉक हो जाएगा।

कोई दूसरा उपयोगकर्ता वही नंबर नहीं चुन सकता।

5. कंटेस्ट पूरा होने का इंतजार करें

जब किसी श्रेणी के सभी 10,000 स्लॉट्स भर जाएँगे तो कंटेस्ट पूरा होगा।

परिणाम घोषित किए जाएँगे।

6. जीतें और पैसे निकालें

परिणाम के आधार पर विजेता चुने जाएँगे।

पुरस्कार राशि आपके खाते में जमा की जाएगी।

आप 48 घंटे के अंदर राशि निकाल सकते हैं।

अतिरिक्त जानकारी

नंबर खरीदने से पहले उसे ज़रूर जांच लें।

अपने खाते की जानकारी सुरक्षित रखें।

जिम्मेदारी से खेलें और खेल का आनंद लें।

कोई समस्या हो तो सहायता टीम से संपर्क करें।

तैयार हो जाइए और Bindass Grand में खेलकर बड़ा इनाम जीतिए!""",

    "kannada": """ಕನ್ನಡ ಆವೃತ್ತಿ – ಹೇಗೆ ಆಟ ಆಡುವುದು

Bindass Grand ಗೆ ಸ್ವಾಗತ! ಇಲ್ಲಿ ಮಜಾ ಮತ್ತು ಬಹುಮಾನ ಗಳಿಸಲು ಸುಲಭವಾದ ಅವಕಾಶ ಇದೆ। ಕೆಳಗಿನ ಹಂತಗಳನ್ನು ಅನುಸರಿಸಿ ಆಟವನ್ನು ಪ್ರಾರಂಭಿಸಿ।

1. ನಿಮ್ಮ ಕಾನ್ಟೆಸ್ಟ್ ಆಯ್ಕೆ ಮಾಡಿ

ಕಾನ್ಟೆಸ್ಟ್‌ಗಳು ₹100, ₹200, ₹300 ಇವುಗಳಿಂದ ಪ್ರಾರಂಭವಾಗುತ್ತವೆ।

ನಿಮ್ಮ ಇಷ್ಟ ಮತ್ತು ಬಜೆಟ್‌ಗೆ ತಕ್ಕಂತೆ ಒಂದು ಕಾನ್ಟೆಸ್ಟ್ ಆಯ್ಕೆ ಮಾಡಿ।

2. ವಾಹನ ವರ್ಗವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ

ಕಾನ್ಟೆಸ್ಟ್ ಆಯ್ಕೆ ಮಾಡಿದ ನಂತರ ವಾಹನ ವರ್ಗವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ।

ವರ್ಗಗಳು 1 – 1000, 1001 – 2000 ಹೀಗೆ 10,000 ವರೆಗೆ ಇರುತ್ತವೆ।

ಪ್ರತಿ ವರ್ಗದಲ್ಲೂ 10,000 ಸ್ಲಾಟ್‌ಗಳು ಇರುತ್ತವೆ।

3. ನಿಮ್ಮ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ

ಪ್ರತಿ ಸ್ಲಾಟ್ ಒಂದು ವಿಶೇಷ ಸಂಖ್ಯೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ।

ನೀವು ಆಡಲು ಇಚ್ಛಿಸುವ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ।

ಆಯ್ಕೆ ಮಾಡಿದ ಕಾನ್ಟೆಸ್ಟ್‌ಗೆ ಅನುಗುಣವಾಗಿ ಹಣ ಕತ್ತರಿಸಲಾಗುತ್ತದೆ।

4. ಸಂಖ್ಯೆಯನ್ನು ಲಾಕ್ ಮಾಡಿ

ಒಂದು ಸಂಖ್ಯೆಯನ್ನು ಖರೀದಿಸಿದ ಕೂಡಲೇ ಲಾಕ್ ಆಗುತ್ತದೆ।

ಬೇರೆ ಯಾರೂ ಅದೇ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಲು ಸಾಧ್ಯವಾಗುವುದಿಲ್ಲ।

5. ಕಾನ್ಟೆಸ್ಟ್ ಮುಗಿಯುವವರೆಗೆ ಕಾಯಿರಿ

ಒಂದು ವರ್ಗದ ಎಲ್ಲಾ 10,000 ಸ್ಲಾಟ್‌ಗಳು ತುಂಬಿದ ನಂತರ ಕಾನ್ಟೆಸ್ಟ್ ಮುಗಿಯುತ್ತದೆ।

ಫಲಿತಾಂಶವನ್ನು ಪ್ರಕಟಿಸಲಾಗುತ್ತದೆ।

6. ಗೆದ್ದು ಹಣವನ್ನು ಹಿಂಪಡೆಯಿರಿ

ಫಲಿತಾಂಶದ ಆಧಾರದ ಮೇಲೆ ವಿಜೇತರನ್ನು ಆಯ್ಕೆ ಮಾಡಲಾಗುತ್ತದೆ।

ಬಹುಮಾನವನ್ನು ನಿಮ್ಮ ಖಾತೆಗೆ ಜಮಾ ಮಾಡಲಾಗುತ್ತದೆ।

ನೀವು 48 ಗಂಟೆಗಳೊಳಗೆ ಹಣವನ್ನು ಹಿಂಪಡೆಯಬಹುದು।

ಹೆಚ್ಚುವರಿ ಮಾಹಿತಿ

ಸಂಖ್ಯೆಯನ್ನು ಖರೀದಿಸುವ ಮೊದಲು ಖಚಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ।

ನಿಮ್ಮ ಖಾತೆ ವಿವರಗಳನ್ನು ಸುರಕ್ಷಿತವಾಗಿರಿಸಿ।

ಜವಾಬ್ದಾರಿಯಿಂದ ಆಟವಾಡಿ ಮತ್ತು ಮಜಾ ಮಾಡಿ!

ಯಾವುದೇ ಸಮಸ್ಯೆ ಎದುರಾದಲ್ಲಿ ಸಹಾಯಕ್ಕಾಗಿ ಸಂಪರ್ಕಿಸಿ।

ಆಟ ಪ್ರಾರಂಭಿಸಿ, ಮಜಾ ಮಾಡಿ ಮತ್ತು Bindass Grand ನಲ್ಲಿ ದೊಡ್ಡ ಬಹುಮಾನಗಳನ್ನು ಗೆದ್ದಿರಿ!"""
}

async def seed_how_to_play():
    """Seed the how to play content into the database."""
    try:
        db = get_database()
        
        # Check if content already exists
        existing = await db.settings.find_one({"key": "how_to_play"})
        if existing:
            print("How to play content already exists. Updating...")
        else:
            print("Seeding how to play content...")
        
        # Insert or update the content
        await db.settings.update_one(
            {"key": "how_to_play"},
            {
                "$set": {
                    "key": "how_to_play",
                    "value": HOW_TO_PLAY_CONTENT,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }
            },
            upsert=True
        )
        
        print("✅ How to play content seeded successfully!")
        print(f"   - English: {len(HOW_TO_PLAY_CONTENT['english'])} characters")
        print(f"   - Hindi: {len(HOW_TO_PLAY_CONTENT['hindi'])} characters")
        print(f"   - Kannada: {len(HOW_TO_PLAY_CONTENT['kannada'])} characters")
        
    except Exception as e:
        print(f"❌ Error seeding how to play content: {e}")
        return False
    
    return True

async def main():
    """Main function to run the seeding process."""
    print("🚀 Starting How to Play content seeding...")
    
    # Import database connection
    from database import connect_to_mongo, close_mongo_connection
    
    try:
        await connect_to_mongo()
        success = await seed_how_to_play()
        
        if success:
            print("🎉 Seeding completed successfully!")
        else:
            print("💥 Seeding failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Database connection error: {e}")
        sys.exit(1)
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
