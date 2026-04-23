# Fonction pour calculer le coût d'une requête en fonction du modèle et du nombre de tokens utilisés

def compute_cost(model: str, input_tokens: int, output_tokens: int):
    # Exemple pour Claude 3 Sonnet (à adapter selon modèle)
    # Prix en $ par 1k tokens
    prices = {
        "claude-3-sonnet-latest": {"input": 0.003, "output": 0.015},
        "claude-3-opus-latest": {"input": 0.015, "output": 0.075},
        "claude-haiku-4-5-20251001": {"input": 0.00025, "output": 0.00125},
    }

    p = prices.get(model, {"input": 0, "output": 0})
    cost = (input_tokens / 1000 * p["input"]) + (output_tokens / 1000 * p["output"])
    return round(cost, 6)
