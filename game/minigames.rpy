# ============================================================
#  ПЕТЛЯ ДОВЕРИЯ — Мини-игры
#  Экраны и логика для 4 мини-игр
# ============================================================

# ============================================================
#  ОБЩАЯ ИНФРАСТРУКТУРА
# ============================================================

init python:
    import time as _time
    import os as _os

    # --- Палитра терминального стиля ---
    TERM_BG      = "#0a0e14"
    TERM_GREEN   = "#00ff41"
    TERM_CYAN    = "#00e5ff"
    TERM_RED     = "#ff1744"
    TERM_AMBER   = "#ffab00"
    TERM_DIM     = "#1a3a1a"
    TERM_GRID_BG = "#0d1117"

    # ========================================================
    #  Мини-игра 1: Взлом протокола — BinaryPuzzle (Такудзу)
    # ========================================================
    class BinaryPuzzle(object):
        """
        Головоломка Такудзу 4x4.
        Правила:
        - Каждая строка и столбец содержат ровно 2 нуля и 2 единицы
        - Нет трёх одинаковых символов подряд (по горизонтали/вертикали)
        """
        def __init__(self):
            # Единственное решение
            self.solution = [
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 1, 0],
            ]
            # Сетка игрока: None = пусто, 0 или 1 = установлено
            self.grid = [[None]*4 for _ in range(4)]
            self.locked = [[False]*4 for _ in range(4)]

            # Предзаполненные подсказки (зафиксированы)
            hints = [(0, 0), (0, 3), (1, 1), (1, 2), (2, 0), (2, 3), (3, 1), (3, 2)]
            for r, c in hints:
                self.grid[r][c] = self.solution[r][c]
                self.locked[r][c] = True

        def toggle_cell(self, row, col):
            """Цикл: None -> 0 -> 1 -> None"""
            if self.locked[row][col]:
                return
            val = self.grid[row][col]
            if val is None:
                self.grid[row][col] = 0
            elif val == 0:
                self.grid[row][col] = 1
            else:
                self.grid[row][col] = None
            renpy.restart_interaction()

        def is_complete(self):
            for r in range(4):
                for c in range(4):
                    if self.grid[r][c] is None:
                        return False
            return True

        def check_valid(self):
            """Проверить решение по правилам такудзу."""
            if not self.is_complete():
                return False
            for i in range(4):
                row = [self.grid[i][c] for c in range(4)]
                col = [self.grid[r][i] for r in range(4)]
                # Равное количество 0 и 1
                if row.count(0) != 2 or row.count(1) != 2:
                    return False
                if col.count(0) != 2 or col.count(1) != 2:
                    return False
                # Нет трёх подряд
                for line in [row, col]:
                    for j in range(2):
                        if line[j] == line[j+1] == line[j+2]:
                            return False
            return True

        def get_errors(self):
            """Множество (row, col) ячеек с ошибками — для подсветки."""
            errors = set()
            for i in range(4):
                row = [self.grid[i][c] for c in range(4)]
                col = [self.grid[r][i] for r in range(4)]
                for j in range(2):
                    if row[j] is not None and row[j] == row[j+1] == row[j+2]:
                        errors.update([(i, j), (i, j+1), (i, j+2)])
                    if col[j] is not None and col[j] == col[j+1] == col[j+2]:
                        errors.update([(j, i), (j+1, i), (j+2, i)])
            return errors

    # ========================================================
    #  Мини-игра 2: Допрос — InterrogationState
    # ========================================================
    class InterrogationState(object):
        """Состояние допроса Елены. 4 хода, тревога 0-100."""
        def __init__(self):
            self.pulse = 80
            self.anxiety = 25
            self.turn = 1
            self.max_turns = 4
            self.failed = False
            self.last_response = ""

            # Ответы Елены: turn -> tactic -> (anxiety_delta, new_pulse, response)
            self.responses = {
                1: {
                    "pressure": (25, 110,
                        "Ты... ты с ума сошёл! Я здесь жертва, как и ты!"),
                    "empathy": (-10, 75,
                        "Спасибо... Да, может быть, ты прав. Мне страшно."),
                    "bluff": (10, 95,
                        "Что?.. Откуда ты это знаешь? Нет, ты блефуешь."),
                    "reveal": (5, 85,
                        "Ампула? Я... просто нашла её на полу, хотела спрятать."),
                },
                2: {
                    "pressure": (20, 120,
                        "Прекрати давить на меня! Я ничего не скрываю!"),
                    "empathy": (-5, 78,
                        "Ладно... Я расскажу немного. Я видела такие ампулы раньше."),
                    "bluff": (15, 100,
                        "Ты не можешь этого знать! Ты... ты блефуешь!"),
                    "reveal": (10, 90,
                        "Хорошо, это снотворное. Но я не использовала его!"),
                },
                3: {
                    "pressure": (25, 130,
                        "ХВАТИТ! Ещё одно слово — и я нажму тревожную кнопку!"),
                    "empathy": (-10, 72,
                        "Ладно... я расскажу. Мне заплатили пронести ампулу."),
                    "bluff": (15, 105,
                        "Нет! Ты не можешь знать о корпорации! Это невозможно!"),
                    "reveal": (5, 88,
                        "Пульс? Да, я нервничаю. Потому что ты мне угрожаешь!"),
                },
                4: {
                    "pressure": (30, 140,
                        "ВСЁ! Я БОЛЬШЕ НЕ МОГУ! ОСТАВЬ МЕНЯ В ПОКОЕ!"),
                    "empathy": (-15, 68,
                        "Хорошо... Хорошо. Я всё расскажу. Мне заплатили..."),
                    "bluff": (10, 100,
                        "Я не Кукловод! Клянусь! Я просто... перевозчик."),
                    "reveal": (0, 82,
                        "Ладно. Ладно! Я расскажу всё. Только обещай молчать."),
                },
            }

        def apply_tactic(self, tactic):
            if self.turn > self.max_turns or self.failed:
                return
            data = self.responses[self.turn][tactic]
            delta, new_pulse, response = data
            self.anxiety = min(100, max(0, self.anxiety + delta))
            self.pulse = new_pulse
            self.last_response = response
            if self.anxiety >= 100:
                self.failed = True
            self.turn += 1
            renpy.restart_interaction()

        def is_success(self):
            return self.turn > self.max_turns and not self.failed and self.anxiety < 50

        def is_finished(self):
            return self.turn > self.max_turns or self.failed

    # ========================================================
    #  Мини-игра 3: Распределение воздуха — AirDistribution
    # ========================================================
    class AirDistribution(object):
        """
        Управление кислородом в 4 секторах.
        Всего 40 ед., начало: 25/5/5/5. Цель: все >= 10.
        """
        SECTORS = [
            ("Жилой блок",        "Виктор", "#e07070"),
            ("Тех. отсек",        "Ян",     "#a8e0b0"),
            ("Медблок",           "Елена",  "#c8a8d8"),
            ("Центр. шлюз",       "Алекс",  "#a8d8ea"),
        ]

        def __init__(self):
            self.levels = [25, 5, 5, 5]
            self.moves_left = 5

        def can_transfer(self, from_idx, to_idx, amount):
            if from_idx == to_idx:
                return False
            if self.levels[from_idx] < amount:
                return False
            if self.moves_left <= 0:
                return False
            return True

        def transfer(self, from_idx, to_idx, amount):
            if not self.can_transfer(from_idx, to_idx, amount):
                return
            self.levels[from_idx] -= amount
            self.levels[to_idx] += amount
            self.moves_left -= 1
            renpy.restart_interaction()

        def is_ideal(self):
            return all(lv >= 10 for lv in self.levels)

        def get_result(self):
            """1 = идеал, 2 = прагматик, 0 = провал."""
            if self.is_ideal():
                return 1
            safe = sum(1 for lv in self.levels if lv >= 10)
            if safe >= 2:
                return 2
            return 0

        def danger_color(self, level):
            if level >= 10:
                return TERM_GREEN
            elif level >= 5:
                return TERM_AMBER
            return TERM_RED

    # ========================================================
    #  Мини-игра 4: Обыск в темноте — SearchGameState
    # ========================================================
    class SearchGameState(object):
        """Состояние мини-игры обыска."""
        ITEMS = [
            {"name": "Блокнот",      "hint": "под матрасом",       "x": 350,  "y": 680, "r": 70},
            {"name": "Брелок",       "hint": "в кармане куртки",   "x": 1450, "y": 320, "r": 60},
            {"name": "Следы крови",  "hint": "у вент. решётки",    "x": 1050, "y": 780, "r": 75},
        ]
        TRAPS = [
            {"name": "Скрипучая половица", "x": 700,  "y": 500, "r": 90},
            {"name": "Пустые банки",       "x": 1250, "y": 620, "r": 80},
        ]
        LIGHT_RADIUS = 150

        def __init__(self):
            self.items_found = [False, False, False]
            self.traps_triggered = [False, False]
            self.detection = 0.0
            self.result = None

        def check_traps(self, mx, my):
            """Проверить попадание мыши в ловушку."""
            if self.result is not None:
                return
            for i, trap in enumerate(self.TRAPS):
                if self.traps_triggered[i]:
                    continue
                dx = mx - trap["x"]
                dy = my - trap["y"]
                if dx * dx + dy * dy < trap["r"] * trap["r"]:
                    self.traps_triggered[i] = True
                    self.detection = min(100.0, self.detection + 20.0)
                    renpy.notify(trap["name"] + "! Риск +20%")
                    if self.detection >= 100.0:
                        self.result = False

        def tick_detection(self):
            """Пассивный прирост детекции (вызывается раз в секунду)."""
            if self.result is not None:
                return
            self.detection = min(100.0, self.detection + 1.5)
            if self.detection >= 100.0:
                self.result = False
            renpy.restart_interaction()

        def collect_item(self, index):
            if self.items_found[index] or self.result is not None:
                return
            self.items_found[index] = True
            renpy.notify("Найдено: " + self.ITEMS[index]["name"])
            if all(self.items_found):
                self.result = True
            renpy.restart_interaction()

        def in_light(self, ix, iy, mx, my):
            dx = ix - mx
            dy = iy - my
            return dx * dx + dy * dy < self.LIGHT_RADIUS * self.LIGHT_RADIUS

        def found_count(self):
            return sum(1 for f in self.items_found if f)

    # ========================================================
    #  Генерация изображения фонарика для мини-игры 4
    # ========================================================
    def _generate_flashlight():
        """Создать круглый градиент тьмы с прозрачным центром."""
        import pygame
        radius = SearchGameState.LIGHT_RADIUS
        size = radius * 2
        r_sq = float(radius * radius)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Заполнить тёмным
        surf.fill((0, 0, 0, 220))
        # Внутри круга — градиент от прозрачного (центр) к тёмному (край)
        for yy in range(size):
            dy = yy - radius
            dy_sq = dy * dy
            if dy_sq >= r_sq:
                continue
            dx_max = int((r_sq - dy_sq) ** 0.5)
            for xx in range(radius - dx_max, radius + dx_max + 1):
                dx = xx - radius
                dist_sq = dx * dx + dy_sq
                t = (dist_sq / r_sq) ** 0.5
                alpha = int(220 * t * t)
                surf.set_at((xx, yy), (0, 0, 0, alpha))
        path = _os.path.join(renpy.config.gamedir, "flashlight_circle.png")
        pygame.image.save(surf, path)

    # Генерировать при старте
    try:
        _generate_flashlight()
    except Exception:
        pass

    _FL_RADIUS = SearchGameState.LIGHT_RADIUS
    _FL_IMG_PATH = _os.path.join(renpy.config.gamedir, "flashlight_circle.png")


