from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .data import ARTIFACTS
from .paths import KNOWLEDGE_BASE_DIR
from .translations import artifact_text, tab_label


MODEL_NAME = "qwen2.5:0.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"

STRICT_GUIDE_PROMPT = """You are Kemet Lens Museum Guide.
The APP_KNOWLEDGE block is your only allowed source of artifact facts.
Do not use outside knowledge, training data, memory, common history knowledge, or assumptions.
Do not use the dialect guide, examples, normalized meaning, artifact key, or user wording as a source of facts.
Use them only to understand the visitor's question.
Answer only when the answer is directly stated in APP_KNOWLEDGE.
Do not guess, infer, complete missing dates, or repeat unrelated overview text.
If the answer is not directly available in APP_KNOWLEDGE, say only the equivalent of:
'I do not have that information for this artifact.'
in the same language as the visitor's question.
Keep the answer short, clear, and suitable for tourists.
Use no more than 2 short sentences."""

DIALECT_GUIDE_PROMPT = """Understand English, Modern Standard Arabic, Egyptian Arabic, Arabizi/Franco Arabic, and mixed Arabic-English questions.
Use the normalized meaning only to understand informal wording.
Do not mention the normalization.
Answer in the same language as the visitor's original question.
If the visitor writes Arabizi/Franco Arabic with Latin letters, answer in simple Arabic using Arabic script.
Never answer in Persian, Farsi, Urdu, or another Arabic-script language.
Use the selected GUI language only if the question language is unclear."""

OLLAMA_UNAVAILABLE_MESSAGE = (
    "The offline AI guide is not available right now. Please make sure Ollama is running on this laptop."
)
MISSING_INFO_MESSAGES = {
    "en": "I do not have that information for this artifact.",
    "ar": "لا أملك هذه المعلومة عن هذه القطعة.",
    "fr": "Je n'ai pas cette information pour cet artefact.",
    "de": "Ich habe diese Information zu diesem Artefakt nicht.",
    "es": "No tengo esa información sobre este artefacto.",
}
MISSING_INFO_MESSAGE = MISSING_INFO_MESSAGES["en"]

LANGUAGE_NAMES = {
    "en": "English",
    "ar": "Arabic",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
}

ARTIFACT_ALIASES = {
    "tutankhamun": (
        "tutankhamun", "tutankhamon", "tutankhamen", "king tut", " tut ",
        "توت عنخ آمون", "توت عنخ امون", "الملك توت", " توت ",
    ),
    "ramses_ii": (
        "ramses", "ramesses", "ramsis", "ramsees", "ramses ii", "ramesses ii",
        "رمسيس الثاني", "رمسيس",
    ),
    "nefertiti": (
        "nefertiti", "nfrtiti", "نفرتيتي",
    ),
    "anubis": (
        "anubis", "anobis", "أنوبيس", "انوبيس",
    ),
    "pyramids_of_giza": (
        "pyramids of giza", "pyramids", "pyramid", "giza pyramids",
        "ahram", "ahramat", "el ahram", "haram khufu", "khufu",
        "أهرامات الجيزة", "اهرامات الجيزة", "الأهرامات", "الاهرامات",
        "الأهرام", "الاهرام", "هرم خوفو", "خوفو",
    ),
}


def resolve_artifact_key_from_question(question: str, fallback_key: str) -> str:
    """Choose the artifact knowledge file when a visitor names an artifact directly."""
    lowered = f" {question.lower()} "
    for artifact_key, aliases in ARTIFACT_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lowered:
                return artifact_key
    return fallback_key

