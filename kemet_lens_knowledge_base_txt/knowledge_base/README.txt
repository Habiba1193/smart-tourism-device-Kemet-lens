Kemet Lens Offline RAG Knowledge Base

This folder contains local text files for the "Ask the Museum Guide" offline chatbot.

How to use:
1. When YOLO detects an artifact class, use the class key to open the matching text file.
   Example:
   detected class = tutankhamun
   file = knowledge_base/tutankhamun.txt

2. Send the content of the text file plus the user's question to Ollama.

3. Use a strict prompt:
   "Answer only using the artifact information provided. Do not use outside knowledge."

Included artifact files:
- tutankhamun.txt
- nefertiti.txt
- ramses.txt
- anubis.txt
- pyramids.txt

These files include:
- short description
- overview
- historical background
- era
- dynasty
- materials
- famous for
- location
- symbolism
- why it matters
- timeline
- did you know
- hidden detail
- fun facts
- common user questions

Note:
These text files are a starting knowledge base. You can add more details, translations, image paths, or new artifacts later.
