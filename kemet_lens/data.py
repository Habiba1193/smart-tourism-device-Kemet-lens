from __future__ import annotations

from dataclasses import dataclass


TAB_NAMES = [
    "Overview",
    "History",
    "Quick Facts",
    "Historical Timeline",
    "Why It Matters",
    "Did You Know?",
    "Hidden Info",
    "Fun Facts",
]


@dataclass(frozen=True)
class Artifact:
    key: str
    display_name: str
    image: str
    thumbnail: str
    default_confidence: int
    short_description: str
    overview: str
    history: str
    quick_facts: tuple[tuple[str, str], ...]
    timeline: tuple[tuple[str, str], ...]
    why: str
    did_you_know: str
    hidden_info: str
    fun_facts: str


ARTIFACTS: dict[str, Artifact] = {
    "tutankhamun": Artifact(
        key="tutankhamun",
        display_name="Tutankhamun",
        image="artifacts/tutankhamun.png",
        thumbnail="thumbnails/tutankhamun.png",
        default_confidence=93,
        short_description=(
            "The Boy King whose nearly intact tomb and golden death mask became the "
            "face of ancient Egypt."
        ),
        overview=(
            "Tutankhamun — The Boy King\n\n"
            "Tutankhamun became pharaoh at roughly age 9 and died at around 18–19, "
            "making him one of the most obscure rulers of his era — yet today he is "
            "arguably the most famous Egyptian pharaoh in the world. The reason? In "
            "1922, British archaeologist Howard Carter discovered his nearly intact "
            "tomb in the Valley of the Kings, packed with over 5,000 treasures that "
            "had been sealed for 3,300 years. His golden death mask has become the "
            "face of ancient Egypt."
        ),
        history=(
            "Reign & rediscovery\n\n"
            "Born around 1341 BCE, likely as the son of the controversial Akhenaten, "
            "Tutankhamun (\"living image of Amun\") reversed his father's radical "
            "religious reforms, restored traditional Egyptian polytheism, and moved "
            "the capital back to Thebes. His short reign was guided by two powerful "
            "advisors: the vizier Ay and the general Horemheb. He died unexpectedly "
            "young — the cause still debated. His tomb was sealed, forgotten, and "
            "then built over, which ironically preserved it from the ancient grave "
            "robbers who looted almost every other royal tomb."
        ),
        quick_facts=(
            ("Age", "Became pharaoh at ~9 years old; died at ~18–19"),
            ("Birth name", "Tutankhaten, meaning \"living image of Aten\""),
            ("Tomb", "KV62 contained 5,398 individual artifacts"),
            ("Death mask", "Solid gold mask weighs 10.23 kg (22.5 lbs)"),
            ("DNA", "Shows sibling inbreeding, a common royal practice"),
            ("Health", "Had a club foot and required walking sticks; 130 were found in his tomb"),
        ),
        timeline=(
            ("~1341 BCE", "Born — son of Akhenaten, likely with a sister-wife"),
            ("~1332 BCE", "Becomes pharaoh at ~9 years old; changes name to Tutankhamun"),
            ("~1332 BCE", "Restores traditional religion; moves capital back to Thebes"),
            ("~1323 BCE", "Dies suddenly at ~18–19; buried hastily in a small tomb"),
            ("1922 CE", "Howard Carter discovers KV62 — \"wonderful things\" inside"),
            ("2022 CE", "Treasures move to new Grand Egyptian Museum near Giza"),
        ),
        why=(
            "A time capsule from 1323 BCE\n\n"
            "Because his tomb was sealed and forgotten, it gives us an unparalleled "
            "snapshot of royal Egyptian material culture — what pharaohs wore, ate, "
            "owned, and valued. Almost no other royal tomb survived undisturbed.\n\n"
            "The Amarna aftermath\n\n"
            "Tut's reign is a crucial transitional chapter — showing how a civilization "
            "dismantles a failed revolution and reassembles its cultural identity. It's "
            "a story about religious resilience and political survival."
        ),
        did_you_know=(
            "When Howard Carter first peered through a small hole into the tomb with a "
            "candle on November 26, 1922, his patron Lord Carnarvon asked \"Can you see "
            "anything?\" Carter reportedly replied: \"Yes — wonderful things.\" It remains "
            "one of history's most understated responses to a discovery.\n\n"
            "Tutankhamun was buried with a dagger made of meteorite iron — an incredibly "
            "rare and precious material in the Bronze Age. Chemical analysis confirmed "
            "the iron came from space. He was literally buried with a knife from the stars."
        ),
        hidden_info=(
            "Tut's tomb appears to have been prepared and decorated in great haste — "
            "likely because he died unexpectedly young. Some of the painted murals were "
            "still wet when the tomb was sealed. His mummy shows signs of a leg fracture "
            "shortly before death, fueling theories of an accident or even murder.\n\n"
            "Among the tomb's contents was a linen shirt — one of the world's oldest "
            "surviving garments. Also found: his childhood lock of hair, a pair of his "
            "sandals, and a boomerang. The boy king apparently enjoyed hunting games."
        ),
        fun_facts=(
            "The \"Curse of the Pharaohs\" began when Lord Carnarvon died 5 months after "
            "the tomb opened, from an infected mosquito bite. Headlines exploded. In "
            "reality, studies show the 58 people present at the opening had normal or "
            "above-average lifespans. Howard Carter, the main \"curse victim,\" lived "
            "another 17 years.\n\n"
            "Tut's innermost coffin — the one holding his mummy — is made of solid gold "
            "and weighs 110.4 kg. It is the single most valuable object ever found in an "
            "Egyptian tomb and remains inside KV62's sarcophagus to this day, too fragile "
            "to move."
        ),
    ),
    "nefertiti": Artifact(
        key="nefertiti",
        display_name="Nefertiti",
        image="artifacts/nefertiti.png",
        thumbnail="thumbnails/nefertiti.png",
        default_confidence=88,
        short_description=(
            "The Beautiful One, principal wife of Akhenaten and a powerful queen of the Amarna Period."
        ),
        overview=(
            "Nefertiti — The Beautiful One\n\n"
            "Queen Nefertiti (~1370–1330 BCE) was the principal wife of the "
            "\"heretic pharaoh\" Akhenaten and one of the most powerful women in "
            "Egyptian history. She co-ruled during the radical Amarna Period, when "
            "Egypt's ancient polytheistic religion was temporarily abolished in "
            "favour of worshipping a single sun deity — Aten. Her painted limestone "
            "bust, discovered in 1912, is among the most recognized artworks ever created."
        ),
        history=(
            "The Amarna revolution\n\n"
            "Nefertiti rose alongside her husband Akhenaten, who moved Egypt's "
            "capital from Thebes to a new city called Akhetaten (modern Amarna). "
            "Together they dismantled the powerful priestly class of Amun, "
            "redistributed their wealth to the crown, and forced a new religion on "
            "a deeply traditional civilization. Nefertiti appears in temple art "
            "performing religious rites typically reserved for pharaohs — an "
            "extraordinary elevation of queenly power."
        ),
        quick_facts=(
            ("Name meaning", "\"A beautiful woman has come\" in ancient Egyptian"),
            ("Origins", "Unknown — possibly a foreign princess or Egyptian noblewoman"),
            ("Children", "Had six daughters with Akhenaten; no confirmed sons"),
            ("Bust", "Sculpted by royal artist Thutmose around 1345 BCE"),
            ("After Akhenaten", "Vanishes from records — possibly ruled as pharaoh"),
            ("Tomb", "Her tomb has never been definitively found"),
        ),
        timeline=(
            ("~1370 BCE", "Likely birth period of Nefertiti"),
            ("~1353 BCE", "Akhenaten rises; Nefertiti becomes central to royal power"),
            ("~1345 BCE", "Her famous bust is sculpted by Thutmose"),
            ("~1330 BCE", "After Akhenaten's death, she vanishes from records"),
            ("1912 AD", "Nefertiti's painted limestone bust is discovered"),
            ("1913 AD", "The bust is taken to Germany, where it remains contested"),
        ),
        why=(
            "Proto-monotheism\n\n"
            "The Amarna Period under Nefertiti and Akhenaten represents one of the "
            "earliest known attempts at monotheistic religion in human history — "
            "potentially influencing later Abrahamic faiths through the Hebrew "
            "people's time in Egypt.\n\n"
            "Women and power in antiquity\n\n"
            "Nefertiti's near-pharaonic status challenges assumptions about gender "
            "and power in the ancient world. She is evidence that women wielded "
            "real political and religious authority 3,300 years ago."
        ),
        did_you_know=(
            "The famous Nefertiti bust has only one inlaid eye — the left eye "
            "socket is empty. The sculptor Thutmose may have never completed it, "
            "or the eye could have been removed. Some believe it was a model used "
            "in the workshop rather than a finished piece for display.\n\n"
            "Germany has held the bust since 1913. Egypt has repeatedly demanded "
            "its return, arguing it was smuggled out illegally. The bust sits in "
            "Berlin's Neues Museum and is one of the most contested museum pieces "
            "in the world."
        ),
        hidden_info=(
            "Some Egyptologists believe Nefertiti became pharaoh herself after "
            "Akhenaten's death under the name \"Neferneferuaten\" — and may have "
            "even been the direct predecessor to Tutankhamun, effectively ruling "
            "Egypt as a woman pharaoh for several years.\n\n"
            "In 2015, British Egyptologist Nicholas Reeves proposed that Nefertiti's "
            "tomb might be hidden behind a secret sealed door in Tutankhamun's tomb "
            "in the Valley of the Kings. Radar scans suggested anomalies, but "
            "subsequent investigations have been inconclusive."
        ),
        fun_facts=(
            "When Borchardt's team excavated Nefertiti's bust in 1912, he reportedly "
            "described it in the expedition log as merely a \"coloured plaster bust "
            "of a princess\" — widely suspected to be deliberate misdescription to "
            "smuggle it out of Egypt without proper scrutiny.\n\n"
            "The Amarna art style that flourished under Nefertiti and Akhenaten was "
            "shockingly naturalistic compared to traditional Egyptian art — showing "
            "the royal family in relaxed, intimate poses, even playing with their "
            "daughters. It was an artistic revolution that vanished almost as quickly "
            "as it appeared."
        ),
    ),
    "pyramids_of_giza": Artifact(
        key="pyramids_of_giza",
        display_name="Pyramids of Giza",
        image="artifacts/great_pyramid.jpeg",
        thumbnail="thumbnails/great_pyramid.jpeg",
        default_confidence=91,
        short_description=(
            "The only surviving wonder of the ancient Seven Wonders, standing as a "
            "testament to Old Kingdom engineering genius."
        ),
        overview=(
            "The Pyramids of Giza\n\n"
            "The Great Pyramid of Khufu, completed around 2560 BCE, is the only surviving "
            "wonder of the ancient Seven Wonders of the World — and for good reason. "
            "Three pyramids dominate the Giza plateau: Khufu (the largest), Khafre, and "
            "Menkaure. Together with the Great Sphinx, they form one of the most studied "
            "and debated complexes in human history, standing as testament to the "
            "organizational, mathematical, and engineering genius of the Old Kingdom Egyptians."
        ),
        history=(
            "Construction & purpose\n\n"
            "Pyramid building reached its peak during the Old Kingdom (2686–2181 BCE). "
            "The Giza pyramids were royal tombs designed to launch the pharaoh's soul into "
            "eternal life and align with the stars of Orion's belt — the constellation "
            "associated with Osiris. Construction involved tens of thousands of workers, a "
            "sophisticated supply chain, and precise astronomical and mathematical knowledge. "
            "Workers were paid laborers — not slaves — who received food, healthcare, and "
            "even sick leave."
        ),
        quick_facts=(
            ("Great Pyramid", "Originally 146.6 m tall — tallest structure on Earth for 3,800 years"),
            ("Stone blocks", "Built from ~2.3 million blocks, each 2.5–15 tonnes"),
            ("Original surface", "Smooth polished white limestone that gleamed brilliantly"),
            ("Temperature", "Internal temperature stays at about 20°C regardless of outside weather"),
            ("Level base", "Base is level to within 2.1 centimetres across 230 metres"),
            ("Alignment", "Aligned with true north to within 3/60 of a degree"),
        ),
        timeline=(
            ("~2630 BCE", "Step Pyramid of Djoser built at Saqqara — Egypt's first pyramid"),
            ("~2575 BCE", "Sneferu builds the Bent Pyramid and Red Pyramid — first true smooth-sided pyramids"),
            ("~2560 BCE", "Great Pyramid of Khufu completed at Giza"),
            ("~2530 BCE", "Khafre's pyramid and the Great Sphinx constructed"),
            ("~2510 BCE", "Menkaure's pyramid completes the Giza trio"),
            ("1300s CE", "White limestone casing stripped for building Cairo's mosques and fortresses"),
        ),
        why=(
            "Engineering that defies time\n\n"
            "The pyramids demonstrate that 4,600 years ago, humans could plan, organize, "
            "and execute megaprojects requiring precision mathematics, logistics, and "
            "thousands of coordinated workers — systems we recognize as modern project "
            "management.\n\n"
            "Window into ancient religion\n\n"
            "The pyramids encode Egypt's entire cosmology — the afterlife, the stars, "
            "the sun's journey. Understanding them means understanding how millions of "
            "people answered the question of what happens after death."
        ),
        did_you_know=(
            "The Great Pyramid was originally encased in brilliant white Tura limestone, "
            "making it gleam in the sun and possibly visible from the Mediterranean. The "
            "smooth casing stones were stripped away in the 14th century CE to build Cairo "
            "— the rough stepped appearance we see today is actually the exposed core.\n\n"
            "In 2017, scientists using cosmic-ray muon detectors, like an X-ray for "
            "buildings, discovered a previously unknown large void — at least 30 metres "
            "long — hidden inside the Great Pyramid. Nobody knows what it is or what it contains."
        ),
        hidden_info=(
            "Graffiti found in hidden chambers inside the Great Pyramid — written by the "
            "construction workers — reads \"friends of Khufu\" and other crew names. These "
            "workers were proud of their achievement and tagged their work like any modern "
            "construction crew.\n\n"
            "The Sphinx almost certainly had a beard and a royal uraeus, or cobra, on its "
            "forehead — fragments were found nearby. It was also painted in vivid colors: "
            "red face, yellow and blue body. The austere grey monolith we see today looks "
            "nothing like the original."
        ),
        fun_facts=(
            "The Great Pyramid's perimeter divided by twice its height gives you a number "
            "extremely close to pi (3.14159...). Whether this was intentional or a "
            "coincidence of using a wheel to measure distance is one of archaeology's most "
            "delightful unanswered questions.\n\n"
            "If you disassembled the Great Pyramid and built a wall 1 metre thick by 3 "
            "metres tall, it would stretch all the way around France. Napoleon reportedly "
            "calculated that the stones from all three Giza pyramids could build a wall "
            "around France — and checked the math himself."
        ),
    ),
    "ramses_ii": Artifact(
        key="ramses_ii",
        display_name="Ramesses II",
        image="artifacts/ramses_ii.png",
        thumbnail="thumbnails/ramses_ii.png",
        default_confidence=89,
        short_description=(
            "The Great pharaoh, warrior, builder, diplomat, and master of royal propaganda."
        ),
        overview=(
            "Ramesses II — The Great\n\n"
            "Ruling Egypt for approximately 66 years (1279–1213 BCE), Ramesses II "
            "is considered the mightiest pharaoh of the New Kingdom and perhaps "
            "all of ancient Egypt. A warrior, builder, diplomat, and self-promoter "
            "of extraordinary scale, he reshaped Egypt's landscape with monuments "
            "and left his name on every surface he could find — including monuments "
            "he didn't actually build."
        ),
        history=(
            "Reign & legacy\n\n"
            "Ramesses came to power at around 25 and ruled until his death at "
            "roughly 90. He led Egypt's military into the Levant, Nubia, and Libya. "
            "His most famous campaign — the Battle of Kadesh against the Hittites "
            "(~1274 BCE) — ended in a diplomatic stalemate, but he depicted it as "
            "a glorious personal victory on temple walls across Egypt. The resulting "
            "peace treaty is one of the oldest surviving international agreements."
        ),
        quick_facts=(
            ("Reign", "~66 years — the second longest pharaoh reign in history"),
            ("Children", "Had over 100 children by multiple wives and concubines"),
            ("Monuments", "Built or expanded more monuments than any other pharaoh"),
            ("Abu Simbel", "Commissioned temples with four 20-metre statues of himself"),
            ("Mummy", "Shows arthritis, dental decay, and evidence of old battle wounds"),
            ("Hair", "His red hair was preserved — a rare trait in ancient Egypt"),
        ),
        timeline=(
            ("~1303 BCE", "Born, son of Pharaoh Seti I and Queen Tuya"),
            ("~1279 BCE", "Becomes pharaoh at ~24 years old"),
            ("~1274 BCE", "Battle of Kadesh against the Hittites — the largest chariot battle in history"),
            ("~1258 BCE", "Signing of the Egypt–Hittite peace treaty, the earliest known international treaty"),
            ("~1244 BCE", "Abu Simbel temples completed"),
            ("~1213 BCE", "Dies at ~90 years old after a 66-year reign"),
        ),
        why=(
            "First peace treaty in history\n\n"
            "The treaty with the Hittites established the concept of international "
            "diplomacy — that great powers could negotiate rather than annihilate. "
            "A replica hangs in the United Nations building in New York today.\n\n"
            "Master of propaganda\n\n"
            "Ramesses pioneered state-sponsored narrative control. He plastered his "
            "face and victories on every temple, creating the template for how rulers "
            "project power through architecture and image — still practiced today."
        ),
        did_you_know=(
            "Ramesses II was so prolific at usurping existing monuments — carving "
            "his name over predecessors' names — that future pharaohs had to carve "
            "his inscriptions extra deep so no one could erase them without destroying "
            "the stone.\n\n"
            "When his mummy was flown to France in 1976 for conservation, it was "
            "officially issued an Egyptian passport — listing his occupation as "
            "\"King (deceased).\" He received a full head-of-state welcome at Paris airport."
        ),
        hidden_info=(
            "Ramesses actually retreated and nearly lost the Battle of Kadesh — the "
            "Hittites ambushed his forces and almost captured him. His \"glorious "
            "victory\" was essentially a propaganda fabrication. The real outcome "
            "was a draw.\n\n"
            "DNA and medical analysis of his mummy revealed he likely suffered from "
            "severe atherosclerosis, and his teeth were so worn down from a lifetime "
            "of eating grit-contaminated bread that he must have been in near-constant "
            "pain in his later years."
        ),
        fun_facts=(
            "Abu Simbel was engineered so that twice a year — on February 22 and "
            "October 22, believed to be Ramesses' birthday and coronation day — "
            "sunlight penetrates 60 metres into the mountain to illuminate three "
            "of the four inner statues. The fourth, Ptah, god of darkness, stays dark.\n\n"
            "When the Aswan Dam was built in the 1960s, the entire Abu Simbel temple "
            "complex was cut into pieces and relocated 65 metres uphill and 200 metres "
            "back — one of the greatest engineering feats of the 20th century. UNESCO "
            "moved an ancient wonder to save it from modern progress."
        ),
    ),
    "anubis": Artifact(
        key="anubis",
        display_name="Anubis",
        image="artifacts/anubis.png",
        thumbnail="thumbnails/anubis.png",
        default_confidence=86,
        short_description=(
            "Guardian of the dead, god of death, embalming, and the afterlife."
        ),
        overview=(
            "Anubis — Guardian of the Dead\n\n"
            "Anubis is one of ancient Egypt's oldest and most iconic deities, "
            "worshipped as the god of death, embalming, and the afterlife. He "
            "appears as a man with the black head of a jackal — a creature "
            "associated with cemeteries since jackals were commonly seen near "
            "burial grounds. He presided over the sacred Weighing of the Heart "
            "ceremony, the ultimate judgment of every soul."
        ),
        history=(
            "Origins & evolution\n\n"
            "Anubis was Egypt's primary god of the dead from the Old Kingdom "
            "(~2686 BCE) until the Middle Kingdom, when Osiris gradually took "
            "his role. His cult center was at Cynopolis (\"City of the Dog\"). "
            "He was believed to be the son of Osiris and Nephthys, raised in "
            "secret. Over time, his role shifted from ruler of the underworld "
            "to its divine embalmer and protector of graves."
        ),
        quick_facts=(
            ("Name meaning", "\"Royal child\" or linked to the word for \"decay\""),
            ("Depiction", "Jackal-headed man or a full black jackal"),
            ("Black color", "Fertility, rebirth, and the Nile's soil — not evil"),
            ("Embalming myth", "He mummified Osiris after his murder"),
            ("Ritual masks", "Priests wore Anubis masks during burial rituals"),
            ("Other title", "Also called \"Imy-ut\" — \"he who is in the place of embalming\""),
        ),
        timeline=(
            ("~3100 BCE", "First Dynasty: Anubis appears as the primary god of the dead"),
            ("~2686 BCE", "Old Kingdom: Anubis cult at its peak, featured in Pyramid Texts"),
            ("~2055 BCE", "Middle Kingdom: Osiris rises; Anubis becomes embalmer and guide"),
            ("~1550 BCE", "New Kingdom: Book of the Dead codifies the Weighing of the Heart ceremony"),
            ("~30 BCE", "Roman era: Anubis absorbed into Greco-Roman religion as \"Hermanubis\""),
        ),
        why=(
            "Blueprint for the afterlife\n\n"
            "Anubis gave ancient Egyptians a framework for death — a moral "
            "universe where your deeds in life determined your fate. The "
            "Weighing of the Heart is essentially an ancient concept of divine "
            "justice.\n\n"
            "Origin of mummification\n\n"
            "His mythology legitimized and sacralized the entire practice of "
            "embalming, preserving bodies so the soul could return. This gave "
            "us 3,000 years of mummies and the scientific data we still study today."
        ),
        did_you_know=(
            "The black color of Anubis was not meant to be frightening — it "
            "symbolized the rich black soil of the Nile, representing fertility "
            "and resurrection. His dark form was a promise of rebirth, not doom.\n\n"
            "The famous \"Anubis shrine\" found in Tutankhamun's tomb — a black "
            "jackal crouching on a gilded chest — was so realistic that Howard "
            "Carter described it as the most eerie thing he'd ever seen in the tomb."
        ),
        hidden_info=(
            "Anubis had a female counterpart called Anput, and a daughter named "
            "Kebechet (\"the cooling water\"), who assisted souls in the afterlife "
            "by offering purifying water. These figures are almost never mentioned "
            "in popular accounts.\n\n"
            "Some ancient texts describe Anubis cutting open the bodies of the "
            "unjust in the underworld — a far darker role than his usual portrayal "
            "as a gentle guide of souls."
        ),
        fun_facts=(
            "Priests performing mummification would wear full Anubis masks — "
            "complete with the elongated snout — during the ritual. Archaeologists "
            "have found actual bronze Anubis masks used in ceremonies.\n\n"
            "The Greeks identified Anubis with their god Hermes (guide of the dead), "
            "creating the hybrid deity \"Hermanubis\" — depicted holding a caduceus "
            "with a jackal head. Quite the crossover."
        ),
    ),
}


ALIASES = {
    "tut": "tutankhamun",
    "0": "tutankhamun",
    "king_tut": "tutankhamun",
    "tutankhamen": "tutankhamun",
    "mask": "tutankhamun",
    "4": "pyramids_of_giza",
    "pyramid": "pyramids_of_giza",
    "pyramids": "pyramids_of_giza",
    "giza": "pyramids_of_giza",
    "2": "nefertiti",
    "nefertiti_bust": "nefertiti",
    "1": "ramses_ii",
    "ramses": "ramses_ii",
    "ramsis": "ramses_ii",
    "ramesses": "ramses_ii",
    "ramesses_ii": "ramses_ii",
    "3": "anubis",
}


def normalize_artifact_key(class_name: str) -> str | None:
    key = class_name.strip().lower().replace(" ", "_").replace("-", "_")
    if key in ARTIFACTS:
        return key
    return ALIASES.get(key)
