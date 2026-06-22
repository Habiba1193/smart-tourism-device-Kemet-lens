from functools import lru_cache
from pathlib import Path
import re

from .artifact_content import ARTIFACT_CONTENT


LANGUAGES = [
    {"code": "en", "icon": "En", "native": "English", "english": "English"},
    {"code": "ar", "icon": "ع", "native": "العربية", "english": "Arabic"},
    {"code": "fr", "icon": "Fr", "native": "Français", "english": "French"},
    {"code": "de", "icon": "De", "native": "Deutsch", "english": "German"},
    {"code": "es", "icon": "Es", "native": "Español", "english": "Spanish"},
]


UI = {
    "en": {
        "back": "Back",
        "brand": "KEMET LENS",
        "splash_tagline": "AWAKEN THE PAST",
        "home_title": "BEGIN YOUR JOURNEY\nTHROUGH ANCIENT\nEGYPT",
        "home_subtitle": "Scan an Egyptian artifact to reveal its name,\nhistory, and hidden meaning.",
        "begin_journey": "Begin Journey",
        "about_kemet_lens": "About Kemet Lens",
        "choose_language": "CHOOSE YOUR LANGUAGE",
        "language_subtitle": "Select how you want to explore Egypt's history.",
        "continue": "Continue",
        "artifact_scanner": "ARTIFACT SCANNER",
        "scanner_subtitle": "Place the artifact inside the frame.",
        "scanner_status": "Object detected · Ready to analyze",
        "place_artifact_here": "Place artifact here",
        "capture_artifact": "Capture Artifact",
        "processing_title": "DECODING HISTORY",
        "processing_step": "DECODING HISTORY WITH AI...",
        "processing_subtitle": "Analyzing artifact and searching the ancient\narchive.",
        "artifact_profile": "ARTIFACT PROFILE",
        "match_badge": "{confidence}% Match",
        "overview": "Overview",
        "history": "History",
        "quick_facts": "Quick Facts",
        "historical_timeline": "Historical Timeline",
        "why_it_matters": "Why It Matters",
        "did_you_know": "Did You Know?",
        "hidden_info": "Hidden Info",
        "fun_facts": "Fun Facts",
        "ask_guide_title": "Ask the Museum Guide",
        "guide_question_what": "What is this?",
        "guide_question_important": "Why is it important?",
        "guide_question_found": "Where was it found?",
        "guide_question_timeline": "Show timeline",
        "guide_question_fun": "Tell me a fun fact",
        "guide_question_symbolize": "What does it symbolize?",
        "guide_input_placeholder": "Ask about this artifact...",
        "ask_bakkar_subtitle": "Your offline Egyptian museum guide",
        "guide_ask": "Ask Bakkar",
        "guide_thinking": "Bakkar is reading the papyrus...",
        "guide_empty_answer": "Bakkar:\n\nEvery artifact has a story. Ask me what this one reveals.",
        "discover": "Discover Another Artifact",
        "home": "Home",
        "ask_bakkar": "Ask Bakkar",
        "change_language": "Change Language",
        "language": "Language",
        "recently_scanned": "Recently Scanned",
        "recent": "Recently Discovered",
        "recent_title": "RECENTLY DISCOVERED",
        "recent_subtitle": "Tap an artifact to view its profile again.",
        "recent_empty_title": "No artifacts scanned yet",
        "recent_empty_body": "Scanned artifacts will appear here after recognition.",
        "detected_choice_title": "MULTIPLE MONUMENTS DETECTED",
        "detected_choice_subtitle": "Choose the monument you want to explore from this capture.",
        "detected_choice_select": "Select Monument",
        "detected_choice_count": "{count} monuments found",
        "match": "MATCH",
        "unknown_title": "ARTIFACT NOT RECOGNIZED",
        "unknown_subtitle": "Try moving the object closer or improving the\nlighting.",
        "tip": "Tip",
        "tip_body": "Use steady lighting and keep the object\ncentered in the frame.",
        "return_home": "Return Home",
        "about_title": "ABOUT KEMET LENS",
        "about_intro": "Kemet Lens is an offline AI museum guide. It recognizes Egyptian artifacts, shows their history, and lets visitors ask Bakkar questions.",
        "how_it_works": "HOW IT WORKS",
        "features": "FEATURES",
        "camera": "Camera",
        "camera_body": "Point at artifact",
        "ai_detection": "AI Detection",
        "ai_detection_body": "Instant recognition",
        "artifact_info": "Artifact Info",
        "artifact_info_body": "Historical context",
        "guide_flow": "Ask Bakkar",
        "guide_flow_body": "Ask questions",
        "display": "Display",
        "display_body": "Rich multilingual content",
        "offline_title": "Offline operation",
        "offline_body": "Works without internet connection anywhere in the museum.",
        "ai_title": "AI-powered detection",
        "ai_body": "Advanced neural networks recognize artifacts instantly.",
        "bakkar_title": "Ask Bakkar",
        "bakkar_body": "Ask Bakkar answers visitor questions about the scanned artifact using offline multilingual knowledge files stored on the device.",
        "pi_title": "Raspberry Pi-based system",
        "pi_body": "Compact, portable hardware for any museum setup.",
        "touch_title": "Touch screen interface",
        "touch_body": "Responsive UI designed for visitors and guides.",
        "multi_title": "Multilingual support",
        "multi_body": "Explore history in English, Arabic, French, German, and Spanish.",
        "museum_title": "Museum experience",
        "museum_body": "Transforms any visit into an immersive educational journey.",
    },
    "ar": {
        "back": "رجوع",
        "brand": "عدسة كيميت",
        "splash_tagline": "أيقظ الماضي",
        "home_title": "ابدأ رحلتك\nعبر مصر القديمة",
        "home_subtitle": "امسح قطعة أثرية مصرية لتعرف اسمها\nوتاريخها ومعناها الخفي.",
        "begin_journey": "ابدأ الرحلة",
        "about_kemet_lens": "عن عدسة كيميت",
        "choose_language": "اختر لغتك",
        "language_subtitle": "اختر كيف تريد استكشاف تاريخ مصر.",
        "continue": "متابعة",
        "artifact_scanner": "ماسح القطع الأثرية",
        "scanner_subtitle": "ضع القطعة الأثرية داخل الإطار.",
        "scanner_status": "تم اكتشاف جسم · جاهز للتحليل",
        "place_artifact_here": "ضع القطعة هنا",
        "capture_artifact": "التقط القطعة الأثرية",
        "processing_title": "فك رموز التاريخ",
        "processing_step": "فك رموز التاريخ بالذكاء الاصطناعي...",
        "processing_subtitle": "يتم تحليل القطعة والبحث في\nالأرشيف القديم.",
        "artifact_profile": "ملف القطعة الأثرية",
        "match_badge": "تطابق {confidence}%",
        "overview": "نظرة عامة",
        "history": "التاريخ",
        "quick_facts": "حقائق سريعة",
        "historical_timeline": "الخط الزمني",
        "why_it_matters": "لماذا يهم",
        "did_you_know": "هل تعلم؟",
        "hidden_info": "معلومة خفية",
        "fun_facts": "حقائق ممتعة",
        "ask_guide_title": "اسأل مرشد المتحف",
        "guide_question_what": "ما هذا؟",
        "guide_question_important": "لماذا هو مهم؟",
        "guide_question_found": "أين عُثر عليه؟",
        "guide_question_timeline": "اعرض الخط الزمني",
        "guide_question_fun": "أخبرني بحقيقة ممتعة",
        "guide_question_symbolize": "ماذا يرمز؟",
        "guide_input_placeholder": "اسأل عن هذه القطعة...",
        "ask_bakkar_subtitle": "مرشدك المصري دون إنترنت",
        "guide_ask": "اسأل بكار",
        "guide_thinking": "بكار يقرأ البردية...",
        "guide_empty_answer": "بكار:\n\nلكل قطعة أثرية قصة. اسألني عمّا تكشفه هذه القطعة.",
        "discover": "اكتشف قطعة أخرى",
        "home": "الرئيسية",
        "ask_bakkar": "اسأل بكار",
        "change_language": "تغيير اللغة",
        "language": "اللغة",
        "recently_scanned": "الممسوحة حديثاً",
        "recent": "اكتشافات حديثة",
        "recent_title": "اكتشافات حديثة",
        "recent_subtitle": "اضغط على قطعة لعرض ملفها مرة أخرى.",
        "recent_empty_title": "لا توجد قطع ممسوحة بعد",
        "recent_empty_body": "ستظهر القطع هنا بعد التعرف عليها.",
        "detected_choice_title": "تم اكتشاف أكثر من أثر",
        "detected_choice_subtitle": "اختر الأثر الذي تريد معرفة معلوماته من هذه اللقطة.",
        "detected_choice_select": "اختر الأثر",
        "detected_choice_count": "تم العثور على {count} آثار",
        "match": "تطابق",
        "unknown_title": "لم يتم التعرف على القطعة",
        "unknown_subtitle": "حاول تقريب الجسم أو تحسين\nالإضاءة.",
        "tip": "نصيحة",
        "tip_body": "استخدم إضاءة ثابتة وأبقِ الجسم\nفي وسط الإطار.",
        "return_home": "العودة للرئيسية",
        "about_title": "عن عدسة كيميت",
        "about_intro": "عدسة كيميت مرشد متحف ذكي يعمل دون إنترنت. يتعرف على الآثار المصرية، يعرض تاريخها، ويتيح للزائر سؤال بكار.",
        "how_it_works": "كيف يعمل",
        "features": "المزايا",
        "camera": "الكاميرا",
        "camera_body": "وجّهها للقطعة",
        "ai_detection": "كشف ذكي",
        "ai_detection_body": "تعرف فوري",
        "artifact_info": "معلومات الأثر",
        "artifact_info_body": "سياق تاريخي",
        "guide_flow": "اسأل بكار",
        "guide_flow_body": "اسأل بحرية",
        "display": "العرض",
        "display_body": "محتوى متعدد اللغات",
        "offline_title": "عمل دون إنترنت",
        "offline_body": "يعمل في أي مكان داخل المتحف دون اتصال.",
        "ai_title": "كشف بالذكاء الاصطناعي",
        "ai_body": "شبكات عصبية متقدمة تتعرف على القطع فوراً.",
        "bakkar_title": "اسأل بكار",
        "bakkar_body": "يجيب بكار على أسئلة الزوار عن القطعة الممسوحة باستخدام ملفات معرفة متعددة اللغات مخزنة على الجهاز.",
        "pi_title": "نظام Raspberry Pi",
        "pi_body": "جهاز صغير ومحمول مناسب لأي متحف.",
        "touch_title": "واجهة لمس",
        "touch_body": "واجهة سهلة وسريعة للزوار والمرشدين.",
        "multi_title": "دعم متعدد اللغات",
        "multi_body": "استكشف التاريخ بالعربية والإنجليزية والفرنسية والألمانية والإسبانية.",
        "museum_title": "تجربة متحفية",
        "museum_body": "تحول الزيارة إلى تجربة تعليمية غامرة.",
    },
    "fr": {
        "back": "Retour",
        "brand": "KEMET LENS",
        "splash_tagline": "RÉVEILLER LE PASSÉ",
        "home_title": "COMMENCEZ VOTRE VOYAGE\nDANS L'ÉGYPTE ANCIENNE",
        "home_subtitle": "Scannez un artefact égyptien pour révéler\nson nom, son histoire et son sens caché.",
        "begin_journey": "Commencer",
        "about_kemet_lens": "À propos de Kemet Lens",
        "choose_language": "CHOISISSEZ VOTRE LANGUE",
        "language_subtitle": "Choisissez comment explorer l'histoire de l'Égypte.",
        "continue": "Continuer",
        "artifact_scanner": "SCANNER D'ARTEFACT",
        "scanner_subtitle": "Placez l'artefact dans le cadre.",
        "scanner_status": "Objet détecté · Prêt à analyser",
        "place_artifact_here": "Placez l'artefact ici",
        "capture_artifact": "Capturer l'artefact",
        "processing_title": "DÉCODAGE DE L'HISTOIRE",
        "processing_step": "DÉCODAGE AVEC L'IA...",
        "processing_subtitle": "Analyse de l'artefact et recherche dans\nles archives anciennes.",
        "artifact_profile": "PROFIL DE L'ARTEFACT",
        "match_badge": "{confidence}% Similarité",
        "overview": "Aperçu",
        "history": "Histoire",
        "quick_facts": "Faits clés",
        "historical_timeline": "Chronologie",
        "why_it_matters": "Importance",
        "did_you_know": "Le saviez-vous ?",
        "hidden_info": "Info cachée",
        "fun_facts": "Anecdotes",
        "ask_guide_title": "Demander au guide du musée",
        "guide_question_what": "Qu'est-ce que c'est ?",
        "guide_question_important": "Pourquoi est-ce important ?",
        "guide_question_found": "Où cela a-t-il été trouvé ?",
        "guide_question_timeline": "Afficher la chronologie",
        "guide_question_fun": "Racontez-moi une anecdote",
        "guide_question_symbolize": "Que symbolise-t-il ?",
        "guide_input_placeholder": "Posez une question sur cet artefact...",
        "ask_bakkar_subtitle": "Votre guide égyptien hors ligne",
        "guide_ask": "Demander à Bakkar",
        "guide_thinking": "Bakkar lit le papyrus...",
        "guide_empty_answer": "Bakkar :\n\nChaque artefact a une histoire. Demandez-moi ce que celui-ci révèle.",
        "discover": "Découvrir un autre artefact",
        "home": "Accueil",
        "ask_bakkar": "Demander à Bakkar",
        "change_language": "Changer la langue",
        "language": "Langue",
        "recently_scanned": "Scannés récemment",
        "recent": "Découvert récemment",
        "recent_title": "DÉCOUVERT RÉCEMMENT",
        "recent_subtitle": "Touchez un artefact pour revoir son profil.",
        "recent_empty_title": "Aucun artefact scanné",
        "recent_empty_body": "Les artefacts reconnus apparaîtront ici.",
        "detected_choice_title": "PLUSIEURS MONUMENTS DÉTECTÉS",
        "detected_choice_subtitle": "Choisissez le monument que vous voulez explorer dans cette capture.",
        "detected_choice_select": "Choisir le monument",
        "detected_choice_count": "{count} monuments trouvés",
        "match": "SIMILARITÉ",
        "unknown_title": "ARTEFACT NON RECONNU",
        "unknown_subtitle": "Rapprochez l'objet ou améliorez\nl'éclairage.",
        "tip": "Conseil",
        "tip_body": "Gardez une lumière stable et l'objet\nau centre du cadre.",
        "return_home": "Retour à l'accueil",
        "about_title": "À PROPOS DE KEMET LENS",
        "about_intro": "Kemet Lens est un guide de musée hors ligne. Il reconnaît les artefacts égyptiens, affiche leur histoire et permet aux visiteurs de poser des questions à Bakkar.",
    },
    "de": {
        "back": "Zurück",
        "brand": "KEMET LENS",
        "splash_tagline": "DIE VERGANGENHEIT WECKEN",
        "home_title": "BEGINNE DEINE REISE\nDURCH DAS ALTE ÄGYPTEN",
        "home_subtitle": "Scanne ein ägyptisches Artefakt, um Namen,\nGeschichte und verborgene Bedeutung zu sehen.",
        "begin_journey": "Reise beginnen",
        "about_kemet_lens": "Über Kemet Lens",
        "choose_language": "SPRACHE WÄHLEN",
        "language_subtitle": "Wähle, wie du Ägyptens Geschichte erkunden möchtest.",
        "continue": "Weiter",
        "artifact_scanner": "ARTEFAKT-SCANNER",
        "scanner_subtitle": "Platziere das Artefakt im Rahmen.",
        "scanner_status": "Objekt erkannt · Bereit zur Analyse",
        "place_artifact_here": "Artefakt hier platzieren",
        "capture_artifact": "Artefakt erfassen",
        "processing_title": "GESCHICHTE ENTSCHLÜSSELN",
        "processing_step": "GESCHICHTE MIT KI ENTSCHLÜSSELN...",
        "processing_subtitle": "Artefakt wird analysiert und im alten\nArchiv gesucht.",
        "artifact_profile": "ARTEFAKT-PROFIL",
        "match_badge": "{confidence}% Treffer",
        "overview": "Überblick",
        "history": "Geschichte",
        "quick_facts": "Kurzfakten",
        "historical_timeline": "Zeitleiste",
        "why_it_matters": "Bedeutung",
        "did_you_know": "Wusstest du?",
        "hidden_info": "Verborgene Info",
        "fun_facts": "Spannende Fakten",
        "ask_guide_title": "Museumsführer fragen",
        "guide_question_what": "Was ist das?",
        "guide_question_important": "Warum ist es wichtig?",
        "guide_question_found": "Wo wurde es gefunden?",
        "guide_question_timeline": "Zeitleiste zeigen",
        "guide_question_fun": "Erzähl mir eine spannende Tatsache",
        "guide_question_symbolize": "Was symbolisiert es?",
        "guide_input_placeholder": "Frage zu diesem Artefakt...",
        "ask_bakkar_subtitle": "Dein offline ägyptischer Museumsführer",
        "guide_ask": "Bakkar fragen",
        "guide_thinking": "Bakkar liest den Papyrus...",
        "guide_empty_answer": "Bakkar:\n\nJedes Artefakt hat eine Geschichte. Frag mich, was dieses hier verrät.",
        "discover": "Weiteres Artefakt entdecken",
        "home": "Start",
        "ask_bakkar": "Bakkar fragen",
        "change_language": "Sprache ändern",
        "language": "Sprache",
        "recently_scanned": "Zuletzt gescannt",
        "recent": "Zuletzt entdeckt",
        "recent_title": "ZULETZT ENTDECKT",
        "recent_subtitle": "Tippe auf ein Artefakt, um sein Profil zu öffnen.",
        "recent_empty_title": "Noch keine Artefakte gescannt",
        "recent_empty_body": "Erkannte Artefakte erscheinen hier.",
        "detected_choice_title": "MEHRERE MONUMENTE ERKANNT",
        "detected_choice_subtitle": "Wähle das Monument aus dieser Aufnahme, das du erkunden möchtest.",
        "detected_choice_select": "Monument wählen",
        "detected_choice_count": "{count} Monumente gefunden",
        "match": "TREFFER",
        "unknown_title": "ARTEFAKT NICHT ERKANNT",
        "unknown_subtitle": "Bewege das Objekt näher heran oder verbessere\ndie Beleuchtung.",
        "tip": "Tipp",
        "tip_body": "Nutze gleichmäßiges Licht und halte das Objekt\nin der Mitte des Rahmens.",
        "return_home": "Zurück zum Start",
        "about_title": "ÜBER KEMET LENS",
        "about_intro": "Kemet Lens ist ein Offline-Museumsführer. Er erkennt ägyptische Artefakte, zeigt ihre Geschichte und lässt Besucher Bakkar Fragen stellen.",
    },
    "es": {
        "back": "Atrás",
        "brand": "KEMET LENS",
        "splash_tagline": "DESPIERTA EL PASADO",
        "home_title": "COMIENZA TU VIAJE\nPOR EL ANTIGUO EGIPTO",
        "home_subtitle": "Escanea un artefacto egipcio para revelar\nsu nombre, historia y significado oculto.",
        "begin_journey": "Comenzar viaje",
        "about_kemet_lens": "Acerca de Kemet Lens",
        "choose_language": "ELIGE TU IDIOMA",
        "language_subtitle": "Elige cómo quieres explorar la historia de Egipto.",
        "continue": "Continuar",
        "artifact_scanner": "ESCÁNER DE ARTEFACTOS",
        "scanner_subtitle": "Coloca el artefacto dentro del marco.",
        "scanner_status": "Objeto detectado · Listo para analizar",
        "place_artifact_here": "Coloca el artefacto aquí",
        "capture_artifact": "Capturar artefacto",
        "processing_title": "DESCIFRANDO LA HISTORIA",
        "processing_step": "DESCIFRANDO CON IA...",
        "processing_subtitle": "Analizando el artefacto y buscando en\nel archivo antiguo.",
        "artifact_profile": "PERFIL DEL ARTEFACTO",
        "match_badge": "{confidence}% Coincidencia",
        "overview": "Resumen",
        "history": "Historia",
        "quick_facts": "Datos rápidos",
        "historical_timeline": "Cronología",
        "why_it_matters": "Por qué importa",
        "did_you_know": "¿Sabías que?",
        "hidden_info": "Info oculta",
        "fun_facts": "Datos curiosos",
        "ask_guide_title": "Pregunta al guía del museo",
        "guide_question_what": "¿Qué es esto?",
        "guide_question_important": "¿Por qué es importante?",
        "guide_question_found": "¿Dónde se encontró?",
        "guide_question_timeline": "Mostrar cronología",
        "guide_question_fun": "Cuéntame un dato curioso",
        "guide_question_symbolize": "¿Qué simboliza?",
        "guide_input_placeholder": "Pregunta sobre este artefacto...",
        "ask_bakkar_subtitle": "Tu guía egipcio sin conexión",
        "guide_ask": "Preguntar a Bakkar",
        "guide_thinking": "Bakkar está leyendo el papiro...",
        "guide_empty_answer": "Bakkar:\n\nCada artefacto tiene una historia. Pregúntame qué revela este.",
        "discover": "Descubrir otro artefacto",
        "home": "Inicio",
        "ask_bakkar": "Preguntar a Bakkar",
        "change_language": "Cambiar idioma",
        "language": "Idioma",
        "recently_scanned": "Escaneados recientes",
        "recent": "Descubiertos recientes",
        "recent_title": "DESCUBIERTOS RECIENTES",
        "recent_subtitle": "Toca un artefacto para ver su perfil de nuevo.",
        "recent_empty_title": "Aún no hay artefactos escaneados",
        "recent_empty_body": "Los artefactos reconocidos aparecerán aquí.",
        "detected_choice_title": "VARIOS MONUMENTOS DETECTADOS",
        "detected_choice_subtitle": "Elige el monumento que quieres explorar de esta captura.",
        "detected_choice_select": "Elegir monumento",
        "detected_choice_count": "{count} monumentos encontrados",
        "match": "COINCIDENCIA",
        "unknown_title": "ARTEFACTO NO RECONOCIDO",
        "unknown_subtitle": "Acerca el objeto o mejora\nla iluminación.",
        "tip": "Consejo",
        "tip_body": "Usa luz estable y mantén el objeto\ncentrado en el marco.",
        "return_home": "Volver al inicio",
        "about_title": "ACERCA DE KEMET LENS",
        "about_intro": "Kemet Lens es una guía de museo sin conexión. Reconoce artefactos egipcios, muestra su historia y permite a los visitantes preguntar a Bakkar.",
    },
}


