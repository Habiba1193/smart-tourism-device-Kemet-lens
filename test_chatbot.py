import sys

from kemet_lens.chatbot import build_ollama_prompt, normalize_egyptian_arabic_question, load_artifact_knowledge


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def preview_prompt(language: str, artifact_key: str, question: str) -> None:
    artifact_info = load_artifact_knowledge(language, artifact_key)
    prompt = build_ollama_prompt(language, artifact_key, artifact_info, question)
    print("Original question:", question)
    print("Normalized meaning:", normalize_egyptian_arabic_question(question))
    print("\nPrompt preview:\n")
    print(prompt[:1800])


if __name__ == "__main__":
    preview_prompt("ar", "pyramids_of_giza", "مين بنا الهرم؟")
