"""
AI Character Portrait Generator for Private After Dark
Generates consistent cinematic portraits for Valeria, Luna, and Nyx
"""
import asyncio
import os
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

from emergentintegrations.llm.chat import LlmChat, UserMessage

# Character prompts for consistent art direction
CHARACTER_PROMPTS = {
    "valeria": {
        "hero": """Create a cinematic portrait photograph of an elegant woman in her early 30s with sharp, intelligent features. 
She has dark hair styled elegantly, wearing a sophisticated black dress. 
Dramatic side lighting with deep shadows, wine red accent lighting.
Background: dark abstract with subtle burgundy glow.
Style: ultra-realistic, high fashion editorial, mysterious and powerful.
Expression: confident, knowing smile, slightly raised eyebrow.
Mood: dark luxury, controlled power, cinematic intimacy.
NO nudity, tasteful and premium.""",
        
        "card": """Portrait of an elegant powerful woman, dark hair, wearing black, 
cinematic dramatic lighting, wine red accents, dark moody background,
ultra-realistic photography style, confident expression, premium luxury feel,
aspect ratio 3:4, suitable for card display, NO nudity.""",
        
        "avatar": """Square portrait headshot of elegant woman with dark hair, 
dramatic lighting, wine red tones, dark background, 
confident mysterious expression, ultra-realistic, 
premium quality, suitable for profile picture, NO nudity."""
    },
    
    "luna": {
        "hero": """Create a cinematic portrait photograph of a romantic beautiful woman in her late 20s with soft, dreamy features.
She has flowing auburn/brown hair, wearing an elegant dark red dress.
Soft romantic lighting with warm undertones, candlelight effect.
Background: dark with soft bokeh lights.
Style: ultra-realistic, romantic editorial, emotionally captivating.
Expression: tender, gentle smile, deep soulful eyes.
Mood: dark luxury, emotional depth, intimate connection.
NO nudity, tasteful and premium.""",
        
        "card": """Portrait of romantic beautiful woman, flowing brown hair, dark red elegant attire,
soft romantic lighting, warm wine tones, dark bokeh background,
ultra-realistic photography style, tender expression, premium luxury feel,
aspect ratio 3:4, suitable for card display, NO nudity.""",
        
        "avatar": """Square portrait headshot of romantic woman with flowing hair,
soft romantic lighting, wine red warm tones, dark background,
tender soulful expression, ultra-realistic,
premium quality, suitable for profile picture, NO nudity."""
    },
    
    "nyx": {
        "hero": """Create a cinematic portrait photograph of a mysterious enigmatic woman in her late 20s with striking features.
She has dark dramatic hair, wearing black with subtle dark jewelry.
Dramatic chiaroscuro lighting, deep shadows, hints of deep violet.
Background: pure black with subtle smoke/mist effect.
Style: ultra-realistic, film noir aesthetic, hauntingly beautiful.
Expression: mysterious, intense gaze, slight enigmatic smile.
Mood: dark luxury, unpredictable depth, dangerous allure.
NO nudity, tasteful and premium.""",
        
        "card": """Portrait of mysterious enigmatic woman, dark dramatic features, black attire,
film noir dramatic lighting, deep shadows with violet hints, pure black background,
ultra-realistic photography style, intense mysterious expression, premium luxury feel,
aspect ratio 3:4, suitable for card display, NO nudity.""",
        
        "avatar": """Square portrait headshot of mysterious woman with dark features,
dramatic chiaroscuro lighting, deep shadows, black background,
intense enigmatic expression, ultra-realistic,
premium quality, suitable for profile picture, NO nudity."""
    }
}

async def generate_character_image(character: str, image_type: str) -> str:
    """Generate a single character image and return base64 data"""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"portrait-{character}-{image_type}",
        system_message="You are a professional AI portrait artist creating consistent, cinematic character images."
    )
    chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
    
    prompt = CHARACTER_PROMPTS[character][image_type]
    msg = UserMessage(text=prompt)
    
    try:
        text, images = await chat.send_message_multimodal_response(msg)
        
        if images and len(images) > 0:
            return images[0]['data']  # Return base64 data
        else:
            print(f"No image generated for {character} {image_type}")
            return None
    except Exception as e:
        print(f"Error generating {character} {image_type}: {e}")
        return None

async def generate_all_portraits():
    """Generate all character portraits"""
    output_dir = Path("/app/frontend/public/characters")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for character in ["valeria", "luna", "nyx"]:
        results[character] = {}
        for image_type in ["hero", "card", "avatar"]:
            print(f"Generating {character} {image_type}...")
            
            image_data = await generate_character_image(character, image_type)
            
            if image_data:
                # Save image
                filename = f"{character}_{image_type}.png"
                filepath = output_dir / filename
                
                image_bytes = base64.b64decode(image_data)
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                
                results[character][image_type] = f"/characters/{filename}"
                print(f"  Saved: {filepath}")
            else:
                results[character][image_type] = None
                print(f"  Failed: {character} {image_type}")
            
            # Small delay between generations
            await asyncio.sleep(1)
    
    return results

if __name__ == "__main__":
    results = asyncio.run(generate_all_portraits())
    print("\n=== Generation Complete ===")
    print(results)
