# ================== ГЛАВНЫЙ ГЕРОЙ ==================

default main_hero_name = "Я"
define main_hero = Character("[main_hero_name]", color="#ffffff")

# ================= ИМЕНА ПЕРСОНАЖЕЙ =================
$ Anton = 'Антон'
$ Vasilisa = 'Василиса'
$ Stolyarov = 'Столяров'
$ Pavel = 'Павел'
$ Dmitriy = 'Дмитрий'
$ Permash = 'Пермаш'
$ Rubanok = 'Рубанок'
$ Masha = 'Маша'
$ Alina = 'Алина'
$ Kseniya = 'Ксения'
$ Polina = 'Полина'
$ Veronika = 'Вероника'


# ================== ПЕРЕДВИЖЕНИЕ ПЕРСОНАЖЕЙ ==================
transform pos_left:
    xalign 0.0
    yalign 1.0

transform pos_center:
    xalign 0.5
    yalign 1.0

transform pos_right:
    xalign 1.0
    yalign 1.0


# ================== PYTHON-ФУНКЦИИ ==================

init python:

    name_to_tag = {
        "Антон": "anton",
        "Василиса": "vasilisa",
        "Столяров": "stolyarov",
        "Павел": "pavel",
        "Дмитрий": "dmitriy",
        "Пермаш": "permash",
        "Рубанок": "rubanok",
        "Маша": "masha",
        "Алина": "alina",
        "Ксения": "kseniya",
        "Полина": "polina",
        "Вероника": "veronika",
    }

    

    def ensure_work_story(base_filename, work_filename):
        """
        Гарантирует, что рабочий файл сюжета существует.
        Если нет — копирует из базового.[web:146][web:150]
        """
        import os

        base_path = renpy.config.basedir + "/game/" + base_filename
        work_path = renpy.config.basedir + "/game/" + work_filename

        if not os.path.exists(work_path):
            # если рабочего нет — копируем из базового
            with open(base_path, "r", encoding="utf-8") as f_in:
                data = f_in.read()
            with open(work_path, "w", encoding="utf-8") as f_out:
                f_out.write(data)

    def load_last_dialogue_line(filename):
            """
            Читает РАБОЧИЙ файл и возвращает ТОЛЬКО последнюю непустую строку
            формата (name, text) или None, если файл пустой.[web:155][web:157]
            """
            path = renpy.config.basedir + "/game/" + filename

            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # убираем пустые строки с конца
            while lines and not lines[-1].strip():
                lines.pop()

            if not lines:
                return None

            last_line = lines[-1].strip()

            if ";" not in last_line:
                return None

            name, text = last_line.split(";", 1)
            name = name.strip()
            text = text.strip()

            if not name or not text:
                return None

            return (name, text)

    def append_player_reply_to_story(filename, player_name, npc_name, player_text):
        """
        Добавляет в КОНЕЦ рабочего файла сюжета строку вида:
        player_name->npc_name; текст игрока
        """
        path = renpy.config.basedir + "/game/" + filename
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{player_name}; {player_text}\n")

    def reset_story_to_base(base_filename, work_filename):
        """
        В КОНЦЕ ИГРЫ:
        Перезаписывает рабочий файл базовым (сбрасывает историю).[web:144][web:146]
        """
        base_path = renpy.config.basedir + "/game/" + base_filename
        work_path = renpy.config.basedir + "/game/" + work_filename

        with open(base_path, "r", encoding="utf-8") as f_in:
            data = f_in.read()
        with open(work_path, "w", encoding="utf-8") as f_out:
            f_out.write(data)


    current_chars = []

    def update_characters_visuals(speaking_name):
        """
        speaking_name — русское имя (из файла).
        Логика:
        - если персонажа ещё нет в current_chars — добавляем в конец;
        - если >3 персонажей, убираем самого первого;
        - раскладываем:
            1 персонаж — центр
            2 персонажа — первый слева, второй центр
            3 персонажа — 1 слева, 2 центр, 3 справа
        - при обновлении >3:
            старого hide, новые: 2->лево, 3->право, новый->центр.
        """
        global current_chars

        # если имя неизвестно — ничего не делаем
        if speaking_name not in name_to_tag:
            return

        # если этого имени ещё нет в списке — добавляем
        if speaking_name not in current_chars:
            current_chars.append(speaking_name)

        # если стало > 3, удаляем самого старого
        if len(current_chars) > 3:
            oldest = current_chars.pop(0)
            # спрятать самого старого
            tag = name_to_tag.get(oldest, None)
            if tag is not None:
                renpy.hide(tag)

        # теперь у нас 1..3 персонажа в current_chars
        n = len(current_chars)

        if n == 1:
            # один — по центру
            name0 = current_chars[0]
            tag0 = name_to_tag.get(name0, None)
            if tag0:
                renpy.show(tag0, at_list=[pos_center])
        elif n == 2:
            # два — [0] слева, [1] центр
            name0, name1 = current_chars
            tag0 = name_to_tag.get(name0, None)
            tag1 = name_to_tag.get(name1, None)
            if tag0:
                renpy.show(tag0, at_list=[pos_left])
            if tag1:
                renpy.show(tag1, at_list=[pos_center])
        elif n == 3:
            # три — [0] слева, [1] центр, [2] справа
            name0, name1, name2 = current_chars
            tag0 = name_to_tag.get(name0, None)
            tag1 = name_to_tag.get(name1, None)
            tag2 = name_to_tag.get(name2, None)
            if tag0:
                renpy.show(tag0, at_list=[pos_left])
            if tag1:
                renpy.show(tag1, at_list=[pos_center])
            if tag2:
                renpy.show(tag2, at_list=[pos_right])

