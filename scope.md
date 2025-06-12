
We are building an **Instagram Carousel Content Generator Bot** powered by NLP. It ingests a user’s Instagram profile, selects top-performing posts, and helps generate carousel post ideas using storytelling techniques based on a structured method (HOP Method). Content goals, voice tones, and optional user inputs will shape the generated carousel output.

---

## 🧱 **Tech Stack**

* **Frontend:** React
* **Backend:** Flask
* **AI/NLP:** Anthropic API, Optional: RAG (for knowledge docs, HOP Method)
* **Storage:** PostgreSQL / Firebase (User Profiles & Saved Data)
* **Authentication:** Firebase Auth or custom JWT
* **Media Processing (Voice Note):** Whisper (for STT) or use existing integrations
* **Deployment:** Dockerized services, optional AWS/GCP

---

## 📲 **User Flow**

1. User logs in.
2. Inputs Instagram profile link (with option to save profile).
3. System fetches top 3 posts via scraping or third-party IG API.
4. One post must be a sales post (content type classification).
5. User selects:

   * **Goal:** Awareness / Sell / Nurture
   * **HOP Method:** (e.g., Humble Brag, Origin Story)
   * **Voice Tone:** Direct/Bold, Storytelling, Witty/Edgy
   * (Optional) Inspiration post link
   * (Optional) Long voice note or journal entry
6. System uses all inputs to:

   * Extract micro-story (from voice)
   * Generate a carousel outline: Hook → Story Pages → CTA
7. User receives up to 10-page carousel structure as output.

---

## 🏗️ **Architecture Overview**

```text
[React Frontend]
    |
    | REST APIs (JSON)
    v
[Flask Backend] <--> [PostgreSQL DB]
    |
    |-- [Instagram Scraper / API Integration]
    |-- [RAG: Curriculum/Framework Embeddings + Anthropic for Generation]
    |-- [STT: Voice Note Processor (Whisper or third-party)]
    |-- [Prompt Builder: Based on Goal + HOP + Voice Tone]
    v
[Anthropic API / Claude] or [Custom LangChain RAG Pipeline]
```

---

## 🔗 **Frontend - React**

### Pages / Components

* **Login/Register**
* **Dashboard**
* **Profile Manager** (Saved Instagram profiles)
* **Content Generator Form**

  * IG Profile Link Input
  * Post Goal (Select)
  * HOP Method (Select)
  * Voice Tone Toggle
  * Paste inspiration link
  * Upload voice note / paste journal entry
* **Results View** (Carousel Pages Preview)
* **Settings** (Tone calibration, etc.)

### API Calls

| Endpoint                     | Method | Description                        |
| ---------------------------- | ------ | ---------------------------------- |
| `/api/profile/save`          | POST   | Save user IG profile               |
| `/api/posts/analyze`         | POST   | Fetch top 3 posts + classify       |
| `/api/carousel/generate`     | POST   | Generate carousel structure        |
| `/api/story/extract`         | POST   | Extract story from long-form input |
| `/api/user/voice-tone/train` | POST   | Train voice tone (optional RAG)    |

---

## 🔌 **Backend - Flask**

### Main APIs

```python
@app.route("/api/profile/save", methods=["POST"])
def save_profile(): ...

@app.route("/api/posts/analyze", methods=["POST"])
def analyze_posts(): ...

@app.route("/api/carousel/generate", methods=["POST"])
def generate_carousel(): ...

@app.route("/api/story/extract", methods=["POST"])
def extract_story(): ...

@app.route("/api/user/voice-tone/train", methods=["POST"])
def train_voice_tone(): ...
```

### Key Modules

* **Instagram Scraper/API** – Pull posts + metrics
* **Post Classifier** – Detect post types (Sales/Nurture/Awareness)
* **Goal → Prompt Mapping** – Inject storytelling prompt patterns
* **RAG Component** – Index curriculum & frameworks
* **Voice Note Processor** – STT → micro-story extraction
* **Prompt Builder** – Compose Anthropic-friendly instructions
* **Response Formatter** – Format into 10-page carousel structure

---

## 📘 **RAG Strategy (Optional but Recommended)**

Use LangChain or LlamaIndex to embed:

* HOP Method Docs
* Transcripts/Frameworks
  Use it to enrich prompt context sent to Claude/Anthropic.

---

## 🧪 **AI Prompt Sample**

```txt
User Goal: Sell
HOP Method: Origin Story
Tone: Bold & Direct

Context: [micro-story extracted from voice note or journal]

Instruction: Using the HOP storytelling structure, outline a 10-page Instagram carousel. 
Page 1: Hook
Pages 2–9: Story (aligned with user’s selected method)
Page 10: Call to Action
```

---

## 🗃️ **Database Tables**

### `users`

\| id | email | name | ... |

### `instagram_profiles`

\| id | user\_id | profile\_link | saved\_at |

### `carousel_requests`

\| id | user\_id | profile\_id | goal | method | tone | inspiration\_url | voice\_note\_path | created\_at |

### `generated_carousels`

\| id | request\_id | page\_number | content |


