


def work(messages=None, npc1=None, npc2=None):
    import os
    from llama_cpp import Llama
    import random

    from pyexpat.errors import messages

    from visual import generate_avatar
    from pathlib import Path
    import difflib
    import re

    GENRES = [
        "городская фэнтези",
        "киберпанк",
        "детектив",
        "романтика",
        "хоррор",
        "историческая драма",
        "научная фантастика",
        "мистика"
    ]

    genre = random.choice(GENRES)
    CHARACTERS_MALES = ["Павел", "Дмитрий", "Антон", "Рубанок", "Антон", "Столяров", "Пермаш"]
    CHARACTERS_FEMALES=["Василиса","Маша", "Алина", "Ксения","Полина", "Вероника"]
    ALL_NAMES = CHARACTERS_MALES + CHARACTERS_FEMALES
    ESCAPED_NAMES = sorted([re.escape(name) for name in ALL_NAMES], key=len, reverse=True)
    NAME_PATTERN = f"({'|'.join(ESCAPED_NAMES)});"
    HAIR_LENGHTS=["long","middle","short"]
    HAIR_COLORS=["red","brown","black","white","purple"]
    EYES_COLORS=["blue","brown","purple","red","white"]
    CLOTHES_COLORS=["black","brown","dark-blue"]
    """for name in CHARACTERS_MALES:
        generate_avatar(gender="boy", hair_lenght=random.choice(HAIR_LENGHTS), hair_color=random.choice(HAIR_COLORS),
                        eyes_color=random.choice(EYES_COLORS), clothes_color=random.choice(CLOTHES_COLORS), name=name)
    for name in CHARACTERS_FEMALES:
        generate_avatar(gender="girl", hair_lenght=random.choice(HAIR_LENGHTS), hair_color=random.choice(HAIR_COLORS),
                        eyes_color=random.choice(EYES_COLORS), clothes_color=random.choice(CLOTHES_COLORS), name=name)"""
    # Сколько слоёв загружать на GPU? Для 8 ГБ VRAM — ~35–40
    n_gpu_layers = 40  # попробуй 35, если вылетает OOM
    MODEL_PATH=r".\ai\text\llama-3-8b-instruct-q4_k_m.gguf"
    PROMPT_FILE=r".\ai\text\prompt.txt"
    print("Загрузка модели...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=40,
        n_ctx=8192,
        n_threads=6,
        verbose=False
    )


    def load_prompt(file_path: str) -> str:
        if not os.path.exists(file_path):
            # Если файла нет — используем встроенный промпт (для тестов!)
            return (
                "Ты — мастер интерактивной визуальной новеллы в жанре {genre}. "
                "Ты управляешь двумя персонажами: {npc1} и {npc2}. Игрок — главный герой.\n\n"
                "Правила:\n"
                "- Пиши мысли главного героя в формате: *«...»*\n"
                "- Диалоги строго: \"{ИМЯ}; {РЕПЛИКА}\"\n"
                "- Ответ должен быть 3–6 предложений.\n"
                "- Всегда завершай так, чтобы игрок мог ответить.\n"
                "- Никогда не предлагай варианты — игрок сам решает, что делать.\n"
                "- Подстраивай мысли под действия игрока и обстановку.\n"
                "- Не повторяйся. Развивай сюжет.\n\n"
                "Начни сцену."
            )
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # Экранируем любые одиночные { или } в тексте, кроме {npc1}/{npc2}
            # Но проще — использовать .replace или просто не использовать {} в prompt.txt
            return content

    def generate_opening(genre: str) -> str:
        prompt = f"Напиши 2–3 предложения сеттинга сюжета (место, атмосфера, суть). Без имён."
        out = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        return out["choices"][0]["message"]["content"].strip()

    def generate_response(messages):
        # Ограничиваем контекст
        recent = messages[-6:] if len(messages) > 6 else messages
        output = llm.create_chat_completion(
            messages=recent,
            max_tokens=140,
            temperature=0.65,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["\n\n", "Ты ", "Что ты", "Теперь", "Игрок", "Главный герой", "==="]
        )
        text = output["choices"][0]["message"]["content"].strip()

        return text # максимум 3 реплики

    def chat_step(messages):
        output = llm.create_chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.75,
            top_p=0.9,
            repeat_penalty=1.15
        )
        return output["choices"][0]["message"]["content"].strip()
    import re


    def extract_first_word_before_semicolon(raw_prefix: str) -> str:
        """
        Из строки вида "  М а ш а !@#$ " извлекает первое слово: "Маша"
        — удаляет всё, кроме букв (кириллица/латиница), склеивает, берёт первое слово.
        """
        # Оставляем только буквы и пробелы (чтобы не склеивать разные слова)
        cleaned = re.sub(r'[^а-яА-ЯёЁa-zA-Z\s]', ' ', raw_prefix)
        # Разбиваем по пробелам и берём первое непустое слово
        words = cleaned.split()
        return words[0] if words else ""

    def fix_name(raw_name_part: str, candidates=ALL_NAMES, threshold=0.8):
        """Извлекает первое слово и сопоставляет с ближайшим именем."""
        candidate_word = extract_first_word_before_semicolon(raw_name_part)
        if not candidate_word:
            return None
        matches = difflib.get_close_matches(candidate_word, candidates, n=1, cutoff=threshold)
        return matches[0] if matches else None

    def clean_utterance(text: str) -> str:
        """Удаляет <...>, {...}, [...] и нормализует пробелы."""
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'\[[^\]]*\]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_and_correct_replies(text: str):
        """
        Извлекает реплики из текста, даже если они идут подряд в одной строке.
        Пример: "Маша; привет Дмитрий; здравствуй"
        """
        text = text.strip()
        if text.endswith("</s>"):
            text = text[:-5].rstrip()

        # Находим все вхождения вида "Имя;"
        matches = list(re.finditer(NAME_PATTERN, text))
        if not matches:
            return []

        replies = []
        for i, match in enumerate(matches):
            name = match.group(1)
            start_pos = match.end()  # сразу после ";"
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            utterance = text[start_pos:end_pos]
            clean_utt = clean_utterance(utterance)
            if clean_utt:
                replies.append(f"{name}; {clean_utt}")
        return replies

    if not messages:
        print("=== 🌌 Генерация мира ===")
        opening = generate_opening(genre)
        npc1, npc2 = random.sample(CHARACTERS_MALES+CHARACTERS_FEMALES, 2)
        gender1 = "girl" if npc1 in CHARACTERS_FEMALES else "boy"
        gender2 = "girl" if npc2 in CHARACTERS_FEMALES else "boy"
        generate_avatar(gender=gender1,hair_lenght=random.choice(HAIR_LENGHTS),hair_color=random.choice(HAIR_COLORS),eyes_color=random.choice(EYES_COLORS),clothes_color=random.choice(CLOTHES_COLORS),name=npc1)
        generate_avatar(gender=gender2,hair_lenght=random.choice(HAIR_LENGHTS),hair_color=random.choice(HAIR_COLORS),eyes_color=random.choice(EYES_COLORS),clothes_color=random.choice(CLOTHES_COLORS),name=npc2)
        print(f"🎭 {genre}\n🌍 {opening}\n")
        print(f"👥 Персонажи: {npc1}, {npc2}\n")
        # Первая инструкция — как обычное сообщение от пользователя
        intro = (
            f"Правила:\n"
            f"- Ты играешь ТОЛЬКО за {npc1} и {npc2}.\n"
            f"- Каждая реплика строго: \"ИМЯ; ТЕКСТ\".\n"
            f"- Символ \";\" можно использовать только как разделитель между именем того кто говорит и его фразой и никак иначе.\n"
            f"- Никаких мыслей игрока, вопросов, описаний, пояснений. Говоришь только от лица {npc1} и {npc2}.\n"
            f"- Максимум 3 реплики за раз.\n"
            f"- После реплик — остановись. Жди мой ввод.\n"
            f"Сеттинг: {opening}. Начни."
        )
        messages = [{"role": "user", "content": intro}]
    log_file = Path("text.txt")
    log_file.write_text("", encoding="utf-8")

    print("=== 🎭 Игра началась ===\n")

    try:
        response = generate_response(messages)
        if not response.strip():
            response = f"{npc1}; ...?"
        clean_replies = extract_and_correct_replies(response)
        for line in clean_replies:
            print(line)
        print()
        with open(log_file, "a", encoding="utf-8") as f:
            for rep in clean_replies:
                f.write(rep + "\n")

        messages.append({"role": "assistant", "content": response})


    except Exception:
        pass
    return messages, npc1, npc2