# Light normalization for Egyptian Arabic and Arabizi.
# This is NOT the chatbot answer logic. It only clarifies informal wording before sending the
# question to the local Ollama model with the artifact text.
ARABIC_NORMALIZATION = {
    "مين": "من",
    "فين": "أين",
    "ليه": "لماذا",
    "إمتى": "متى",
    "امتى": "متى",
    "ايه": "ما هو",
    "إيه": "ما هو",
    "حكاية": "قصة",
    "الحكاية": "القصة",
    "اتبنى": "بُني",
    "اتعمل": "صُنع",
    "اتصنع": "صُنع",
    "اتدفن": "دُفن",
    "اكتشفه مين": "من اكتشفه",
    "مين اكتشف": "من اكتشف",
    "مشهور بايه": "بماذا يشتهر",
    "مشهور بإيه": "بماذا يشتهر",
    "بيمثل ايه": "ما رمزه أو معناه",
    "بيرمز لايه": "ما رمزه أو معناه",
    "بيهمنا ليه": "لماذا هو مهم",
    "مهم ليه": "لماذا هو مهم",
    "اتوجد فين": "أين وُجد",
    "موجود فين": "أين يوجد",
    "اتولد امتى": "متى وُلد",
    "مات امتى": "متى مات",
    "احكيلي": "اشرح لي",
    "ببساطة": "بطريقة بسيطة",
    "مين بنا": "من بنى",
    "مين بنى": "من بنى",
    "الهرم اتبنى امتى": "متى بُني الهرم",
    "هرم خوفو اتبنى امتى": "متى بُني هرم خوفو",
    "مين بنا الهرم": "من بنى الهرم",
    "مين بنا هرم خوفو": "من بنى هرم خوفو",
    "مين بنى هرم خوفو": "من بنى هرم خوفو",
    "مين بنا خوفو": "من بنى هرم خوفو",
    "مين بنى خوفو": "من بنى هرم خوفو",
    "خوفو مين": "من هو خوفو",
    "مين خوفو": "من هو خوفو",
    "من خوفو": "من هو خوفو",
    "خلافو": "خوفو",
    "العمال ولا العبيد": "هل بناه العمال أم العبيد",
    "عبيد": "عبيد",
}

