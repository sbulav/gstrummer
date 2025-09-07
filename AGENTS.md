# AGENTS.md — Оркестрация разработки через opencode

Этот документ описывает роли «агентов», правила работы и готовые промпты для использования инструмента **opencode** при разработке настольного Python‑приложения обучения гитарным боям (PySide6, sounddevice, numpy, librosa). Документ служит единым источником правды для планирования, декомпозиции задач, кодогенерации и ревью.

---

## 0) TL;DR

* **Главная цель:** настольное кроссплатформенное приложение с визуализацией боя, метрономом, пресетами рисунков, режимами Practice/Quiz/Song, базовой оценкой точности по микрофону.
* **Стек:** Python 3.11+, PySide6, sounddevice, numpy, librosa, PyYAML, pytest, pyinstaller.
* **Архитектура каталога:** `app/core`, `app/ui`, `app/data`, `app/utils`, `tests`, `assets`.
* **Стиль кода:** PEP8 + type hints + `ruff`/`black`.
* **Данные:** YAML‑пресеты `patterns.yaml`, `songs.yaml`, `lessons.yaml`.
* **Сборка:** `pyinstaller`; Dev‑команды через `make`.
* **Покрытие тестами:** критический core (метроном, планировщик шагов, парсер YAML, оценщик онсетов).

---

## 1) Роли агентов

Каждая роль — это точка зрения/ответственность. В opencode используйте соответствующие промпты.

### 1.1 Архитектор (ARCH)

**Цель:** зафиксировать интерфейсы модулей, зависимости, границы ответственности.
**Зоны ответственности:** схемы данных, публичные API модулей, жизненный цикл, события.
**Приёмка:** диаграмма модулей, скелеты интерфейсов + докстринги, без бизнес‑логики.

### 1.2 Аудио‑движок (AUDIO)

**Цель:** надёжный метроном и воспроизведение сэмплов (клик, скретч), микс громкостей.
**Модули:** `core/metronome.py`, `core/audio_engine.py`, `core/scheduler.py`.
**Приёмка:** стабильный дрейф < 1ms/мин в тесте; API событий «tick(idx, ts)»; заглушки сэмплов.

### 1.3 Паттерны/данные (DATA)

**Цель:** парсинг и валидация YAML‑пресетов, модель `StrumPattern`, `Song`.
**Модули:** `core/patterns.py`, `utils/io.py`.
**Приёмка:** схемная валидация, понятные ошибки, тесты на примерах.

### 1.4 Оценка исполнения (EVAL)

**Цель:** онсет‑детекция, квантизация к шагам, метрики точности/лаг/стабильность.
**Модули:** `core/evaluator.py`, `utils/latency.py`.
**Приёмка:** офлайн‑тест на синтетических данных; интерфейс «analyze(audio)->Report».

### 1.5 Визуализация/GUI (UI)

**Цель:** PySide6‑интерфейс, таймлайн со стрелками D/U, акценты, индикаторы попаданий.
**Модули:** `ui/main_window.py`, `ui/practice_view.py`, `ui/quiz_view.py`, `ui/song_view.py`, `ui/components/*`.
**Приёмка:** 60fps анимации на таймлайне из таймеров Qt; горячие клавиши; доступность.

### 1.6 UX‑наставник (UX)

**Цель:** микро‑копирайтинг, подсказки, туториал, режим «минимум информации».
**Артефакты:** строки локализации, подсказки, чек‑листы занятий.

### 1.7 QA‑инженер (QA)

**Цель:** сценарные тесты, smoke‑чек‑листы, репорты перфоманса/латентности.

### 1.8 Сборка/релиз (DEVOPS)

**Цель:** Makefile, запуск/линт/тесты, PyInstaller‑спеки, артефакты релиза.

---

## 2) Структура репозитория

```
app/
  core/
    patterns.py
    metronome.py
    audio_engine.py
    evaluator.py
    scheduler.py
  ui/
    main_window.py
    practice_view.py
    quiz_view.py
    song_view.py
    components/
      timeline.py
      transport.py
  data/
    patterns.yaml
    songs.yaml
    lessons.yaml
    samples/
      click_high.wav
      click_low.wav
      strum_down.wav
      strum_up.wav
  utils/
    io.py
    latency.py
assets/
  icons/
  fonts/
Makefile
pyproject.toml
README.md
AGENTS.md
tests/
  test_metronome.py
  test_patterns.py
  test_scheduler.py
  test_evaluator.py
```

---

## 3) Форматы данных (YAML)

### 3.1 patterns.yaml

