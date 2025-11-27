# Wayler Notes

## 1. GEMINI API key / environment configuration
- Fixed a Django startup error caused by using the raw GEMINI API key as the `decouple.config` option name.
- In `LearningSystem/settings.py`, changed:
  - `GEMINI_API_KEY = config("AIzaSyAiLQuJFl5bNGDHJQIQoiwZN0r1Xnwzn1M")`
  - To: `GEMINI_API_KEY = config("GEMINI_API_KEY")`
- Agreed convention:
  - Real GEMINI API key is provided via environment variable or `.env` file, not hard‑coded in settings.
  - Example `.env` entry:
    - `GEMINI_API_KEY=your_real_gemini_api_key_here`

## 2. .env file setup
- Instructions for creating `.env` in the Django project root:
  - PowerShell: `New-Item -Path ".env" -ItemType File -Force`
  - Then add: `GEMINI_API_KEY=your_real_gemini_api_key_here`
- Alternative: set environment variable in shell before running Django commands:
  - `$env:GEMINI_API_KEY = "your_real_gemini_api_key_here"`

## 3. Accessibility and blind user mode: TTS and structure
- Existing work in uncommitted changes:
  - Added TTS controls and wrappers to several templates:
    - `home.html`: `#tts-home` region and TTS buttons.
    - `learning_resources.html`: `#tts-content` region and TTS buttons.
    - `study_topic.html`: `#tts-topic-content` region and TTS buttons.
    - `learning_path.html`: includes `_tts_global.html` for shared controls.
  - Added language awareness via `window.USER_LANGUAGE_CODE = "{{ user_language|default:'en' }}"` on relevant pages.
  - `views.py`: passes `user_language` based on `Student_Profile.preferred_language` (default `"en"`).
  - JS helper at `MyProject/static/MyProject/js/tts.js`:
    - Maps app language codes to Web Speech API language codes.
    - Exposes global `startReading(selector)` and `stopReading()` wrappers.

## 4. New blind / normal / deaf mode concept
- Agreed conceptual behavior for **blind user mode**:
  - **AI‑powered features for image descriptions**: screen readers (and platform services) generate rich, AI‑based descriptions for images and other visual content.
  - **Activation by double‑tap anywhere**: once an item has focus, the user can double‑tap anywhere on the screen to activate it.
  - **System navigation via touch exploration and swipes**: moving a finger around announces the item under the finger; swiping right/left moves focus to next/previous element.
- Introduced three explicit modes:
  - `Normal`: standard visual interface, no extra screen‑reader guidance.
  - `Blind`: optimized for screen reader + TTS, with the above behavior description.
  - `Deaf`: focuses on transcripts, captions, and on‑screen text rather than audio.

## 5. Global accessibility mode selector in `_tts_global.html`
- Implemented: `_tts_global.html` now provides a **global mode selector** and global blind‑mode TTS controls.
- Behavior:
  - Loads static and TTS JS.
  - Renders a fixed‑position **mode selector** (Normal / Blind / Deaf):
    - `<select id="accessibility-mode-select" onchange="setAccessibilityMode(this.value)">` with options for each mode.
  - Provides screen‑reader accessible descriptions:
    - A visually hidden container with three `<p data-mode="...">` entries:
      - For `blind`:
        - "AI‑powered features for image descriptions, activation by double‑tap anywhere once the item is focused, and system navigation via touch exploration and left/right swipes." (conceptual description only; actual gesture behavior still provided by OS/AT).
      - For `normal`: short description of standard UI.
      - For `deaf`: emphasizes transcripts/captions.
  - Global TTS bar:
    - Fixed at bottom right.
    - Marked with `data-mode-only="blind"` so it only displays in blind mode.
    - Buttons:
      - `startReading('body')` → read the whole page.
      - `stopReading()` → stop speech.
  - JavaScript logic in `_tts_global.html`:
    - `applyAccessibilityMode(mode)`:
      - Persists mode to `localStorage` under `"accessibility_mode"`.
      - Shows/hides description `<p>` elements based on `data-mode`.
      - Shows/hides any element with `data-mode-only="blind"` (global + page‑level TTS controls).
    - Exposes `window.setAccessibilityMode(mode)` so pages can reuse it.
    - On `DOMContentLoaded`, reads persisted mode (if any) and applies it, defaulting to the profile’s `accessibility_mode` (fallback `normal`).

## 6. Page-level integration for blind user mode
- Pattern for replacing existing TTS blocks in templates like `home.html`, `learning_resources.html`, `study_topic.html`:
  - Replace simple TTS bar with an **accessibility mode selector + description + TTS controls**.
  - Example structure:
    - Mode selector:
      - Label + `<select>` with `normal`, `blind`, `deaf`.
    - Description container:
      - `<p data-mode="blind">` with the AI‑powered / double‑tap / swipe explanation.
      - `<p data-mode="normal">` and `<p data-mode="deaf">` with short descriptions.
    - TTS controls:
      - Wrapped in a container with `data-mode-only="blind"` so they respect the selected mode.
      - Use the appropriate content selector per page:
        - `'#tts-home'` on home.
        - `'#tts-content'` on learning resources.
        - `'#tts-topic-content'` on study topic.
- Page-level logic can either:
  - Use the global `setAccessibilityMode` defined in `_tts_global.html` (preferred), or
  - Define its own small wrapper that defers to the global if present.

## 7. Transcripts and captions for deaf / hard-of-hearing support
- Added a transcript field for materials:
  - In `MyProject/models.py`: `transcript = models.TextField(blank=True, null=True, help_text='Optional transcript text for audio/video materials')`.
- Added a captions file field for materials:
  - In `MyProject/models.py`: `captions_file = models.FileField(upload_to='captions/', blank=True, null=True, help_text='Optional caption file (e.g. WebVTT) for video/audio')`.
  - **Note:** This requires uploading and managing caption files (more work for content authors), similar to how YouTube/edX/Coursera handle captions.
- `course_detail.html`:
  - Under course materials, each material can show:
    - A `<video>` tag with `<track kind="captions">` when `captions_file` is present.
    - An `<audio>` tag for audio materials.
    - A transcript section:
      - Expanded by default when `student_profile.prefers_transcripts` or `student_profile.needs_captions` is true.
      - Otherwise rendered as `<details><summary>Transcript</summary>`.
    - Transcript content is wrapped in `.material-transcript` with an `aria-label` like:
      - `aria-label="Transcript for {{ m.title }}"`.
- This aligns with the **Deaf** mode, where primary access is through text and captions instead of audio.

---

This file is a running summary of what was done in this session:
- Fixed environment configuration around GEMINI API key.
- Documented `.env` and envvar usage.
- Clarified and documented blind user mode behavior.
- Implemented a global accessibility mode selector (Normal / Blind / Deaf) in `_tts_global.html` and wired it to page-level TTS via `data-mode-only="blind"`.
- Added transcript and caption support for materials, plus user-level preferences (`accessibility_mode`, `needs_captions`, `prefers_transcripts`) to drive deaf/blind behavior.