ARABIZI_PHRASE_NORMALIZATION = {
    # Common question patterns
    "meen bana el haram": "من بنى الهرم",
    "meen bna el haram": "من بنى الهرم",
    "meen bana el ahram": "من بنى الأهرامات",
    "meen bna el ahram": "من بنى الأهرامات",
    "meen bana haram khufu": "من بنى هرم خوفو",
    "meen bana el haram khufu": "من بنى هرم خوفو",
    "meen bna haram khufu": "من بنى هرم خوفو",
    "meen bna el haram khufu": "من بنى هرم خوفو",
    "meen bana khufu": "من بنى هرم خوفو",
    "meen bna khufu": "من بنى هرم خوفو",
    "meen khufu": "من هو خوفو",
    "meen howa khufu": "من هو خوفو",
    "khufu meen": "من هو خوفو",
    "who is khufu": "من هو خوفو",
    "who was khufu": "من هو خوفو",
    "emta etbana el haram": "متى بُني الهرم",
    "emta etbana haram khufu": "متى بُني هرم خوفو",
    "emta etbana el haram khufu": "متى بُني هرم خوفو",
    "emta mat tutankhamun": "متى مات توت عنخ آمون",
    "emta tutankhamun mat": "متى مات توت عنخ آمون",
    "tutankhamun mat emta": "متى مات توت عنخ آمون",
    "meen anubis": "من هو أنوبيس",
    "meen anobis": "من هو أنوبيس",
    "who is anubis": "من هو أنوبيس",
    "anubis meen": "من هو أنوبيس",
    "leh anubis mashhour": "لماذا أنوبيس مشهور",
    "anubis mashhour leh": "لماذا أنوبيس مشهور",
    "meen nefertiti": "من هي نفرتيتي",
    "who is nefertiti": "من هي نفرتيتي",
    "nefertiti meen": "من هي نفرتيتي",
    "leh nefertiti mashhoora": "لماذا نفرتيتي مشهورة",
    "nefertiti mashhoora leh": "لماذا نفرتيتي مشهورة",
    "meen ramses": "من هو رمسيس الثاني",
    "meen ramsis": "من هو رمسيس الثاني",
    "who is ramses": "من هو رمسيس الثاني",
    "who is ramesses": "من هو رمسيس الثاني",
    "ramses meen": "من هو رمسيس الثاني",
    "ramsis meen": "من هو رمسيس الثاني",
    "emta ramses mat": "متى مات رمسيس الثاني",
    "emta ramsis mat": "متى مات رمسيس الثاني",
    "ramses mat emta": "متى مات رمسيس الثاني",
    "ramsis mat emta": "متى مات رمسيس الثاني",
    "ramses hokm kam sana": "كم سنة حكم رمسيس الثاني",
    "ramsis hokm kam sana": "كم سنة حكم رمسيس الثاني",
    "meen el ahram": "ما هي أهرامات الجيزة",
    "what are the pyramids": "ما هي أهرامات الجيزة",
    "el ahram fen": "أين توجد أهرامات الجيزة",
    "ahram fen": "أين توجد أهرامات الجيزة",
    "pyramids fen": "أين توجد أهرامات الجيزة",
    "tutankhamun mat 3ando kam sana": "كم كان عمر توت عنخ آمون عندما مات",
    "tutankhamun mat aando kam sana": "كم كان عمر توت عنخ آمون عندما مات",
    "mat 3ando kam sana": "كم كان عمره عندما مات",
    "mat aando kam sana": "كم كان عمره عندما مات",
    "how old was tutankhamun when he died": "كم كان عمر توت عنخ آمون عندما مات",
    "when did tutankhamun die": "متى مات توت عنخ آمون",
    "when did tutankhamun dies": "متى مات توت عنخ آمون",
    "el haram etbana emta": "متى بُني الهرم",
    "haram khufu etbana emta": "متى بُني هرم خوفو",
    "et3amal men eh": "مما صُنع",
    "etsana3 men eh": "مما صُنع",
    "made of eh": "مما صُنع",
    "leh mohem": "لماذا هو مهم",
    "leh howa mohem": "لماذا هو مهم",
    "leh da mohem": "لماذا هذا مهم",
    "eh ahameto": "ما أهميته",
    "eh ahmeyto": "ما أهميته",
    "eh hekayto": "ما قصته",
    "eh el hekaya": "ما القصة",
    "eh el story": "ما القصة",
    "eh el tareekh": "ما التاريخ",
    "eh tarikho": "ما تاريخه",
    "fen mawgood": "أين يوجد",
    "fen etla2a": "أين وُجد",
    "fen etlaqah": "أين وُجد",
    "fen etkashaf": "أين اكتُشف",
    "meen ektashaf": "من اكتشف",
    "meen kashaf": "من اكتشف",
    "kan 3ayesh fen": "أين عاش",
    "etdfen fen": "أين دُفن",
    "mat emta": "متى مات",
    "etwald emta": "متى وُلد",
    "etwled emta": "متى وُلد",
    "famous for eh": "بماذا يشتهر",
    "mashhour b eh": "بماذا يشتهر",
    "mashhour b eih": "بماذا يشتهر",
    "byrmoz l eh": "يرمز إلى ماذا",
    "byrmoz la eh": "يرمز إلى ماذا",
    "symbol of eh": "ما رمزه",
    "2oly summary": "اعطني ملخصًا",
    "2oli summary": "اعطني ملخصًا",
    "e7kili 3ano": "اشرح لي عنه",
    "e7kely 3ano": "اشرح لي عنه",
    "e7kili 3anoh": "اشرح لي عنه",
    "explain simply": "اشرح ببساطة",
    "2oli fun fact": "قل لي معلومة ممتعة",
    "fun fact": "معلومة ممتعة",
    "hidden info": "معلومات خفية",
    "show timeline": "اعرض الخط الزمني",
    "timeline": "الخط الزمني",
}