```yaml
- id: rock_8
  name: "Рок-восьмушки (акц. 2 и 4)"
  time_sig: [4,4]
  steps_per_bar: 8
  bpm_default: 92
  bpm_min: 60
  bpm_max: 140
  notes: "Чередование D/U, акценты на 2 и 4"
  steps:
    - {t: 0.0,   dir: D, accent: 0.7}
    - {t: 0.125, dir: U}
    - {t: 0.25,  dir: D, accent: 1.0}
    - {t: 0.375, dir: U}
    - {t: 0.5,   dir: D, accent: 0.7}
    - {t: 0.625, dir: U}
    - {t: 0.75,  dir: D, accent: 1.0}
    - {t: 0.875, dir: U}
- id: ddu_udu
  name: "DDU UDU (баллада)"
  time_sig: [4,4]
  steps_per_bar: 8
  bpm_default: 84
  bpm_min: 56
  bpm_max: 120
  notes: "Популярный балладный рисунок"
  steps:
    - {t: 0.0,   dir: D, accent: 0.8}
    - {t: 0.125, dir: -}
    - {t: 0.25,  dir: D}
    - {t: 0.375, dir: U}
    - {t: 0.5,   dir: -}
    - {t: 0.625, dir: U}
    - {t: 0.75,  dir: D}
    - {t: 0.875, dir: U}
```

### 3.2 songs.yaml (примеры)

```yaml
- title: "Группа крови"
  artist: "Кино"
  bpm: 92
  time_sig: [4,4]
  pattern_id: "rock_8"
  progression: ["Am", "F", "G", "C"]
  notes: "Играть плотными восьмушками, акценты 2/4"
- title: "Кукушка"
  artist: "Кино"
  bpm: 78
  time_sig: [4,4]
  pattern_id: "ddu_udu"
  progression: ["Am", "G", "Em", "Am"]
  notes: "Балладный вариант; возможны вариации"
```

---

## 4) Рабочий процесс с opencode

Опорная идея: каждая итерация проходит стадии **Plan → Implement → Review → Test → Integrate**.

### 4.1 Макро‑промпт для планирования (ARCH/PM)

```
opencode plan:
Цель: Реализовать модуль {MODULE} в соответствии с AGENTS.md.
Шаги:
1) Уточнить публичный API, входы/выходы, исключения.
2) Нарисовать краткую диаграмму зависимостей (ASCII) и список событий/колбеков.
3) Сгенерировать скелет файлов с докстрингами и type hints.
4) Добавить задачи тестирования (pytest) + примеры фикстур.
Критерии готовности: описаны ниже в разделе DoD для {MODULE}.
```

### 4.2 Макро‑промпт для имплементации (OWNER‑модуля)

```
opencode implement:
Контекст: Реализуем {FILEPATHS} по API из раздела 1 и схемам данных.
Требования:
- PEP8, type hints, докстринги в стиле Google.
- Никаких глобальных синглтонов.
- Логгер через `logging.getLogger(__name__)`.
- Исключения: ValueError/RuntimeError с понятными сообщениями.
- Кроссплатформенность (Windows/macOS/Linux).
- Без блокирующих `sleep` в GUI‑потоке; аудио — отдельный поток.
Выход: рабочий код + минимальные тесты.
```

### 4.3 Промпт для UI‑слоя (UI)

```
opencode implement-ui:
Задача: Реализовать PySide6‑виджет {WidgetName}.
Требования:
- Отрисовка таймлайна 8/16 шагов, стрелки D/U, акценты (толщина/яркость).
- Анимация попадания шага (scale + flash) 100–150 мс.
- События: onPlay, onPause, onTempoChange.
- Горячие клавиши: Space (Play/Pause), +/- (BPM), S (Swing toggle).
- Без блокирующих операций; использовать QTimer/Signals.
```

### 4.4 Промпт для аудио‑движка (AUDIO)

```
opencode implement-audio:
Модули: core/metronome.py, core/audio_engine.py, core/scheduler.py
Требования:
- Метроном с расчётом t_step = 60/bpm/steps_per_beat, событие `on_tick(ts, idx)`.
- Планировщик: сопоставление индекса тика с Step.t и выдача «play(strum)».
- Аудио: sounddevice с буферизацией, предзагрузка WAV из data/samples.
- Микс: независимые громкости click/strum, «высокий» клик на «1» доле.
- Тест стабильности: 60 сек, дрейф < 1ms/мин.
```

### 4.5 Промпт для оценщика (EVAL)