# ============================================================
#  СТИЛИ МИНИ-ИГР
# ============================================================

style mg_title_text:
    font "DejaVuSans.ttf"
    size 42
    color "#00ff41"
    outlines [(2, "#003300", 0, 0)]
    text_align 0.5
    xalign 0.5

style mg_label_text:
    font "DejaVuSans.ttf"
    size 28
    color "#00e5ff"

style mg_body_text:
    font "DejaVuSans.ttf"
    size 24
    color "#00ff41"

style mg_button:
    background "#1a3a1a"
    hover_background "#2a5a2a"
    padding (16, 8, 16, 8)
    xminimum 200

style mg_button_text:
    font "DejaVuSans.ttf"
    size 26
    color "#00ff41"
    hover_color "#ffffff"
    xalign 0.5


# ============================================================
#  ЭКРАН МИНИ-ИГРЫ 1: ВЗЛОМ ПРОТОКОЛА
# ============================================================

screen minigame_hack():
    modal True
    zorder 100
    predict False

    default puzzle = BinaryPuzzle()
    default timer_sec = 90
    default timed_out = False
    default solved = False
    default check_pressed = False

    # --- Фон ---
    add Solid(TERM_BG)

    # --- Таймер (тикает каждую секунду) ---
    if not timed_out and not solved:
        timer 1.0 repeat True action If(
            timer_sec > 0,
            true=SetScreenVariable("timer_sec", timer_sec - 1),
            false=SetScreenVariable("timed_out", True)
        )

    # --- Основной контент ---
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 20

        # Заголовок
        text "[[ ВЗЛОМ ПРОТОКОЛА ]]" style "mg_title_text"

        # Правила
        text "Заполните пустые ячейки цифрами 0 или 1." style "mg_body_text" xalign 0.5
        text "В каждой строке и столбце — ровно 2 нуля и 2 единицы. Нет трёх одинаковых подряд." style "mg_body_text" xalign 0.5 size 20

        null height 5

        # Таймер
        hbox:
            xalign 0.5
            spacing 10
            text "ВРЕМЯ:" style "mg_label_text" yalign 0.5
            if timer_sec > 20:
                text "[timer_sec] сек" style "mg_body_text" yalign 0.5
            else:
                text "[timer_sec] сек" style "mg_body_text" yalign 0.5 color TERM_RED

        # Бар таймера
        hbox:
            xalign 0.5
            frame:
                xysize (400, 20)
                background "#1a1a2e"
                frame:
                    yalign 0.5
                    xalign 0.0
                    if timer_sec > 0:
                        xsize int(400 * timer_sec / 90)
                    else:
                        xsize 0
                    ysize 20
                    if timer_sec > 20:
                        background TERM_GREEN
                    else:
                        background TERM_RED

        null height 15

        # Сетка 4x4
        $ errors = puzzle.get_errors() if check_pressed else set()

        grid 4 4:
            xalign 0.5
            spacing 6

            for r in range(4):
                for c in range(4):
                    $ val = puzzle.grid[r][c]
                    $ is_locked = puzzle.locked[r][c]
                    $ is_error = (r, c) in errors

                    $ cell_bg = "#330011" if is_error else ("#0d2818" if is_locked else TERM_GRID_BG)
                    $ cell_text = str(val) if val is not None else ""
                    $ cell_color = TERM_RED if is_error else (TERM_CYAN if is_locked else TERM_GREEN)

                    button:
                        xysize (110, 110)
                        background cell_bg
                        if not is_locked and not timed_out and not solved:
                            hover_background TERM_DIM
                            action [SetScreenVariable("check_pressed", False), Function(puzzle.toggle_cell, r, c)]
                        else:
                            action NullAction()

                        text cell_text:
                            size 48
                            color cell_color
                            font "DejaVuSans.ttf"
                            xalign 0.5
                            yalign 0.5

        null height 20

        # Кнопка проверки
        if not timed_out and not solved:
            textbutton "[[ ПРОВЕРИТЬ ]]":
                style "mg_button"
                text_style "mg_button_text"
                xalign 0.5
                sensitive puzzle.is_complete()
                action [
                    SetScreenVariable("check_pressed", True),
                    If(puzzle.check_valid(),
                       true=SetScreenVariable("solved", True),
                       false=Notify("Ошибка! Проверьте правила."))
                ]

        # Результат — успех
        if solved:
            null height 10
            text ">> ДОСТУП РАЗРЕШЁН <<" style "mg_title_text" color TERM_CYAN
            timer 1.5 action Return(True)

        # Результат — время вышло
        if timed_out:
            null height 10
            text ">> ВРЕМЯ ИСТЕКЛО <<" style "mg_title_text" color TERM_RED
            timer 1.5 action Return(False)