# Common Arabizi / Franco-Arabic words used by Egyptian users.
# These mappings only help Ollama understand the user's wording; they are not answer logic.
ARABIZI_NORMALIZATION = {
    # Question words
    "meen": "من", "min": "من", "mn": "من", "who": "من",
    "fen": "أين", "feen": "أين", "fein": "أين", "fain": "أين", "where": "أين",
    "leh": "لماذا", "leih": "لماذا", "lei": "لماذا", "why": "لماذا",
    "emta": "متى", "imta": "متى", "emte": "متى", "when": "متى",
    "eh": "ما هو", "eih": "ما هو", "ayh": "ما هو", "what": "ما هو",
    "ezay": "كيف", "ezzay": "كيف", "izay": "كيف", "how": "كيف",
    "kam": "كم", "ad": "قدر", "2ad": "قدر",
    "sana": "سنة", "seneen": "سنين", "senen": "سنين", "year": "سنة", "years": "سنين",

    # Common Egyptian particles / connectors
    "el": "ال", "al": "ال", "da": "هذا", "de": "هذه", "di": "هذه", "dah": "هذا",
    "do": "هؤلاء", "dol": "هؤلاء", "howa": "هو", "hya": "هي", "hiya": "هي",
    "aando": "عنده", "3ando": "عنده", "ando": "عنده", "3ndo": "عنده", "omro": "عمره",
    "w": "و", "we": "و", "wa": "و", "aw": "أو", "wala": "ولا",
    "fi": "في", "fe": "في", "fel": "في ال", "f el": "في ال", "men": "من", "mn": "من",
    "3an": "عن", "aan": "عن", "3ala": "على", "ala": "على", "l": "ل", "le": "ل", "la": "ل",
    "b": "ب", "be": "ب", "bel": "بال", "bl": "بال",
    "keda": "هكذا", "kda": "هكذا", "bas": "فقط", "bs": "فقط", "gedan": "جدا",

    # Verbs users often use
    "bana": "بنى", "bna": "بنى", "banah": "بنى", "built": "بنى", "build": "بنى",
    "etbana": "بُني", "etbany": "بُني", "etbna": "بُني", "etbena": "بُني",
    "3amal": "عمل", "amal": "عمل", "et3amal": "صُنع", "etsana3": "صُنع", "etsane3": "صُنع",
    "made": "صُنع", "sana3": "صنع", "material": "المادة", "materials": "المواد",
    "etdfen": "دُفن", "etdafen": "دُفن", "dafn": "دفن", "buried": "دُفن",
    "mat": "مات", "maat": "مات", "died": "مات", "die": "مات", "dies": "مات", "moot": "موت",
    "etwald": "وُلد", "etwled": "وُلد", "born": "وُلد",
    "3ash": "عاش", "aash": "عاش", "lived": "عاش",
    "ektashaf": "اكتشف", "ektashef": "اكتشف", "etkashaf": "اكتُشف", "discovered": "اكتُشف",
    "kashaf": "كشف", "la2a": "وجد", "la2o": "وجدوا", "found": "وُجد",
    "e7ki": "احكي", "e7kili": "احكي لي", "e7kely": "احكي لي", "explain": "اشرح",
    "2oli": "قل لي", "2oly": "قل لي", "olly": "قل لي", "tell": "قل لي",
    "wareeni": "أرني", "show": "اعرض", "compare": "قارن", "far2": "فرق", "difference": "فرق",

    # History / importance / meaning
    "mohem": "مهم", "mohm": "مهم", "important": "مهم", "importance": "أهمية",
    "aham": "أهم", "ahamya": "أهمية", "ahmeya": "أهمية", "ahmeyto": "أهميته", "ahameto": "أهميته",
    "tareekh": "تاريخ", "tarikh": "تاريخ", "history": "تاريخ", "story": "قصة", "hekaya": "قصة", "7ekaya": "قصة",
    "ma3na": "معنى", "meaning": "معنى", "symbol": "رمز", "ramz": "رمز", "byrmoz": "يرمز", "beyrmoz": "يرمز",
    "religion": "الدين", "dein": "الدين", "myth": "أسطورة", "ostora": "أسطورة", "osora": "أسطورة",
    "fun": "ممتع", "fact": "معلومة", "facts": "معلومات", "secret": "سر", "hidden": "خفي", "info": "معلومات",

    # Places / artifact words
    "haram": "هرم", "ahram": "أهرامات", "ahramat": "أهرامات", "pyramid": "هرم", "pyramids": "أهرامات",
    "giza": "الجيزة", "geza": "الجيزة", "giza plateau": "هضبة الجيزة",
    "luxor": "الأقصر", "lo2sor": "الأقصر", "aswan": "أسوان", "nile": "النيل",
    "valley": "وادي", "kings": "الملوك", "valley of kings": "وادي الملوك",
    "museum": "متحف", "tomb": "مقبرة", "maqbara": "مقبرة", "ma2bara": "مقبرة",
    "temple": "معبد", "ma3bad": "معبد", "statue": "تمثال", "mask": "قناع", "mummy": "مومياء",

    # Names / classes in the project
    "khufu": "خوفو", "khoufu": "خوفو", "khofu": "خوفو", "kufu": "خوفو", "khoufo": "خوفو", "cheops": "خوفو",
    "khafre": "خفرع", "kafre": "خفرع", "chephren": "خفرع",
    "menkaure": "منكاورع", "mankaure": "منكاورع", "menkara": "منكاورع", "mykerinos": "منكاورع",
    "tut": "توت عنخ آمون", "tutankhamun": "توت عنخ آمون", "tutankhamon": "توت عنخ آمون", "tout": "توت عنخ آمون",
    "nefertiti": "نفرتيتي", "nfrtiti": "نفرتيتي",
    "ramses": "رمسيس", "ramesses": "رمسيس", "ramsis": "رمسيس", "ramsees": "رمسيس",
    "anubis": "أنوبيس", "anobis": "أنوبيس",
    "abu": "أبو", "simbel": "سمبل", "abusimbel": "أبو سمبل",
    "sphinx": "أبو الهول", "abu el hol": "أبو الهول", "abou el hol": "أبو الهول",

    # Common nouns/adjectives for tourist questions
    "king": "ملك", "pharaoh": "فرعون", "queen": "ملكة", "god": "إله", "goddess": "إلهة",
    "worker": "عامل", "workers": "عمال", "slave": "عبد", "slaves": "عبيد", "engineer": "مهندس", "engineers": "مهندسون",
    "gold": "ذهب", "stone": "حجر", "limestone": "حجر جيري", "granite": "جرانيت", "wood": "خشب",
    "old": "قديم", "ancient": "قديم", "new": "جديد", "big": "كبير", "small": "صغير",
    "simple": "بسيط", "summary": "ملخص", "short": "مختصر", "quick": "سريع",
}