for code in ("fr", "de", "es"):
    for key, value in UI["en"].items():
        UI[code].setdefault(key, value)

UI["fr"].update({
    "how_it_works": "COMMENT ÇA MARCHE",
    "features": "FONCTIONNALITÉS",
    "camera": "Caméra",
    "camera_body": "Visez l'artefact",
    "ai_detection": "Détection IA",
    "ai_detection_body": "Reconnaissance instantanée",
    "artifact_info": "Infos artefact",
    "artifact_info_body": "Contexte historique",
    "guide_flow": "Demander à Bakkar",
    "guide_flow_body": "Poser des questions",
    "display": "Affichage",
    "display_body": "Contenu multilingue",
    "offline_title": "Fonctionnement hors ligne",
    "offline_body": "Fonctionne sans connexion internet partout dans le musée.",
    "ai_title": "Détection par IA",
    "ai_body": "Des réseaux neuronaux avancés reconnaissent les artefacts instantanément.",
    "bakkar_title": "Demander à Bakkar",
    "bakkar_body": "Bakkar répond aux questions des visiteurs sur l'artefact scanné avec des fichiers de connaissances multilingues stockés sur l'appareil.",
    "pi_title": "Système Raspberry Pi",
    "pi_body": "Matériel compact et portable pour tout musée.",
    "touch_title": "Interface tactile",
    "touch_body": "Interface réactive conçue pour les visiteurs et guides.",
    "multi_title": "Support multilingue",
    "multi_body": "Explorez l'histoire en français, anglais, arabe, allemand et espagnol.",
    "museum_title": "Expérience muséale",
    "museum_body": "Transforme une visite en parcours éducatif immersif.",
})