# ============================================================
#  ЭКРАН МИНИ-ИГРЫ 2: ДОПРОС ЗА ЗАКРЫТОЙ ДВЕРЬЮ
# ============================================================

screen minigame_interrogation():
    modal True
    zorder 100
    predict False

    default state = InterrogationState()

    add Solid(TERM_BG)

    hbox:
        xfill True
        yfill True

        # === ЛЕВАЯ ПАНЕЛЬ: Елена ===
        frame:
            xsize 700
            yfill True
            background "#0d1117"
            padding (40, 40, 40, 40)

            vbox:
                spacing 18

                text "[[ ЕЛЕНА ]]" style "mg_title_text" size 36

                null height 5

                # Пульс
                hbox:
                    spacing 10
                    text "ПУЛЬС:" style "mg_label_text" yalign 0.5
                    if state.pulse < 90:
                        text "[state.pulse] bpm" size 30 color TERM_GREEN font "DejaVuSans.ttf" yalign 0.5
                    elif state.pulse < 120:
                        text "[state.pulse] bpm" size 30 color TERM_AMBER font "DejaVuSans.ttf" yalign 0.5
                    else:
                        text "[state.pulse] bpm" size 30 color TERM_RED font "DejaVuSans.ttf" yalign 0.5

                # Тревога — бар
                vbox:
                    spacing 5
                    text "ТРЕВОГА:" style "mg_label_text"
                    hbox:
                        spacing 10
                        frame:
                            xysize (450, 24)
                            background "#1a1a2e"
                            frame:
                                xalign 0.0
                                yalign 0.5
                                xsize int(450 * state.anxiety / 100)
                                ysize 24
                                if state.anxiety < 40:
                                    background TERM_GREEN
                                elif state.anxiety < 70:
                                    background TERM_AMBER
                                else:
                                    background TERM_RED
                        if state.anxiety < 40:
                            text "[state.anxiety]%%" size 24 color TERM_GREEN font "DejaVuSans.ttf" yalign 0.5
                        elif state.anxiety < 70:
                            text "[state.anxiety]%%" size 24 color TERM_AMBER font "DejaVuSans.ttf" yalign 0.5
                        else:
                            text "[state.anxiety]%%" size 24 color TERM_RED font "DejaVuSans.ttf" yalign 0.5

                null height 15

                # Портрет Елены (заглушка)
                frame:
                    xysize (280, 350)
                    xalign 0.5
                    background "#1a1a2e"
                    text "[[ ЕЛЕНА ]]":
                        xalign 0.5
                        yalign 0.5
                        color "#c8a8d8"
                        size 28
                        font "DejaVuSans.ttf"

                null height 10

                # Последний ответ Елены
                if state.last_response:
                    frame:
                        background "#0a1a0a"
                        padding (15, 10, 15, 10)
                        xfill True
                        text state.last_response:
                            color "#c8a8d8"
                            size 20
                            font "DejaVuSans.ttf"

        # === ПРАВАЯ ПАНЕЛЬ: Тактики ===
        frame:
            xsize 1220
            yfill True
            background TERM_BG
            padding (40, 40, 40, 40)

            vbox:
                spacing 15

                if state.turn <= state.max_turns:
                    $ cur_turn = state.turn
                    text "[[ ДОПРОС — Ход [cur_turn]/[state.max_turns] ]]" style "mg_title_text" size 36
                else:
                    text "[[ ДОПРОС — ЗАВЕРШЁН ]]" style "mg_title_text" size 36

                null height 15

                if not state.is_finished():
                    text "Выберите тактику:" style "mg_label_text"
                    null height 10

                    vbox:
                        spacing 12

                        textbutton "[[ ДАВЛЕНИЕ ]] — Агрессивно надавить":
                            style "mg_button"
                            text_style "mg_button_text"
                            text_size 22
                            xfill True
                            action Function(state.apply_tactic, "pressure")

                        textbutton "[[ ЭМПАТИЯ ]] — Проявить сочувствие":
                            style "mg_button"
                            text_style "mg_button_text"
                            text_size 22
                            xfill True
                            action Function(state.apply_tactic, "empathy")

                        textbutton "[[ БЛЕФ ]] — Сделать вид, что знаешь больше":
                            style "mg_button"
                            text_style "mg_button_text"
                            text_size 22
                            xfill True
                            action Function(state.apply_tactic, "bluff")

                        textbutton "[[ РАСКРЫТЬ КАРТЫ ]] — Предъявить улику":
                            style "mg_button"
                            text_style "mg_button_text"
                            text_size 22
                            xfill True
                            action Function(state.apply_tactic, "reveal")

                elif state.failed:
                    text ">> ТРЕВОГА КРИТИЧЕСКАЯ <<" style "mg_title_text" color TERM_RED
                    null height 10
                    text "Елена впала в истерику. Допрос провален." style "mg_body_text" color TERM_RED
                    timer 2.0 action Return(False)

                elif state.is_success():
                    text ">> ДОПРОС УСПЕШЕН <<" style "mg_title_text" color TERM_CYAN
                    null height 10
                    $ final_anx = state.anxiety
                    text "Елена раскололась. Уровень тревоги: [final_anx]%%." style "mg_body_text" color TERM_CYAN
                    timer 2.0 action Return(True)

                else:
                    # Закончились ходы, но тревога >= 50
                    text ">> ЕЛЕНА НЕ РАСКРЫЛАСЬ <<" style "mg_title_text" color TERM_AMBER
                    null height 10
                    $ final_anx = state.anxiety
                    text "Тревога слишком высокая ([final_anx]%%). Елена не доверяет вам." style "mg_body_text" color TERM_AMBER
                    timer 2.0 action Return(False)