def artifact_knowledge_path(language: str, artifact_key: str) -> Path:
    return KNOWLEDGE_BASE_DIR / language / f"{artifact_key}.txt"


def load_artifact_knowledge(language: str, artifact_key: str) -> str:
    path = artifact_knowledge_path(language, artifact_key)
    if not path.exists():
        # Fallback to English if the selected language file is missing.
        path = artifact_knowledge_path("en", artifact_key)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def format_gui_artifact_data(language: str, artifact_key: str) -> str:
    artifact = ARTIFACTS.get(artifact_key)
    if artifact is None:
        return ""

    localized = artifact_text(language, artifact)
    lines: list[str] = [
        "GUI DATA CURRENTLY SHOWN IN THE APP",
        f"Display Name: {localized['display_name']}",
        f"Short Description: {localized['short_description']}",
        "",
        f"{tab_label(language, 'Overview')}:",
        str(localized["overview"]),
        "",
        f"{tab_label(language, 'History')}:",
        str(localized["history"]),
        "",
        f"{tab_label(language, 'Quick Facts')}:",
    ]
    for item in localized["quick_facts"]:
        label = item.get("label", "").strip()
        value = item.get("value", "").strip()
        lines.append(f"- {label}: {value}" if label else f"- {value}")

    lines.extend(["", f"{tab_label(language, 'Historical Timeline')}:"])
    for item in localized["timeline"]:
        date = item.get("date", "").strip()
        event = item.get("event", "").strip()
        lines.append(f"- {date}: {event}" if date else f"- {event}")

    lines.extend(["", f"{tab_label(language, 'Why It Matters')}:"])
    for item in localized["why_it_matters"]:
        title = item.get("title", "").strip()
        body = item.get("text", "").strip()
        lines.append(f"- {title}: {body}" if title else f"- {body}")

    lines.extend(["", f"{tab_label(language, 'Did You Know?')}:"])
    for item in localized["did_you_know"]:
        lines.append(f"- {item}")

    lines.extend(["", f"{tab_label(language, 'Hidden Info')}:"])
    for item in localized["hidden_info"]:
        lines.append(f"- {item}")

    lines.extend(["", f"{tab_label(language, 'Fun Facts')}:"])
    for item in localized["fun_facts"]:
        lines.append(f"- {item}")
    return "\n".join(lines).strip()