UI["de"].update({
    "how_it_works": "SO FUNKTIONIERT ES",
    "features": "FUNKTIONEN",
    "camera": "Kamera",
    "camera_body": "Auf Artefakt richten",
    "ai_detection": "KI-Erkennung",
    "ai_detection_body": "Sofortige Erkennung",
    "artifact_info": "Artefakt-Info",
    "artifact_info_body": "Historischer Kontext",
    "guide_flow": "Bakkar fragen",
    "guide_flow_body": "Fragen stellen",
    "display": "Anzeige",
    "display_body": "Mehrsprachiger Inhalt",
    "offline_title": "Offline-Betrieb",
    "offline_body": "Funktioniert im Museum ohne Internetverbindung.",
    "ai_title": "KI-gestützte Erkennung",
    "ai_body": "Fortschrittliche neuronale Netze erkennen Artefakte sofort.",
    "bakkar_title": "Bakkar fragen",
    "bakkar_body": "Bakkar beantwortet Besucherfragen zum gescannten Artefakt mit mehrsprachigen Wissensdateien, die auf dem Gerät gespeichert sind.",
    "pi_title": "Raspberry-Pi-System",
    "pi_body": "Kompakte, portable Hardware für jedes Museum.",
    "touch_title": "Touchscreen-Oberfläche",
    "touch_body": "Intuitive Oberfläche für Besucher und Führungen.",
    "multi_title": "Mehrsprachige Unterstützung",
    "multi_body": "Geschichte auf Deutsch, Englisch, Arabisch, Französisch und Spanisch erleben.",
    "museum_title": "Museumserlebnis",
    "museum_body": "Macht den Besuch zu einer immersiven Lernerfahrung.",
})

