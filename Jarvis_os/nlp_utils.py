import re

def extract_places(text: str):
    text = text.lower()

    text = re.sub(
        r"(distance|how far|calculate|from|to|between|is|the|what)",
        "",
        text
    )
    text = re.sub(r"\s+", " ", text).strip()

    if " to " in text:
        src, dst = text.split(" to ", 1)
        return src.strip(), dst.strip()

    return None, text.strip()
