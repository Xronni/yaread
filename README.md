# 📚 YaRead — AI-Powered PDF Reader

<p align="center">
  <img src="icon.ico" width="128" height="128" alt="YaRead Logo">
</p>

<p align="center">
  <strong>YaRead</strong> is an intelligent desktop reader that automatically analyzes narrative emotional changes using artificial intelligence and synchronizes playback of corresponding multi-channel background audio loops.
</p>

<p align="center">
  <!-- Place your demo.gif in the project root folder and it will render below -->
  <img src="assets/demo.gif" alt="YaRead Demo" width="600">
</p>

<p align="center">
  <a href="https://boosty.to/xronni/single-payment/donation/809763/target?share=target_link"><img src="https://img.shields.io/badge/Boosty-Support%20Project-orange?style=flat&logo=boosty" alt="Support on Boosty"></a>
  <img src="https://img.shields.io/badge/License-Proprietary-red" alt="License: Proprietary EULA">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
</p>

---

## 🌐 Navigation / Навигация
* 🇺🇸 [English Version](#-english-version)
* 🇷🇺 [Русская версия](#-русская-версия)

---

## 🇺🇸 English Version

### ✨ Key Features
* 🧠 **Dual AI Engine:** Use cloud providers (OpenAI, Gemini, DeepSeek, OpenRouter) or run locally and private offline using `.gguf` models.
* 🎵 **Adaptive Soundtracks:** Automatically detects 12 emotions in the text and dynamically crossfades between custom background music tracks.
* 📖 **Universal Format Support:** Read PDF, EPUB, and FB2 files seamlessly.
* 🎨 **Atmospheric Themes:** Choose between Light, Dark, Sepia, or Starry Night.

---

### 📥 1. Installation

1. Download the latest version from the **[Releases](https://github.com/Xronni/yaread/releases)** section.
2. Extract the ZIP archive completely into a separate folder.

> [!WARNING]  
> **Important:** Do not move the `yaread.exe` file to the desktop on its own. It must remain in the same folder as the `data` directory, otherwise the program will crash. If you want a shortcut, right-click `yaread.exe` → **Send to** → **Desktop (create shortcut)**.

---

### ⚙️ 2. Setup & AI Configuration

Launch the program and configure your preferred AI engine on the top panel:

*   **Online Mode (Quick start):** Choose your provider (OpenAI, Gemini, DeepSeek, or OpenRouter) and paste your personal API key.  
    _Note: This mode consumes your official API credits from the respective provider._
*   **Offline Mode (Private & Local):** Select **Local .GGUF**.
    1. Download the recommended model: `qwen2.5-7b-instruct-q4_k_m.gguf` from [Hugging Face](https://huggingface.co/paultimothymooney/Qwen2.5-7B-Instruct-Q4_K_M-GGUF/tree/main).
    2. Place the downloaded `.gguf` file inside the `models` folder in the application's root directory.
    3. Click **Open File** (or drag & drop your book) and click **Start**.

---

### ⌨️ 3. Controls & Hotkeys

| Hotkey | Action |
|:---:|---|
| **Spacebar** | Play/Pause (Starts/stops auto-scrolling and background music) |
| **Ctrl + F** | Open quick text search bar |
| **Escape** | Close search bar / clear active selections |
| **Alt + Mouse Drag** | Highlight a text fragment and click **"Ask AI"** for an instant explanation |
| **Arrow Up / Down** | Manual text navigation |
| **PageUp / PageDown** | Manual page-by-page navigation |

---

### 🎵 4. Soundtrack Emotions

The application dynamically adjusts the audio tracks based on 12 narrative emotions:

1. 📖 Story / Narrative
2. ⏳ Tension / Suspense
3. ⚔️ Action / Climax
4. 🍃 Resolution
5. 💖 Romance
6. 🖤 Sadness
7. 🎉 Joy
8. 🔮 Mystery
9. 🏃‍♂️ Chase
10. 💀 Horror
11. 💭 Memories / Flashback
12. 🎭 Comedy

---

## 🇷🇺 Русская версия

### ✨ Основные возможности
* 🧠 **Двойной движок ИИ:** Работайте через облачные API (OpenAI, Gemini, DeepSeek, OpenRouter) или полностью локально и приватно без интернета с помощью `.gguf` моделей.
* 🎵 **Адаптивные саундтреки:** ИИ определяет 12 эмоций в тексте и плавно переключает фоновую музыку под настроение читаемого фрагмента.
* 📖 **Универсальность:** Поддержка форматов PDF, EPUB и FB2.
* 🎨 **Атмосферные темы:** Сепия, Темная, Светлая и анимированная Звёздная Ночь.

---

### 📥 1. Установка

1. Скачайте последнюю версию во вкладке **[Releases](https://github.com/Xronni/yaread/releases)**.
2. Полностью распакуйте скачанный ZIP-архив в отдельную папку.

> [!WARNING]  
> **Важно:** Не перемещайте файл `yaread.exe` отдельно от папки `data`. Они должны находиться в одной директории, иначе программа закроется с ошибкой. Для удобства нажмите правой кнопкой мыши по `yaread.exe` → **Отправить** → **Рабочий стол (создать ярлык)**.

---

### ⚙️ 2. Использование и настройка ИИ

Запустите программу и выберите режим работы ИИ на верхней панели:

*   **Онлайн-режим (Быстрый старт):** Выберите провайдера (OpenAI, Gemini, DeepSeek или OpenRouter) и вставьте свой API-ключ.  
    _Примечание: Запросы расходуют баланс вашего личного аккаунта выбранного ИИ-сервиса._
*   **Автономный режим (Локальный):** Выберите **Local .GGUF**.
    1. Загрузите модель `qwen2.5-7b-instruct-q4_k_m.gguf` с [Hugging Face](https://huggingface.co/paultimothymooney/Qwen2.5-7B-Instruct-Q4_K_M-GGUF/tree/main).
    2. Поместите файл в папку `models` в корневой директории программы.
    3. Нажмите **Открыть файл** (или перетащите книгу в окно приложения) и нажмите **Старт**.

---

### ⌨️ 3. Управление и горячие клавиши

| Горячая клавиша | Действие |
|:---:|---|
| **Пробел** | Старт / Пауза (запуск автопрокрутки и музыки) |
| **Ctrl + F** | Открыть строку быстрого поиска текста |
| **Escape** | Закрыть строку поиска / сбросить выделение |
| **Alt + Выделение мышью** | Удерживая Alt, выделите текст и нажмите **"Спросить ИИ"** для получения справки |
| **Стрелки Вверх / Вниз** | Ручная навигация по тексту |
| **PageUp / PageDown** | Прокрутка текста на экран вверх / вниз |

---

### 🎵 4. Саундтреки (Эмоции)

Фоновые композиции сменяют друг друга в зависимости от тона повествования:

1. 📖 История / Повествование
2. ⏳ Напряжение / Саспенс
3. ⚔️ Действие / Экшен
4. 🍃 Развязка
5. 💖 Романтика
6. 🖤 Грусть
7. 🎉 Радость
8. 🔮 Мистика
9. 🏃‍♂️ Погоня
10. 💀 Хоррор
11. 💭 Воспоминания / Флешбэк
12. 🎭 Комедия

---

## 🤝 Support the Project / Поддержать проект
If you like YaRead, you can support development by donating:  
Если вам нравится YaRead, вы можете поддержать разработку:

* 🍊 **[Boosty (Support YaRead)](https://boosty.to/xronni/single-payment/donation/809763/target?share=target_link)**