# ============================================================
#  ЭКРАН МИНИ-ИГРЫ 3: РАСПРЕДЕЛЕНИЕ ВОЗДУХА
# ============================================================

screen minigame_air():
    modal True
    zorder 100
    predict False

    default air = AirDistribution()
    default selected_from = None
    default amount = 5
    default confirmed = False

    add Solid(TERM_BG)

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15

        text "[[ РАСПРЕДЕЛЕНИЕ ВОЗДУХА ]]" style "mg_title_text"

        # Инфо
        hbox:
            xalign 0.5
            spacing 30
            text "Ходы: [air.moves_left]/5" style "mg_label_text"
            $ total_o2 = sum(air.levels)
            text "Общий O2: [total_o2] ед." style "mg_label_text"

        null height 5

        # 4 сектора
        hbox:
            xalign 0.5
            spacing 20

            for i in range(4):
                $ s_name, s_person, s_color = air.SECTORS[i]
                $ s_level = air.levels[i]
                $ s_dcolor = air.danger_color(s_level)
                $ is_sel = (selected_from == i)
                $ f_bg = "#1a3a1a" if is_sel else "#0d1117"

                frame:
                    xysize (380, 480)
                    background f_bg
                    padding (15, 15, 15, 15)

                    vbox:
                        spacing 8
                        xfill True

                        text s_name:
                            color TERM_CYAN
                            size 22
                            font "DejaVuSans.ttf"
                            xalign 0.5

                        text s_person:
                            color s_color
                            size 20
                            font "DejaVuSans.ttf"
                            xalign 0.5

                        null height 5

                        # Вертикальная шкала
                        frame:
                            xalign 0.5
                            xysize (80, 200)
                            background "#0a0a0a"
                            # Заполнение снизу
                            $ bar_h = int(200 * min(s_level, 30) / 30.0)
                            frame:
                                xfill True
                                ysize bar_h
                                yalign 1.0
                                background s_dcolor

                        text "[s_level] ед.":
                            color s_dcolor
                            size 28
                            font "DejaVuSans.ttf"
                            xalign 0.5

                        null height 5

                        # Кнопки
                        if not confirmed and air.moves_left > 0:
                            if selected_from is None:
                                textbutton "ОТКАЧАТЬ":
                                    xalign 0.5
                                    style "mg_button"
                                    text_style "mg_button_text"
                                    text_size 18
                                    sensitive (s_level > 0)
                                    action SetScreenVariable("selected_from", i)
                            elif selected_from == i:
                                textbutton "ОТМЕНА":
                                    xalign 0.5
                                    style "mg_button"
                                    text_style "mg_button_text"
                                    text_size 18
                                    action SetScreenVariable("selected_from", None)
                            else:
                                textbutton "ЗАКАЧАТЬ":
                                    xalign 0.5
                                    style "mg_button"
                                    text_style "mg_button_text"
                                    text_size 18
                                    sensitive air.can_transfer(selected_from, i, amount)
                                    action [
                                        Function(air.transfer, selected_from, i, amount),
                                        SetScreenVariable("selected_from", None),
                                    ]

                        # Статус безопасности
                        if s_level >= 10:
                            text "НОРМА" color TERM_GREEN size 16 font "DejaVuSans.ttf" xalign 0.5
                        elif s_level >= 5:
                            text "ОПАСНО" color TERM_AMBER size 16 font "DejaVuSans.ttf" xalign 0.5
                        else:
                            text "КРИТ." color TERM_RED size 16 font "DejaVuSans.ttf" xalign 0.5

        null height 10

        # Переключатель объёма
        hbox:
            xalign 0.5
            spacing 20
            text "Объём перекачки:" style "mg_label_text" yalign 0.5
            textbutton "5 ед.":
                style "mg_button"
                text_style "mg_button_text"
                text_size 22
                action SetScreenVariable("amount", 5)
                if amount == 5:
                    background "#2a5a2a"
            textbutton "10 ед.":
                style "mg_button"
                text_style "mg_button_text"
                text_size 22
                action SetScreenVariable("amount", 10)
                if amount == 10:
                    background "#2a5a2a"

        null height 15

        # Автоматический результат при 0 ходов или идеальном балансе
        if air.moves_left <= 0 and not confirmed:
            $ auto_result = air.get_result()
            if auto_result == 1:
                text ">> ВСЕ СЕКТОРЫ СТАБИЛИЗИРОВАНЫ <<" style "mg_title_text" color TERM_CYAN
            elif auto_result == 2:
                text ">> БАЛАНС НЕ ИДЕАЛЕН — КТО-ТО ПОСТРАДАЕТ <<" style "mg_title_text" color TERM_AMBER
            else:
                text ">> КРИТИЧЕСКИЙ СБОЙ РАСПРЕДЕЛЕНИЯ <<" style "mg_title_text" color TERM_RED
            timer 2.0 action Return(auto_result)

        elif air.is_ideal() and not confirmed:
            text ">> ВСЕ СЕКТОРЫ СТАБИЛИЗИРОВАНЫ <<" style "mg_title_text" color TERM_CYAN
            timer 2.0 action Return(1)

        elif not confirmed and air.moves_left > 0:
            # Кнопка подтверждения
            textbutton "[[ ПОДТВЕРДИТЬ РАСПРЕДЕЛЕНИЕ ]]":
                xalign 0.5
                style "mg_button"
                text_style "mg_button_text"
                action Return(air.get_result())