UI["es"].update({
    "how_it_works": "CÓMO FUNCIONA",
    "features": "FUNCIONES",
    "camera": "Cámara",
    "camera_body": "Apunta al artefacto",
    "ai_detection": "Detección IA",
    "ai_detection_body": "Reconocimiento instantáneo",
    "artifact_info": "Info del artefacto",
    "artifact_info_body": "Contexto histórico",
    "guide_flow": "Preguntar a Bakkar",
    "guide_flow_body": "Hacer preguntas",
    "display": "Pantalla",
    "display_body": "Contenido multilingüe",
    "offline_title": "Funcionamiento sin conexión",
    "offline_body": "Funciona sin internet en cualquier zona del museo.",
    "ai_title": "Detección con IA",
    "ai_body": "Redes neuronales avanzadas reconocen artefactos al instante.",
    "bakkar_title": "Preguntar a Bakkar",
    "bakkar_body": "Bakkar responde a las preguntas de los visitantes sobre el artefacto escaneado usando archivos de conocimiento multilingües guardados en el dispositivo.",
    "pi_title": "Sistema Raspberry Pi",
    "pi_body": "Hardware compacto y portátil para cualquier museo.",
    "touch_title": "Interfaz táctil",
    "touch_body": "Interfaz intuitiva diseñada para visitantes y guías.",
    "multi_title": "Soporte multilingüe",
    "multi_body": "Explora la historia en español, inglés, árabe, francés y alemán.",
    "museum_title": "Experiencia de museo",
    "museum_body": "Convierte la visita en una experiencia educativa inmersiva.",
})


