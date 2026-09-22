def detect_language(code: str):
    code = code.lower()

    scores = {
        "python": 0,
        "javascript": 0,
        "cpp": 0
    }

    # --- Python indicators ---
    if "def " in code:
        scores["python"] += 2
    if "import " in code:
        scores["python"] += 2
    if "print(" in code:
        scores["python"] += 1
    if ":" in code:
        scores["python"] += 1
    if "self" in code:
        scores["python"] += 1

    # --- JavaScript indicators ---
    if "function " in code:
        scores["javascript"] += 2
    if "console.log" in code:
        scores["javascript"] += 2
    if "var " in code or "let " in code or "const " in code:
        scores["javascript"] += 2
    if "=>" in code:
        scores["javascript"] += 1

    # --- C++ indicators ---
    if "#include" in code:
        scores["cpp"] += 3
    if "std::" in code:
        scores["cpp"] += 2
    if "cout" in code:
        scores["cpp"] += 2
    if "cin" in code:
        scores["cpp"] += 2
    if "int main" in code:
        scores["cpp"] += 3

    # --- Decision ---
    detected = max(scores, key=scores.get)

    # If all scores are 0 → unknown
    if scores[detected] == 0:
        return "Unknown"

    return detected