# ============================================================
#  ЭКРАН МИНИ-ИГРЫ 4: ОБЫСК В ТЕМНОТЕ
# ============================================================

screen minigame_search():
    modal True
    zorder 100
    predict False

    default game = SearchGameState()
    default time_left = 60
    default timed_out = False

    # --- Фон: тёмная комната ---
    add Solid("#050508")

    # --- Мышь ---
    $ mx, my = renpy.get_mouse_pos()

    # --- Проверка ловушек ---
    $ game.check_traps(mx, my)

    # --- Таймер и пассивная детекция ---
    if game.result is None and not timed_out:
        timer 1.0 repeat True action [
            If(time_left > 0,
                true=SetScreenVariable("time_left", time_left - 1),
                false=SetScreenVariable("timed_out", True)),
            Function(game.tick_detection),
        ]

    # --- Тайм-аут ---
    if timed_out and game.result is None:
        if game.found_count() >= 3:
            $ game.result = True
        else:
            $ game.result = False

    # --- Обновление экрана для отслеживания мыши ---
    timer 0.1 repeat True action Function(renpy.restart_interaction)

    # --- Элементы комнаты (подсказки окружения) ---
    # Кровать/матрас
    frame:
        pos (250, 600)
        xysize (200, 160)
        background "#0a0f0a"
        text "кровать" color "#0a200a" size 14 font "DejaVuSans.ttf" xalign 0.5 yalign 0.5

    # Куртка на стене
    frame:
        pos (1350, 240)
        xysize (180, 200)
        background "#0a0f0a"
        text "куртка" color "#0a200a" size 14 font "DejaVuSans.ttf" xalign 0.5 yalign 0.5

    # Вентиляционная решётка
    frame:
        pos (960, 710)
        xysize (180, 140)
        background "#0a0f0a"
        text "вент. решётка" color "#0a200a" size 12 font "DejaVuSans.ttf" xalign 0.5 yalign 0.5

    # --- Предметы для поиска (кнопки) ---
    for idx in range(3):
        $ item = game.ITEMS[idx]
        $ ix = item["x"]
        $ iy = item["y"]
        $ ir = item["r"]
        $ item_found = game.items_found[idx]
        $ item_visible = game.in_light(ix, iy, mx, my)

        if not item_found:
            button:
                pos (ix - ir, iy - ir)
                xysize (ir * 2, ir * 2)
                background "#00ff4130"
                hover_background "#00ff4160"
                action Function(game.collect_item, idx)
                sensitive item_visible
                if not item_visible:
                    background "#00000000"
                text item["name"]:
                    size 16
                    color TERM_GREEN
                    font "DejaVuSans.ttf"
                    xalign 0.5
                    yalign 0.5
                    if not item_visible:
                        color "#00000000"
        else:
            frame:
                pos (ix - ir, iy - ir)
                xysize (ir * 2, ir * 2)
                background "#00ff4115"
                text "OK":
                    size 32
                    color "#00ff4180"
                    font "DejaVuSans.ttf"
                    xalign 0.5
                    yalign 0.5

    # --- Ловушки (визуальные маркеры) ---
    for tidx in range(2):
        $ trap = game.TRAPS[tidx]
        $ trap_vis = game.in_light(trap["x"], trap["y"], mx, my)
        $ trap_trig = game.traps_triggered[tidx]
        if trap_vis and not trap_trig:
            frame:
                pos (trap["x"] - 20, trap["y"] - 20)
                xysize (40, 40)
                background "#ff170020"

    # --- Тёмная маска с отверстием фонарика ---
    # 4 тёмных прямоугольника вокруг квадрата
    $ lr = _FL_RADIUS
    $ lx0 = max(0, mx - lr)
    $ ly0 = max(0, my - lr)
    $ lx1 = min(1920, mx + lr)
    $ ly1 = min(1080, my + lr)

    # Верхняя полоса
    if ly0 > 0:
        add Solid("#000000dc"):
            pos (0, 0)
            xysize (1920, ly0)

    # Нижняя полоса
    if ly1 < 1080:
        add Solid("#000000dc"):
            pos (0, ly1)
            xysize (1920, 1080 - ly1)

    # Левая полоса (между верхней и нижней)
    if lx0 > 0:
        add Solid("#000000dc"):
            pos (0, ly0)
            xysize (lx0, ly1 - ly0)

    # Правая полоса
    if lx1 < 1920:
        add Solid("#000000dc"):
            pos (lx1, ly0)
            xysize (1920 - lx1, ly1 - ly0)

    # Круговой градиент внутри квадрата
    if _os.path.exists(_FL_IMG_PATH):
        add Image(_FL_IMG_PATH):
            pos (mx - lr, my - lr)

    # --- HUD (поверх всего) ---
    frame:
        xalign 0.5
        yalign 0.0
        yoffset 15
        background "#0a0e14b0"
        padding (30, 10, 30, 10)

        hbox:
            spacing 40

            # Таймер
            hbox:
                spacing 8
                text "ВРЕМЯ:" style "mg_label_text" size 22 yalign 0.5
                if time_left > 15:
                    text "[time_left]с" size 26 font "DejaVuSans.ttf" color TERM_GREEN yalign 0.5
                else:
                    text "[time_left]с" size 26 font "DejaVuSans.ttf" color TERM_RED yalign 0.5

            # Детекция
            hbox:
                spacing 8
                text "РИСК:" style "mg_label_text" size 22 yalign 0.5
                $ det_int = int(game.detection)
                frame:
                    xysize (180, 18)
                    background "#1a1a2e"
                    yalign 0.5
                    frame:
                        xalign 0.0
                        yalign 0.5
                        xsize int(180 * min(game.detection, 100) / 100.0)
                        ysize 18
                        background TERM_RED
                text "[det_int]%%" size 22 font "DejaVuSans.ttf" color TERM_RED yalign 0.5

            # Найдено предметов
            $ fc = game.found_count()
            text "Найдено: [fc]/3" style "mg_label_text" size 22 yalign 0.5

    # --- Экраны результата ---
    if game.result is True:
        frame:
            xalign 0.5
            yalign 0.5
            background "#0a0e14e0"
            padding (60, 30, 60, 30)
            vbox:
                spacing 10
                text ">> УЛИКИ СОБРАНЫ <<" style "mg_title_text" color TERM_CYAN
                text "Вы покинули комнату незамеченным." style "mg_body_text" xalign 0.5
        timer 2.0 action Return(True)

    if game.result is False:
        frame:
            xalign 0.5
            yalign 0.5
            background "#0a0e14e0"
            padding (60, 30, 60, 30)
            vbox:
                spacing 10
                text ">> ОБНАРУЖЕН <<" style "mg_title_text" color TERM_RED
                text "Виктор входит в комнату..." style "mg_body_text" color TERM_RED xalign 0.5
        timer 2.0 action Return(False)
