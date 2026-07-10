# -*- coding: utf-8 -*-
"""
Простой классификатор обращений на основе ключевых слов.
Без внешних API — работает офлайн, подходит для пилотного запуска.
При желании легко заменить на вызов LLM (см. llm_matcher.py).
"""
import re
from data import CATEGORIES, DEFAULT_RESPONSE


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^а-яёa-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify(user_text: str, top_n: int = 1):
    """
    Возвращает список наиболее подходящих категорий, отсортированных по релевантности.
    Если совпадений нет — возвращает DEFAULT_RESPONSE.
    """
    norm_text = normalize(user_text)
    scored = []

    for cat in CATEGORIES:
        score = 0
        for kw in cat["keywords"]:
            kw_norm = normalize(kw)
            if kw_norm in norm_text:
                score += 2  # точное вхождение фразы
            else:
                # частичное совпадение по словам
                kw_words = set(kw_norm.split())
                text_words = set(norm_text.split())
                overlap = len(kw_words & text_words)
                if overlap:
                    score += overlap
        if score > 0:
            scored.append((score, cat))

    if not scored:
        return [DEFAULT_RESPONSE]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [cat for _, cat in scored[:top_n]]


def format_response(cat: dict) -> str:
    lines = [
        f"📌 Категория: {cat['title']}",
        f"\n🏛 Куда обратиться: {cat['organ']}",
    ]
    if cat.get("escalation"):
        lines.append("\n⚠️ Если не помогло:")
        for step in cat["escalation"]:
            lines.append(f"  • {step}")
    lines.append(f"\n📞 Контакты: {cat['contacts']}")
    lines.append(f"🔗 Подать обращение: {cat['link']}")
    if cat.get("documents"):
        lines.append("\n📄 Необходимые документы:")
        for doc in cat["documents"]:
            lines.append(f"  • {doc}")
    lines.append(f"\n⏱ Срок рассмотрения: {cat['deadline']}")
    lines.append(f"⚖️ Нормативная база: {cat['law']}")
    return "\n".join(lines)


if name == "__main__":
    # быстрый тест из консоли
    tests = [
        "Не выплачивают алименты уже три месяца",
        "Соседи шумят каждую ночь, музыка громкая",
        "В магазине продали алкоголь моему 15-летнему сыну",
        "Во дворе не убирают мусор уже месяц",
        "Работодатель не платит зарплату второй месяц",
        "Что-то странное произошло",
    ]
    for t in tests:
        print("=" * 60)
        print("Запрос:", t)
        result = classify(t)[0]
        print(format_response(result))