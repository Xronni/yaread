# 📚 YaRead — AI-Powered PDF Reader

<p align="center">
  <img src="assets/icon.png" width="128" height="128" alt="YaRead Logo">
</p>

<p align="center">
  <strong>YaRead</strong> is an intelligent desktop reader that automatically analyzes narrative emotional changes using artificial intelligence and synchronizes playback of corresponding multi-channel background audio loops.
</p>

<p align="center">
  <img src="assets/demo.gif" alt="YaRead Demo" width="700">
</p>

<p align="center">
  <a href="https://boosty.to/xronni/single-payment/donation/809763/target?share=target_link"><img src="https://img.shields.io/badge/Boosty-Support%20Project-orange?style=flat&logo=boosty" alt="Support on Boosty"></a>
  <a href="https://github.com/Xronni/yaread/releases/latest"><img src="https://img.shields.io/github/v/release/Xronni/yaread?color=blue&label=Latest%20Release" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-FCC624?style=flat&logo=linux&logoColor=black" alt="Platform: Linux | Windows">
  <img src="https://img.shields.io/badge/Qt-6-41CD52?logo=qt&logoColor=white" alt="Qt 6">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-green" alt="License: MIT"></a>
</p>

---

## 🌐 Navigation / Навигация
* 🇺🇸 [English Version](#-english-version)
* 🇷🇺 [Русская версия](#-русская-версия)

---

## 🇺🇸 English Version

### ✨ Key Features
* 🧠 **Dual AI Engine:** Use cloud providers (OpenAI, Gemini, DeepSeek, OpenRouter) or run locally and completely private offline using `.gguf` models.
* 🎵 **Adaptive Soundtracks:** Automatically detects 12 narrative emotions in the text and dynamically crossfades between custom background music tracks.
* 📖 **Universal Format Support:** Read PDF, EPUB, and FB2 files seamlessly.
* 🎨 **Atmospheric Themes:** Choose between Light, Dark, Sepia, or animated Starry Night.
* 🐧 **Native Linux Integration:** Distributed as a Debian/Ubuntu `.deb` package with desktop integration, MIME handlers, and high-DPI icons.

---

### 📥 1. Installation & Requirements

#### Prerequisites:
* **Operating System:** Linux (Ubuntu 22.04+, Debian 12+, Arch Linux, Fedora) or Windows 10/11
* **Python:** 3.10 or newer

#### System Packages (Ubuntu / Debian):
```bash
sudo apt update && sudo apt install -y python3 python3-pyqt6 python3-pygame python3-fitz python3-bs4 python3-lxml python3-ebooklib
```

#### Option A: Install Debian / Ubuntu Package (.deb) — Recommended
Download `yaread_1.0.0_all.deb` from the **[Releases](https://github.com/Xronni/yaread/releases/latest)** section and install:
```bash
sudo dpkg -i yaread_1.0.0_all.deb
sudo apt install -f  # automatically install dependencies if needed
```
Launch `YaRead` from your application launcher or type `yaread` in the terminal.

#### Option B: Standalone Portable Linux Archive or Git Clone
1. Download `yaread-v1.0.0-linux-x86_64.tar.gz` from **[Releases](https://github.com/Xronni/yaread/releases/latest)** (or clone the repository):
   ```bash
   tar -xzf yaread-v1.0.0-linux-x86_64.tar.gz
   cd yaread-1.0.0
   ```
2. Run the application:
   ```bash
   ./run.sh
   ```
3. *(Optional)* Install desktop shortcut and icon to your application menu:
   ```bash
   ./install.sh
   ```

> [!TIP]
> Running `./install.sh` registers YaRead in your GNOME/KDE applications menu and dashboard.

#### Option C: Windows Standalone
1. Download `YaRead_1.0.0.zip` from **[Releases](https://github.com/Xronni/yaread/releases/latest)**.
2. Extract the ZIP archive completely into a separate folder.
3. Launch `yaread.exe`.

> [!WARNING]  
> **Important:** Do not move `yaread.exe` out of its folder. It must remain in the same directory as the `data` folder. To create a desktop shortcut, right-click `yaread.exe` → **Send to** → **Desktop (create shortcut)**.

---

### ⚙️ 2. Setup & AI Configuration

Launch YaRead and configure your preferred AI engine on the top panel:

*   **Online Mode (Quick start):** Choose your provider (OpenAI, Gemini, DeepSeek, or OpenRouter) and paste your personal API key.  
    _Note: This mode consumes your official API credits from the respective provider._
*   **Offline Mode (Private & Local):** Select **Local .GGUF**.
    1. Download the recommended model: `qwen2.5-7b-instruct-q4_k_m.gguf` from [Hugging Face](https://huggingface.co/paultimothymooney/Qwen2.5-7B-Instruct-Q4_K_M-GGUF/tree/main).
    2. Model storage location:
       * **Deb package / Linux user:** Place the downloaded `.gguf` file in `~/.local/share/yaread/models/` or `~/models/`.
       * **Portable / Git:** Place it in the `models/` directory inside the application folder.
       * *Or enter the full absolute path to the `.gguf` file directly in the AI model field.*
    3. Click **Open File** (or drag & drop your book) and click **Start**.

---

### ⌨️ 3. Controls & Hotkeys

| Hotkey | Action |
|:---:|---|
| **Spacebar** | Play / Pause (Starts / stops auto-scrolling and background music) |
| **Ctrl + F** | Open quick text search bar |
| **Escape** | Close search bar / clear active selections |
| **Alt + Mouse Drag** | Highlight a text fragment and click **"Ask AI"** for an instant explanation |
| **Arrow Up / Down** | Manual text scrolling |
| **PageUp / PageDown** | Page-by-page scrolling |

---

### 🎵 4. Soundtrack Emotions

YaRead dynamically adjusts background audio loops based on 12 narrative emotions:

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

### 🛡️ 5. Security & Community
* [Security Policy](SECURITY.md)
* [Contributing Guidelines](CONTRIBUTING.md)
* [Code of Conduct](CODE_OF_CONDUCT.md)
* Verify release checksums using `SHA256SUMS.txt` available on the [Releases](https://github.com/Xronni/yaread/releases) page.

---

## 🇷🇺 Русская версия

### ✨ Основные возможности
* 🧠 **Двойной движок ИИ:** Работайте через облачные API (OpenAI, Gemini, DeepSeek, OpenRouter) или полностью локально и приватно без интернета с помощью `.gguf` моделей.
* 🎵 **Адаптивные саундтреки:** ИИ определяет 12 эмоций в тексте и плавно переключает фоновую музыку под настроение читаемого фрагмента.
* 📖 **Универсальность:** Поддержка форматов PDF, EPUB и FB2.
* 🎨 **Атмосферные темы:** Сепия, Темная, Светлая и анимированная Звёздная Ночь.
* 🐧 **Нативная поддержка Linux:** Установочный `.deb` пакет для Debian/Ubuntu, интеграция в меню приложений и поддержка ярлыков рабочего стола.

---

### 📥 1. Установка и запуск

#### Системные требования:
* **ОС:** Linux (Ubuntu 22.04+, Debian 12+, Arch Linux, Fedora) или Windows 10/11
* **Python:** 3.10 или выше

#### Установка зависимостей (Ubuntu / Debian):
```bash
sudo apt update && sudo apt install -y python3 python3-pyqt6 python3-pygame python3-fitz python3-bs4 python3-lxml python3-ebooklib
```

#### Вариант А: Установка пакета Debian / Ubuntu (.deb) — Рекомендуется
Скачайте `yaread_1.0.0_all.deb` со страницы **[Релизов](https://github.com/Xronni/yaread/releases/latest)** и выполните:
```bash
sudo dpkg -i yaread_1.0.0_all.deb
sudo apt install -f  # автоматическая установка зависимостей при необходимости
```
После установки приложение появится в меню вашей системы или запустится командой `yaread`.

#### Вариант Б: Портативный запуск для Linux или сборка из Git
1. Скачайте архив `yaread-v1.0.0-linux-x86_64.tar.gz` со страницы **[Релизов](https://github.com/Xronni/yaread/releases/latest)** (или клонируйте репозиторий):
   ```bash
   tar -xzf yaread-v1.0.0-linux-x86_64.tar.gz
   cd yaread-1.0.0
   ```
2. Запустите читалку:
   ```bash
   ./run.sh
   ```
3. *(Опционально)* Добавьте ярлык в системное меню приложений GNOME / KDE:
   ```bash
   ./install.sh
   ```

> [!TIP]
> Скрипт `./install.sh` регистрирует YaRead в меню приложений GNOME/KDE и панели задач.

#### Вариант В: Windows (Портативный архив)
1. Скачайте `YaRead_1.0.0.zip` со страницы **[Релизов](https://github.com/Xronni/yaread/releases/latest)**.
2. Распакуйте архив в отдельную папку.
3. Запустите `yaread.exe`.

> [!WARNING]  
> **Важно:** Не перемещайте файл `yaread.exe` отдельно от папки `data`. Они должны находиться в одной директории, иначе программа закроется с ошибкой. Для удобства нажмите правой кнопкой мыши по `yaread.exe` → **Отправить** → **Рабочий стол (создать ярлык)**.

---

### ⚙️ 2. Использование и настройка ИИ

Запустите программу и выберите режим работы ИИ на верхней панели:

*   **Онлайн-режим (Быстрый старт):** Выберите провайдера (OpenAI, Gemini, DeepSeek или OpenRouter) и вставьте свой API-ключ.  
    _Примечание: Запросы расходуют баланс вашего личного аккаунта выбранного ИИ-сервиса._
*   **Автономный режим (Локальный):** Выберите **Local .GGUF**.
    1. Загрузите рекомендуемую модель `qwen2.5-7b-instruct-q4_k_m.gguf` с [Hugging Face](https://huggingface.co/paultimothymooney/Qwen2.5-7B-Instruct-Q4_K_M-GGUF/tree/main).
    2. Куда поместить файл модели:
       * **При установке через .deb на Linux:** Поместите `.gguf` файл в `~/.local/share/yaread/models/` или `~/models/`.
       * **При портативном запуске:** В папку `models/` внутри каталога программы.
       * *Либо укажите полный абсолютный путь к файлу модели в строке настроек ИИ.*
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

## 🤝 Поддержка проекта / Support
Если вам нравится YaRead, вы можете поддержать разработку:
* 🍊 **[Boosty (Support YaRead)](https://boosty.to/xronni/single-payment/donation/809763/target?share=target_link)**

---

## 📄 Лицензия / License
Проект распространяется под лицензией [MIT License](LICENSE.md).
