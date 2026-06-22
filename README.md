# Kemet Lens Readdy PySide6 GUI

A fresh PySide6 recreation of the supplied Readdy mobile prototype.

## Run

```powershell
cd C:\Users\farah\Documents\Codex\2026-05-21\i-will-attach-1-readdy-screenshots\kemet_lens_readdy_gui
python main.py
```

The app launches full-screen on the laptop and keeps the Readdy-style mobile experience centered in a portrait stage. Local image assets live in `assets/`.

If your default Python reports a PySide6 DLL import error, run it from a clean virtual environment with `pip install -r requirements.txt`.

## AI Integration Point

Use `KemetLensWindow.handle_detection(class_name, confidence)` to update the result screen from a real model output. Unknown classes or low confidence route to the helpful unknown screen.

## Ask Bakkar Offline Chatbot

Ask Bakkar uses local knowledge files from `knowledge_base/<language>/<artifact_key>.txt` and sends the selected artifact text plus the user's question to local Ollama at `http://localhost:11434/api/generate`.

The chatbot includes extra prompt support for Egyptian Arabic dialect, Arabizi/Franco Arabic, and mixed Arabic-English questions. It lightly normalizes informal words such as `مين`, `فين`, `ليه`, `امتى`, `ايه`, `اتعمل`, and Arabizi words such as `meen`, `fen`, `leh`, `emta`, and `et3amal` before sending the question to Ollama. The normalization is only for understanding; answers are still generated from the local artifact text files.

Recommended Windows test model:

```powershell
ollama run qwen2.5:0.5b
```