```
opencode implement-eval:
Модули: core/evaluator.py, utils/latency.py
Требования:
- Калибровка задержки: усреднение N онсетов хлопков под клик.
- Onset‑детекция: librosa.onset.onset_detect + параметры окна.
- Квантизация к ближайшему Step; отчёт: попадание/раньше/позже, средний лаг.
- Юнит‑тест на синтетических кликах с контролируемым джиттером.
```

### 4.6 Промпт для DevOps/релиза (DEVOPS)

```
opencode implement-devops:
Добавить Makefile и pyproject.toml с зависимостями.
Команды make: venv, install, lint, test, run, build.
PyInstaller: spec для однофайлового билда, иконка из assets/icons.
```

### 4.7 Промпт для QA

```
opencode qa:
Сгенерировать smoke‑чек‑лист: запуск, выбор паттерна, старт/пауза, изменение BPM, визуальная синхронизация, звук клика, экспорт логов.
Создать pytest сценарии для регрессии метронома и парсера YAML.
```

---

## 5) Definition of Done (DoD) по модулям

* **core/metronome.py:** точность тайминга подтверждена тестом; API `on_tick(cb)`; поток безопасно останавливается; докстринги.
* **core/scheduler.py:** верная индексация шагов в 8/16 сетке; юнит‑тесты на границы такта.
* **core/audio\_engine.py:** воспроизведение клика/скретча без xruns; независимые громкости; graceful shutdown.
* **core/patterns.py & utils/io.py:** загрузка YAML с валидацией; ошибки с указанием ключа/строки; 95% покрытие тестами.
* **core/evaluator.py:** отчёт с метриками; тесты на синтетике.
* **ui/**: не падает при отсутствии микрофона/аудио; 60fps при пустом аудио.
* **Makefile/pyproject:** `make run` запускает приложение из чистой среды.

---

## 6) Код‑стайл и инструменты

* `ruff` (линтер), `black` (формат), `mypy` (типизация, optional `--strict` для core).
* Логи: стандартный `logging` с уровнем из переменной окружения.
* Обработка ошибок: пользовательские сообщения в UI, подробности в лог.

---

## 7) Команды Makefile (целевые)

```
make venv       # создать .venv
make install    # установить зависимости
make lint       # ruff + black --check
make fmt        # black
make typecheck  # mypy
make test       # pytest -q
make run        # запуск приложения
make build      # PyInstaller onefile
```

---

## 8) Как запустить локально (dev)

1. Установить Python 3.11+ и порт‑аудио зависимости (sounddevice).
2. `make venv && make install`
3. `make run`

   * если нет аудио‑устройства, отключите звук в настройках приложения.

---

## 9) Бэклог первой итерации (MVP)

1. **ARCH:** зафиксировать интерфейсы core‑модулей, заскелетить файлы.
2. **DATA:** минимальные `patterns.yaml`, `songs.yaml` (из раздела 3).
3. **AUDIO:** метроном + клик high/low; громкость; play/pause.
4. **UI:** MainWindow + PracticeView с таймлайном и транспортом.
5. **DEVOPS:** Makefile, pyproject, ruff/black/mypy/pytest.
6. **QA:** тесты метронома/паттернов.

**Критерий MVP:** визуальный таймлайн + клик синхронно идут при изменении BPM; можно выбрать паттерн и запустить луп 1 такта.

---

## 10) Маршруты расширения (после MVP)

* Оценка игры по микрофону (onsets + отчёт).
* Swing/Shuffle.
* Режим Song с автопрокруткой аккордов.
* Пакет пресетов боёв 3/4, 16‑драйв, регги/офбиты.
* Экспорт/импорт пользовательских пресетов.

---

## 11) Эталонные промпты (быстрый доступ)

* **Создать скелет core:** `opencode plan -> implement (core/*)`
* **Таймлайн виджет:** `opencode implement-ui (ui/components/timeline.py)`
* **Метроном:** `opencode implement-audio (core/metronome.py)`
* **Парсер YAML:** `opencode implement (core/patterns.py utils/io.py)`
* **PyInstaller билд:** `opencode implement-devops`
* **Smoke‑тесты:** `opencode qa`

---

## 12) Лейблы задач

* `arch`, `audio`, `ui`, `data`, `eval`, `devops`, `qa`, `good-first-issue`, `help-wanted`.

---

## 13) Примечания

* Названия и формы «боёв» различаются по школам — храните альтернативы под одним `pattern_id` с вариантами.
* Помните о латентности аудио — калибровка обязательна перед EVAL.
* Визуализация должна оставаться информативной при 8/16 шагах и любых BPM.