TAB_KEYS = {
    "Overview": "overview",
    "History": "history",
    "Quick Facts": "quick_facts",
    "Historical Timeline": "historical_timeline",
    "Why It Matters": "why_it_matters",
    "Did You Know?": "did_you_know",
    "Hidden Info": "hidden_info",
    "Fun Facts": "fun_facts",
}


ARTIFACT_TEXT = {
    "ar": {
        "tutankhamun": {
            "display_name": "توت عنخ آمون",
            "short_description": "فرعون شاب من الأسرة الثامنة عشرة، اشتهر بقبره شبه السليم وقناعه الذهبي.",
            "overview": "كان توت عنخ آمون فرعوناً مصرياً من الأسرة الثامنة عشرة في عصر الدولة الحديثة، وأصبح مشهوراً بسبب حفظ مقبرته الملكية بصورة استثنائية.",
            "history": "تولى الحكم نحو 1332 ق.م في سن صغيرة. كان حكمه قصيراً، لكن اكتشاف مقبرته عام 1922 جعله من أهم رموز علم المصريات.",
            "why": "قبره من أكمل المدافن الملكية المكتشفة، ويكشف كثيراً عن الفن والطقوس والحياة اليومية في الدولة الحديثة.",
            "did_you_know": "يزن قناعه الذهبي نحو 11 كيلوجراماً من الذهب الخالص.",
            "hidden_info": "أظهرت الفحوص الطبية كسراً في ساقه ومؤشرات مرضية ربما ساهمت في وفاته المبكرة.",
            "fun_facts": "احتوى قبره على أكثر من 5000 قطعة أثرية، منها عربات ومجوهرات وألعاب وأسرة مذهبة.",
            "quick_facts": (("العصر", "الدولة الحديثة"), ("الأسرة", "الثامنة عشرة"), ("المادة", "ذهب، خشب، حجر، كتان"), ("اشتهر بـ", "القبر الملكي والقناع الذهبي"), ("الموقع", "وادي الملوك، الأقصر")),
            "timeline": (("1332 ق.م", "أصبح فرعوناً في سن التاسعة"), ("1323 ق.م", "توفي ودُفن في وادي الملوك"), ("1922 م", "اكتشف هوارد كارتر المقبرة")),
        },
        "nefertiti": {"display_name": "نفرتيتي", "short_description": "الزوجة الملكية الكبرى لأخناتون، اشتهرت بتمثالها النصفي ونفوذها السياسي."},
        "pyramids_of_giza": {"display_name": "أهرامات الجيزة", "short_description": "آخر عجائب العالم القديم الباقية، شُيدت كمقابر ملكية ضخمة على هضبة الجيزة."},
        "ramses_ii": {"display_name": "رمسيس الثاني", "short_description": "فرعون قوي من الدولة الحديثة اشتهر بالمعابد والتماثيل الضخمة وطول فترة حكمه."},
        "anubis": {"display_name": "أنوبيس", "short_description": "الإله ذو رأس ابن آوى، ارتبط بالتحنيط وحماية المقابر ووزن القلب."},
    },
    "fr": {
        "tutankhamun": {
            "display_name": "Toutânkhamon",
            "short_description": "Jeune pharaon de la 18e dynastie, célèbre pour sa tombe presque intacte et son masque d'or.",
            "overview": "Toutânkhamon fut un pharaon égyptien de la 18e dynastie, durant le Nouvel Empire. Sa tombe a conservé un exceptionnel ensemble funéraire royal.",
            "history": "Il monta sur le trône vers 1332 av. J.-C. Son règne fut court, mais la découverte de sa tombe en 1922 transforma l'égyptologie.",
            "why": "Sa tombe offre un aperçu rare de l'art, des rituels et de la vie quotidienne du Nouvel Empire.",
            "did_you_know": "Son masque funéraire pèse environ 11 kilogrammes d'or massif.",
            "hidden_info": "Des examens médicaux ont révélé une jambe cassée et des signes de maladie.",
            "fun_facts": "La tombe contenait plus de 5 000 objets, dont des chars, bijoux, jeux et lits dorés.",
            "quick_facts": (("Ère", "Nouvel Empire"), ("Dynastie", "18e dynastie"), ("Matière", "Or, bois, pierre, lin"), ("Célèbre pour", "Tombe royale et masque d'or"), ("Lieu", "Vallée des Rois, Louxor")),
            "timeline": (("1332 av. J.-C.", "Devient pharaon vers 9 ans"), ("1323 av. J.-C.", "Meurt et est enterré dans la Vallée des Rois"), ("1922", "Tombe découverte par Howard Carter")),
        },
        "nefertiti": {"display_name": "Néfertiti", "short_description": "Grande épouse royale d'Akhenaton, connue pour son buste iconique et son influence."},
        "pyramids_of_giza": {"display_name": "Pyramides de Gizeh", "short_description": "Dernière merveille antique encore debout, construite comme tombe royale monumentale."},
        "ramses_ii": {"display_name": "Ramsès II", "short_description": "Puissant pharaon du Nouvel Empire, célèbre pour ses temples, statues colossales et long règne."},
        "anubis": {"display_name": "Anubis", "short_description": "Dieu à tête de chacal associé à la momification, aux tombes et au jugement du cœur."},
    },
    "de": {
        "tutankhamun": {
            "display_name": "Tutanchamun",
            "short_description": "Junger Pharao der 18. Dynastie, berühmt für sein fast unversehrtes Grab und die goldene Maske.",
            "overview": "Tutanchamun war ein ägyptischer Pharao der 18. Dynastie im Neuen Reich. Sein außergewöhnlich erhaltenes Grab machte ihn weltberühmt.",
            "history": "Er bestieg den Thron um 1332 v. Chr. in sehr jungen Jahren. Sein kurzes Leben wurde durch die Entdeckung des Grabes 1922 zu einem Schlüsselthema der Ägyptologie.",
            "why": "Das Grab bietet einen selten vollständigen Blick auf Kunst, Ritual und Alltag des Neuen Reiches.",
            "did_you_know": "Seine goldene Totenmaske wiegt ungefähr 11 Kilogramm massives Gold.",
            "hidden_info": "Medizinische Untersuchungen zeigten einen Beinbruch und Hinweise auf Krankheit.",
            "fun_facts": "Im Grab lagen über 5.000 Objekte, darunter Wagen, Schmuck, Spiele und vergoldete Möbel.",
            "quick_facts": (("Epoche", "Neues Reich"), ("Dynastie", "18. Dynastie"), ("Material", "Gold, Holz, Stein, Leinen"), ("Berühmt für", "Königsgrab und Goldmaske"), ("Ort", "Tal der Könige, Luxor")),
            "timeline": (("1332 v. Chr.", "Wurde mit etwa 9 Jahren Pharao"), ("1323 v. Chr.", "Starb und wurde im Tal der Könige bestattet"), ("1922", "Grab von Howard Carter entdeckt")),
        },
        "nefertiti": {"display_name": "Nofretete", "short_description": "Große königliche Gemahlin Echnatons, bekannt für ihre Büste und ihren Einfluss."},
        "pyramids_of_giza": {"display_name": "Pyramiden von Gizeh", "short_description": "Das letzte erhaltene Weltwunder der Antike, erbaut als monumentale Königsgräber."},
        "ramses_ii": {"display_name": "Ramses II.", "short_description": "Mächtiger Pharao des Neuen Reiches, bekannt für Tempel, Kolossalstatuen und eine lange Herrschaft."},
        "anubis": {"display_name": "Anubis", "short_description": "Schakalköpfiger Gott der Mumifizierung, Grabwache und Herzenswägung."},
    },
    "es": {
        "tutankhamun": {
            "display_name": "Tutankamón",
            "short_description": "Joven faraón de la dinastía XVIII, famoso por su tumba casi intacta y su máscara dorada.",
            "overview": "Tutankamón fue un faraón egipcio de la dinastía XVIII durante el Reino Nuevo. Su tumba conservó un extraordinario entierro real.",
            "history": "Subió al trono hacia 1332 a. C. siendo muy joven. Su reinado fue breve, pero el descubrimiento de su tumba en 1922 cambió la egiptología.",
            "why": "Su tumba ofrece una visión excepcional del arte, los rituales y la vida diaria del Reino Nuevo.",
            "did_you_know": "Su máscara funeraria pesa aproximadamente 11 kilogramos de oro macizo.",
            "hidden_info": "Los estudios médicos revelaron una pierna rota y señales de enfermedad.",
            "fun_facts": "La tumba contenía más de 5.000 objetos, incluidos carros, joyas, juegos y muebles dorados.",
            "quick_facts": (("Época", "Reino Nuevo"), ("Dinastía", "Dinastía XVIII"), ("Material", "Oro, madera, piedra, lino"), ("Famoso por", "Tumba real y máscara dorada"), ("Ubicación", "Valle de los Reyes, Luxor")),
            "timeline": (("1332 a. C.", "Se convirtió en faraón hacia los 9 años"), ("1323 a. C.", "Murió y fue enterrado en el Valle de los Reyes"), ("1922", "Howard Carter descubrió la tumba")),
        },
        "nefertiti": {"display_name": "Nefertiti", "short_description": "Gran esposa real de Akenatón, recordada por su busto icónico y su influencia política."},
        "pyramids_of_giza": {"display_name": "Pirámides de Guiza", "short_description": "La última maravilla del mundo antiguo, construida como tumbas reales monumentales."},
        "ramses_ii": {"display_name": "Ramsés II", "short_description": "Poderoso faraón del Reino Nuevo, famoso por templos, estatuas colosales y un largo reinado."},
        "anubis": {"display_name": "Anubis", "short_description": "Dios con cabeza de chacal asociado con momificación, tumbas y el pesaje del corazón."},
    },
}


KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
KNOWLEDGE_SECTIONS = {
    "SHORT DESCRIPTION": "short_description",
    "OVERVIEW": "overview",
    "HISTORY": "history",
    "HISTORICAL BACKGROUND": "history",
    "QUICK FACTS": "quick_facts",
    "HISTORICAL TIMELINE": "timeline",
    "TIMELINE": "timeline",
    "WHY IT MATTERS": "why",
    "DID YOU KNOW?": "did_you_know",
    "HIDDEN INFO": "hidden_info",
    "HIDDEN INFO.": "hidden_info",
    "HIDDEN DETAIL": "hidden_info",
    "FUN FACTS": "fun_facts",
}


def _section_heading(line: str) -> tuple[str, str] | tuple[None, None]:
    upper_line = line.upper().strip()
    if upper_line in KNOWLEDGE_SECTIONS:
        return KNOWLEDGE_SECTIONS[upper_line], ""

    for heading, key in sorted(KNOWLEDGE_SECTIONS.items(), key=lambda item: len(item[0]), reverse=True):
        prefix = f"{heading}:"
        if upper_line.startswith(prefix):
            return key, line[len(prefix):].strip()
    return None, None


def _parse_lines_as_pairs(value: str, *, timeline: bool = False) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for raw_line in value.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        if timeline:
            date_split = re.split(r"\s{2,}", line, maxsplit=1)
            if len(date_split) == 2:
                pairs.append((date_split[0].strip(), date_split[1].strip()))
                continue
        item = line.strip()
        if not item:
            continue
        if ":" in item:
            label, detail = item.split(":", 1)
            pairs.append((label.strip(), detail.strip()))
        else:
            pairs.append(("", item))
    return tuple(pairs)


