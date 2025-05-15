def system_user_message(system: str, prompt: str) -> list[dict]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]
def zero_shot_message(prompt: str) -> list[dict]:
    return [
        {"role": "user", "content": prompt}
    ]