# ================== ИГРА ==================

label start:
    init python:
        from llm import work
        MESSAGES,npc1,npc2=work()

    play music 'audio/bg.mp3' fadein (2.0) volume (0.07)

    image anton = "Антон.png"
    image vasalisa = "Василиса.png"
    image stolyarov = "Столяров.png"
    image pavel = "Павел.png"
    image dmitriy = "Дмитрий.png"
    image permash = "Пермаш.png"
    image rubanok = "Рубанок.png"
    image masha = "Маша.png"
    image alina = "Алина.png"
    image kseniya = "Ксения.png"
    image polina = "Полина.png"
    image veronika = "Вероника.png"


    scene bg room

    $ base_story_file = "text_base.txt"
    $ work_story_file = "text.txt"

    # Гарантируем наличие рабочего файла
    $ ensure_work_story(base_story_file, work_story_file)


    while True:

        image anton = "Антон.png"
        image vasalisa = "Василиса.png"
        image stolyarov = "Столяров.png"
        image pavel = "Павел.png"
        image dmitriy = "Дмитрий.png"
        image permash = "Пермаш.png"
        image rubanok = "Рубанок.png"
        image masha = "Маша.png"
        image alina = "Алина.png"
        image kseniya = "Ксения.png"
        image polina = "Полина.png"
        image veronika = "Вероника.png"
        
        scene bg room

        # --- 1. Берём ПОСЛЕДНЮЮ строку из файла ---
        $ last_entry = load_last_dialogue_line(work_story_file)

        if last_entry is not None:
            $ name, text = last_entry

            # ОБНОВИТЬ СПРАЙТЫ В ЗАВИСИМОСТИ ОТ ИМЕНИ
            $ update_characters_visuals(name)

            # Показать реплику
            $ renpy.say(name, text)


        # --- 2. Ввод игрока ---
        $ player_answer = renpy.input("Твой ответ (или «Конец» для выхода):")
        $ player_answer = player_answer.strip()

        if player_answer.lower() == "конец":
            main_hero "Хорошо, на этом закончим."
            $ reset_story_to_base(base_story_file, work_story_file)
            return

        if player_answer:
            # в ответ логично писать от того же имени, которое было в последней строке
            $ last_name = name if last_entry is not None else "Система"

            # 1) дописываем ответ игрока в КОНЕЦ файла
            $ append_player_reply_to_story(work_story_file, main_hero_name, last_name, player_answer)

            init python:
                from llm import work
                MESSAGES.append({"role": "user", "content": player_answer})
                MESSAGES,npc1,npc2=work(MESSAGES,npc1,npc2)