@lru_cache(maxsize=None)
def _knowledge_artifact(language: str, artifact_key: str) -> dict:
    file_path = KNOWLEDGE_DIR / language / f"{artifact_key}.txt"
    if not file_path.exists():
        return {}

    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    metadata: dict[str, str] = {}

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        upper_line = line.upper()

        if ":" in line and current_section is None:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()

        section_key, section_subtitle = _section_heading(line)
        if section_key:
            current_section = section_key
            sections.setdefault(current_section, [])
            if section_subtitle:
                sections[current_section].append(section_subtitle)
            continue

        if upper_line.startswith("COMMON USER QUESTIONS") or upper_line.startswith("EXTRA CHATBOT"):
            current_section = None
            continue

        if current_section:
            sections[current_section].append(raw_line)

    parsed: dict[str, object] = {}
    if metadata.get("display name"):
        parsed["display_name"] = metadata["display name"]

    for key, lines in sections.items():
        value = "\n".join(lines).strip()
        if not value:
            continue
        if key in {"quick_facts", "timeline"}:
            parsed[key] = _parse_lines_as_pairs(value, timeline=key == "timeline")
        else:
            parsed[key] = value
    return parsed


def text(language: str, key: str, **kwargs) -> str:
    value = UI.get(language, UI["en"]).get(key, UI["en"].get(key, key))
    return value.format(**kwargs) if kwargs else value


