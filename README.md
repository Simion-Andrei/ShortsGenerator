# ShortsGenerator (Fake Message Edition) 📱🎬

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![ElevenLabs](https://img.shields.io/badge/AI-ElevenLabs-black?style=for-the-badge)](https://elevenlabs.io/)
[![MoviePy](https://img.shields.io/badge/Render-MoviePy-yellow?style=for-the-badge)](https://zulko.github.io/moviepy/)

**ShortsGenerator** is an automated content creation tool that generates viral "fake text message" videos (commonly seen on TikTok, Reels, and YouTube Shorts). It takes a script file, generates realistic AI voiceovers, builds a visual conversation UI, and overlays it on top of background gameplay footage.

## ✨ Features

- **🗣️ AI Voiceovers**: Integrated with **ElevenLabs** to generate unique voices for each character in the conversation.
- **💬 Dynamic Chat UI**: Automatically draws sent/received message bubbles, handles text wrapping, and supports image attachments.
- **🖼️ Profile Customization**: Processes profile pictures into circular avatars.
- **🎥 Automated Editing**:
  - Syncs the appearance of text bubbles with audio duration.
  - Implements a dynamic "scroll/reveal" mechanic.
  - Overlays content on background video (e.g., Minecraft parkour).
- **🔊 Sound Effects**: Adds notification sounds (e.g., "Ping") for specific message types.

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **FFmpeg**: Required for video processing with MoviePy.
3.  **ElevenLabs API Key**: Required for text-to-speech generation.

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Simion-Andrei/ShortsGenerator.git](https://github.com/Simion-Andrei/ShortsGenerator.git)
    cd ShortsGenerator
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install moviepy pillow python-dotenv elevenlabs numpy
    ```

## ⚙️ Configuration

### 1. Environment Variables
Create a `.env` file in the root directory and add your ElevenLabs API key:

```ini
ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
```

### 2. Project Data
The script requires specific assets in the `data/` folder to run correctly:

* **`content.json`**: The script defining the conversation (see structure below).
* **`minecraft.webm`**: The background video file (or any other vertical video).
* **`PING.mp3`**: The notification sound effect.
* **Profile Images**: Any images referenced in your JSON (e.g., `mom_pic.jpg`).

### 3. Conversation Script (`data/content.json`)
This file controls what happens in the video.

**Example Structure:**
```json
{
  "conversations": [
    {
      "name": "Mom",
      "profile": "data/mom_pic.jpg",
      "messages": [
        {
          "is_user": false,
          "is_image": false,
          "content": "Where are you?",
          "voiceId": "21m00Tcm4TlvDq8ikWAM"
        },
        {
          "is_user": true,
          "is_image": false,
          "content": "I'm at the library!",
          "voiceId": "AZnzlk1XvdvUeBnXmlld"
        },
        {
          "is_user": false,
          "is_image": true,
          "content": "data/evidence_photo.jpg"
        }
      ]
    }
  ]
}
```

* **`is_user`**: `true` for sent messages (right side), `false` for received messages (left side).
* **`voiceId`**: The specific ElevenLabs voice ID to use.
* **`is_image`**: Set to `true` to send an image file instead of text.

## 🚀 Usage

Run the main script to start the generation process:

```bash
python __main__.py
```

**The Process:**
1.  The script reads `data/content.json`.
2.  It calls ElevenLabs to generate audio for every text message (saved as `data/audioX.mp3`).
3.  It generates the visual conversation frames.
4.  It combines the audio, visual frames, and background video.
5.  The final video is saved as `video0.mov` (or `video{index}.mov`).

## 📂 Project Structure

```text
ShortsGenerator/
├── data/
│   ├── content.json        # The conversation script
│   ├── minecraft.webm      # Background footage
│   └── ...                 # Generated audio/images
├── scripts/
│   ├── CreateVideo.py      # Base class
│   ├── CreateVideoFakeMessages.py # Main logic
│   └── Utils.py            # Helper functions (corners, wrapping)
├── __main__.py             # Entry point
├── .env                    # API Keys
└── README.md
```

## 🤝 Contributing

Contributions are welcome!
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License.

---

**Made with ❤️ by [Simion-Andrei](https://github.com/Simion-Andrei)**