def load_app_knowledge(language: str, artifact_key: str) -> str:
    file_knowledge = load_artifact_knowledge(language, artifact_key)
    if file_knowledge:
        return "TEXT KNOWLEDGE FILE\n" + file_knowledge
    return format_gui_artifact_data(language, artifact_key)


def missing_info_message_for(language: str, question: str) -> str:
    if any("\u0600" <= char <= "\u06ff" for char in question):
        return MISSING_INFO_MESSAGES["ar"]
    return MISSING_INFO_MESSAGES.get(language, MISSING_INFO_MESSAGE)


def normalize_egyptian_arabic_question(question: str) -> str:
    """Return a clearer meaning for Egyptian Arabic / Arabizi questions.

    This helper does not answer the question and does not replace the local LLM/RAG logic.
    It only gives Ollama a cleaner interpretation of informal Egyptian wording.
    """
    normalized = question.strip()
    if not normalized:
        return ""

    # Arabic phrase replacements first.
    for slang, formal in sorted(ARABIC_NORMALIZATION.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = normalized.replace(slang, formal)

    # Arabizi phrase replacements before token-level replacements.
    lowered_for_phrases = normalized.lower()
    for phrase, formal in sorted(ARABIZI_PHRASE_NORMALIZATION.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase in lowered_for_phrases:
            lowered_for_phrases = lowered_for_phrases.replace(phrase, formal)
    normalized = lowered_for_phrases

    # Arabizi replacements are done on word boundaries where possible.
    words = normalized.split()
    converted_words: list[str] = []
    for word in words:
        clean = word.strip("؟?.,!،؛:()[]{}\"'").lower()
        replacement = ARABIZI_NORMALIZATION.get(clean)
        converted_words.append(replacement if replacement else word)
    normalized = " ".join(converted_words)

    return normalized


def looks_like_arabizi_question(question: str, normalized_question: str) -> bool:
    if any("\u0600" <= char <= "\u06ff" for char in question):
        return False
    lowered = f" {question.lower()} "
    markers = (
        " emta ", " imta ", " meen ", " fen ", " feen ", " leh ", " eih ", " eh ",
        " mat ", " 3ando ", " aando ", " kam sana ", " sana ", " e7ki ", " 2oli ",
    )
    return any(marker in lowered for marker in markers)


def contains_arabic(text: str) -> bool:
    return any("\u0600" <= char <= "\u06ff" for char in text)


def looks_like_english_question(question: str) -> bool:
    lowered = f" {question.lower()} "
    markers = (
        " who ", " what ", " why ", " where ", " when ", " how ", " tell ", " show ",
        " is ", " are ", " was ", " were ", " did ", " does ", " do ",
    )
    return any(marker in lowered for marker in markers)


def knowledge_language_for_question(selected_language: str, question: str, normalized_question: str) -> str:
    if looks_like_arabizi_question(question, normalized_question) or contains_arabic(question):
        return "ar"
    if looks_like_english_question(question):
        return "en"
    return selected_language


def normalize_for_matching(value: str) -> str:
    text = normalize_egyptian_arabic_question(value).lower()
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


DIRECT_QA_STOPWORDS = {
    "س", "ج", "q", "a", "من", "هو", "هي", "ما", "ماذا", "لماذا", "اين", "أين", "متى",
    "عن", "على", "في", "هذا", "هذه", "احكي", "اشرح", "قل", "لي", "the", "is", "are", "was", "were", "who", "what",
    "why", "where", "when", "did", "does", "do", "this", "that", "about", "with",
}


def direct_answer_tokens(value: str) -> set[str]:
    normalized = normalize_for_matching(value)
    for mark in "؟?.,!،؛:()[]{}\"'/-":
        normalized = normalized.replace(mark, " ")
    return {
        token
        for token in normalized.split()
        if len(token) > 2 and token not in DIRECT_QA_STOPWORDS
    }


def clean_direct_answer(answer_line: str) -> str:
    answer = answer_line.strip()
    for prefix in ("ج:", "ج：", "A:", "A：", "Answer:", "answer:"):
        if answer.startswith(prefix):
            return answer[len(prefix):].strip()
    return answer


def find_direct_answer_in_knowledge(artifact_info: str, question: str, normalized_question: str) -> str:
    """Use explicit Q/A lines from the knowledge file when Ollama drifts."""
    question_tokens = direct_answer_tokens(f"{question} {normalized_question}")
    if not question_tokens:
        return ""

    lines = [line.strip() for line in artifact_info.splitlines() if line.strip()]
    best_answer = ""
    best_score = 0
    q_match = f" {normalize_for_matching(question)} "
    for index, line in enumerate(lines):
        if not (line.startswith("س:") or line.startswith("Q:")):
            continue
        qa_tokens = direct_answer_tokens(line)
        score = len(question_tokens & qa_tokens)

        line_match = f" {normalize_for_matching(line)} "
        if any(marker in q_match for marker in (" meen ", " who ", " مين ", " من ")):
            if any(marker in line_match for marker in (" who ", " مين ", " من ")):
                score += 1
        if any(marker in q_match for marker in (" احكي ", " اشرح ", " tell ", " explain ")):
            if any(marker in line_match for marker in (" who ", " مين ", " من ")):
                score += 1
        if any(marker in q_match for marker in (" emta ", " when ", " مات ", " mat ", " die ", " dies ", " died ")):
            if any(marker in line_match for marker in (" when ", " متى ", " مات ", " died ", " die ")):
                score += 1
        if any(marker in q_match for marker in (" leh ", " why ", " ليه ", " لماذا ")):
            if any(marker in line_match for marker in (" why ", " ليه ", " لماذا ")):
                score += 1

        if score <= best_score:
            continue
        for answer_line in lines[index + 1:index + 4]:
            if answer_line.startswith(("ج:", "A:", "Answer:", "س:", "Q:")):
                if answer_line.startswith(("ج:", "A:", "Answer:")):
                    best_score = score
                    best_answer = clean_direct_answer(answer_line)
                break
    return best_answer if best_score >= 2 else ""


def build_ollama_prompt(language: str, artifact_key: str, artifact_info: str, question: str) -> str:
    language_name = LANGUAGE_NAMES.get(language, "English")
    normalized_question = normalize_egyptian_arabic_question(question)
    if looks_like_arabizi_question(question, normalized_question):
        answer_language_instruction = (
            "The original question is Arabizi/Franco Arabic written with Latin letters. "
            "Answer in simple Arabic using Arabic script. Do not answer in Persian, Farsi, Urdu, or any other language."
        )
    else:
        answer_language_instruction = (
            "Answer in the same language as the original user question. "
            "Use the selected GUI language only if the user question language is unclear."
        )
    return (
        f"{STRICT_GUIDE_PROMPT}\n\n"
        f"{DIALECT_GUIDE_PROMPT}\n\n"
        "Important: The dialect guide and normalized meaning are language aids only. "
        "They are not artifact information and must not be used as factual evidence.\n\n"
        f"Selected GUI language: {language_name} ({language}).\n"
        f"{answer_language_instruction} "
        "If the selected GUI language is Arabic and the user's wording is informal Egyptian Arabic, answer in simple Egyptian Arabic. "
        "Do not translate artifact names unless the provided information does so.\n\n"
        "Question understanding help: If the visitor asks when someone died, how old they were when they died, "
        "or uses wording like 'mat', 'emta mat', 'aando kam sana', or imperfect English such as 'when did ... dies', "
        "look for sections such as Age at Death, Death and Health, Historical Timeline, and chatbot Q&A inside APP_KNOWLEDGE.\n\n"
        f"Artifact key: {artifact_key}\n\n"
        f"<APP_KNOWLEDGE>\n{artifact_info}\n</APP_KNOWLEDGE>\n\n"
        f"Original user question:\n{question}\n\n"
        f"Normalized meaning for understanding only:\n{normalized_question}\n\n"
        "Final answer using APP_KNOWLEDGE only:"
    )


def build_source_check_prompt(artifact_info: str, question: str, answer: str) -> str:
    return (
        "You are a strict source checker for Kemet Lens.\n"
        "Your task is not to answer the visitor.\n"
        "Check whether the CANDIDATE_ANSWER is fully supported by APP_KNOWLEDGE.\n"
        "APP_KNOWLEDGE is the only allowed source.\n"
        "If every factual claim in CANDIDATE_ANSWER is directly supported by APP_KNOWLEDGE, reply YES.\n"
        "If any factual claim uses outside knowledge, guesses, assumptions, or information not directly stated, reply NO.\n"
        "Reply with only YES or NO.\n\n"
        f"<APP_KNOWLEDGE>\n{artifact_info}\n</APP_KNOWLEDGE>\n\n"
        f"VISITOR_QUESTION:\n{question}\n\n"
        f"CANDIDATE_ANSWER:\n{answer}\n\n"
        "VERDICT:"
    )


def answer_is_supported_by_app_knowledge(requests_module, artifact_info: str, question: str, answer: str) -> bool:
    stripped_answer = answer.strip()
    if not stripped_answer:
        return False
    if stripped_answer in MISSING_INFO_MESSAGES.values():
        return True
    if len(stripped_answer) < 18 or len(stripped_answer.split()) < 3:
        return False

    payload = {
        "model": MODEL_NAME,
        "prompt": build_source_check_prompt(artifact_info, question, answer),
        "stream": False,
        "options": {
            "temperature": 0,
            "top_k": 1,
            "top_p": 0.1,
        },
    }
    try:
        response = requests_module.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        verdict = str(response.json().get("response", "")).strip().upper()
    except requests_module.RequestException:
        return True
    except ValueError:
        return True
    return verdict.startswith("YES")


class OllamaGuideWorker(QThread):
    answer_ready = Signal(str, str)

    def __init__(self, language: str, artifact_key: str, question: str, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self.artifact_key = artifact_key
        self.question = question.strip()

    def run(self) -> None:
        try:
            import requests
        except ImportError:
            self.answer_ready.emit(OLLAMA_UNAVAILABLE_MESSAGE, self.artifact_key)
            return

        normalized_question = normalize_egyptian_arabic_question(self.question)
        is_arabizi = looks_like_arabizi_question(self.question, normalized_question)
        effective_artifact_key = resolve_artifact_key_from_question(self.question, self.artifact_key)
        knowledge_language = knowledge_language_for_question(self.language, self.question, normalized_question)
        artifact_info = load_app_knowledge(knowledge_language, effective_artifact_key)
        if not artifact_info:
            self.answer_ready.emit(missing_info_message_for(self.language, self.question), self.artifact_key)
            return
        direct_answer = find_direct_answer_in_knowledge(artifact_info, self.question, normalized_question)

        prompt = build_ollama_prompt(self.language, effective_artifact_key, artifact_info, self.question)
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "top_k": 1,
                "top_p": 0.1,
            },
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()
            answer = str(data.get("response", "")).strip() or missing_info_message_for(self.language, self.question)
            expects_arabic_answer = is_arabizi or contains_arabic(self.question)
            wrong_script = expects_arabic_answer and not contains_arabic(answer)
            answered_missing = answer.strip() in MISSING_INFO_MESSAGES.values()
            unsupported = not answer_is_supported_by_app_knowledge(requests, artifact_info, self.question, answer)
            if wrong_script or answered_missing or unsupported:
                answer = direct_answer or missing_info_message_for(knowledge_language, self.question)
        except requests.RequestException:
            answer = OLLAMA_UNAVAILABLE_MESSAGE
        except ValueError:
            answer = OLLAMA_UNAVAILABLE_MESSAGE

        self.answer_ready.emit(answer, self.artifact_key)