def tab_label(language: str, tab: str) -> str:
    return text(language, TAB_KEYS.get(tab, tab))


def _joined_items(items: list[str]) -> str:
    return "\n\n".join(item for item in items if item)


def _joined_titled_items(items: list[dict[str, str]]) -> str:
    blocks = []
    for item in items:
        title = item.get("title", "").strip()
        body = item.get("text", "").strip()
        blocks.append(f"{title}\n\n{body}" if title else body)
    return "\n\n".join(block for block in blocks if block)


def _pairs_from_dicts(items: list[dict[str, str]], label_key: str, value_key: str) -> tuple[tuple[str, str], ...]:
    return tuple((item.get(label_key, ""), item.get(value_key, "")) for item in items)


def artifact_text(language: str, artifact) -> dict:
    content = ARTIFACT_CONTENT.get(language, {}).get(artifact.key)
    if content is None:
        content = ARTIFACT_CONTENT.get("en", {}).get(artifact.key)

    if content is None:
        content = {
            "display_name": artifact.display_name,
            "short_description": artifact.short_description,
            "overview": artifact.overview,
            "history": artifact.history,
            "quick_facts": [{"label": label, "value": value} for label, value in artifact.quick_facts],
            "timeline": [{"date": date, "event": event} for date, event in artifact.timeline],
            "why_it_matters": [{"title": "", "text": artifact.why}],
            "did_you_know": [artifact.did_you_know],
            "hidden_info": [artifact.hidden_info],
            "fun_facts": [artifact.fun_facts],
        }

    quick_facts = list(content["quick_facts"])
    timeline = list(content["timeline"])
    why_it_matters = list(content["why_it_matters"])
    did_you_know = list(content["did_you_know"])
    hidden_info = list(content["hidden_info"])
    fun_facts = list(content["fun_facts"])

    return {
        "display_name": content["display_name"],
        "short_description": content["short_description"],
        "overview": content["overview"],
        "history": content["history"],
        "quick_facts": quick_facts,
        "timeline": timeline,
        "why_it_matters": why_it_matters,
        "did_you_know": did_you_know,
        "hidden_info": hidden_info,
        "fun_facts": fun_facts,
        "quick_facts_pairs": _pairs_from_dicts(quick_facts, "label", "value"),
        "timeline_pairs": _pairs_from_dicts(timeline, "date", "event"),
        "why": _joined_titled_items(why_it_matters),
        "did_you_know_text": _joined_items(did_you_know),
        "hidden_info_text": _joined_items(hidden_info),
        "fun_facts_text": _joined_items(fun_facts),
    }
