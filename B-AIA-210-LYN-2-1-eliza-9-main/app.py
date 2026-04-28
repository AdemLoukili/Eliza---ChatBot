from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import httpx
import json
import logging
from collections import defaultdict
import time
try:
    from langdetect import detect as langdetect_detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

logging.basicConfig(
    filename='campusbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"


SCHOOLS_INFO = {

    "EPITECH": {
        "description": "École d'informatique et d'innovation technologique. Pédagogie par projet, pas de cours magistraux.",
        "domaine": "Informatique, développement, innovation tech",
        "campus": {
            "Paris": {
                "adresse": "24 Rue Pasteur, 94270 Le Kremlin-Bicêtre",
                "tel": "01 44 08 01 01",
                "horaires": "Lun-Ven 8h30-22h, Sam 9h-18h",
                "transport": "Métro ligne 7 - station Le Kremlin-Bicêtre. Bus 47, 57, 131.",
                "restauration": "RU Le Kremlin-Bicêtre à 5 min, nombreux restos rue Pasteur",
                "specificites": "Plus grand campus EPITECH, hub innovation, nombreux événements tech"
            },
            "Lyon": {
                "adresse": "2 Rue du Professeur Charles Appleton, 69007 Lyon",
                "tel": "04 72 85 72 72",
                "horaires": "Lun-Ven 8h30-21h, Sam 9h-17h",
                "transport": "Métro B - station Gare de Jean Mace. T2 arrêt Centre Berthelot et T1 arrêt Quai Claude Benard.",
                "restauration": "RU Bourse du Travail, kebabs snacks et restos quai de Saône",
                "specificites": "Campus dynamique, fort réseau entreprises région Auvergne-Rhône-Alpes"
            },
            "Bordeaux": {
                "adresse": "183 Rue du Judaïque, 33000 Bordeaux",
                "tel": "05 56 15 06 06",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Tram B - station Judaïque François Rabelais. Bus 4, 15.",
                "restauration": "RU Victoire, nombreux restos rue Sainte-Catherine",
                "specificites": "Campus à taille humaine, excellent réseau startups bordelaises"
            },
            "Toulouse": {
                "adresse": "128 Rue de la Pyramide, 31100 Toulouse",
                "tel": "05 62 88 28 28",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Métro ligne A - station Arènes. Bus 14, 66.",
                "restauration": "RU Arsenal, food trucks campus",
                "specificites": "Écosystème aéronautique et spatial (Airbus, CNES), très actif"
            },
            "Marseille": {
                "adresse": "61 Rue Saint-Joseph, 13006 Marseille",
                "tel": "04 91 36 66 36",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Métro ligne 1 - station Notre-Dame du Mont. Bus 80, 81.",
                "restauration": "Nombreux restos Cours Julien à 2 min",
                "specificites": "Campus méditerranéen, fort réseau French Tech Aix-Marseille"
            },
            "Nantes": {
                "adresse": "4 Rue Ampère, 44470 Carquefou",
                "tel": "02 51 13 13 13",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Bus ligne C - direction Carquefou. TAN : tan.fr",
                "restauration": "Cafétéria sur place, restos Carquefou centre",
                "specificites": "Campus proche de Saint-Nazaire, réseau industrie maritime et numérique"
            },
            "Lille": {
                "adresse": "83 Rue de la Liberté, 59800 Lille",
                "tel": "03 20 04 04 04",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Métro ligne 1 - station République Beaux-Arts. Bus L1, L2.",
                "restauration": "RU Pont de Bois, nombreux restos Vieux-Lille",
                "specificites": "Proximité Belgique, fort réseau ESN et événements eurotech"
            },
            "Strasbourg": {
                "adresse": "2 Rue de Londres, 67000 Strasbourg",
                "tel": "03 88 21 21 21",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Tram ligne A - station Homme de Fer. Bus 2, 10.",
                "restauration": "RU Esplanade, winstubs alsaciens à proximité",
                "specificites": "Campus européen, partenariats avec institutions EU à Strasbourg"
            },
            "Rennes": {
                "adresse": "33 Rue du Bignon, 35000 Rennes",
                "tel": "02 99 27 27 27",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Métro ligne A - station République. Bus C4, 57.",
                "restauration": "RU Beaulieu, nombreux restos quartier Colombier",
                "specificites": "Écosystème cyber et défense, partenariats DGA et Orange Cyberdefense"
            },
            "Montpellier": {
                "adresse": "675 Avenue du Pérols, 34470 Pérols",
                "tel": "04 67 07 07 07",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Tram ligne 3 - station Pérols Étang de l'Or.",
                "restauration": "Cafétéria campus, food trucks réguliers",
                "specificites": "Proche de la mer, réseau biotech et santé numérique actif"
            },
            "Nice": {
                "adresse": "81 Boulevard de la République, 06000 Nice",
                "tel": "04 93 21 21 21",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Tram ligne 1 - station Garibaldi. Bus 10, 22.",
                "restauration": "Nombreux restos quartier Libération",
                "specificites": "Proximité Monaco et Italian Tech, réseau gaming et esport fort"
            },
            "Sophia-Antipolis": {
                "adresse": "Les Algorythmes, 06560 Sophia Antipolis",
                "tel": "04 93 00 00 00",
                "horaires": "Lun-Ven 8h30-21h",
                "transport": "Bus lignes ZOU! 230, 231 depuis Nice. Pas de métro direct.",
                "restauration": "Restaurants technopole, cafétéria sur place",
                "specificites": "Au cœur de la Silicon Valley française, accès direct aux grands groupes tech"
            },
        }
    },

    "EPITA": {
        "description": "École d'ingénieurs spécialisée en intelligence informatique. Diplôme d'ingénieur reconnu CTI.",
        "domaine": "Intelligence artificielle, cybersécurité, réseaux, logiciel",
        "campus": {
            "Paris - Kremlin-Bicêtre": {
                "adresse": "14-16 Rue Voltaire, 94270 Le Kremlin-Bicêtre",
                "tel": "01 44 08 01 01",
                "horaires": "Lun-Ven 8h30-22h",
                "transport": "Métro ligne 7 - station Le Kremlin-Bicêtre.",
                "restauration": "RU Le Kremlin-Bicêtre, restos rue Pasteur",
                "specificites": "Campus principal, laboratoires IA et cybersécurité, forte vie associative"
            },
            "Paris - Villejuif": {
                "adresse": "66 Rue Guy Môquet, 94800 Villejuif",
                "tel": "01 84 07 16 76",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Métro ligne 7 - station Villejuif Léo Lagrange.",
                "restauration": "Cafétéria campus, restos avenue de Paris",
                "specificites": "Campus numérique dédié aux nouvelles technologies et au digital"
            },
            "Lyon": {
                "adresse": "86 Boulevard Marius Vivier Merle, 69003 Lyon",
                "tel": "04 84 34 02 61",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Tram T3 - station Garibaldi Université. Métro D - station Garibaldi.",
                "restauration": "Nombreux restos Part-Dieu à 5 min",
                "specificites": "Campus lyonnais au cœur du quartier Part-Dieu, réseau entreprises tech local"
            },
            "Rennes": {
                "adresse": "19-22 Boulevard Saint-Conwoïon, 35000 Rennes",
                "tel": "02 57 22 08 11",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Métro ligne A - station République. Bus C4.",
                "restauration": "RU Beaulieu, restos quartier Colombier",
                "specificites": "Partenariats défense et cybersécurité, Orange Cyberdefense, DGA"
            },
            "Strasbourg": {
                "adresse": "5 Rue Gustave Adolphe Hirn, 67000 Strasbourg",
                "tel": "03 67 18 04 01",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Tram ligne D - station Observatoire. Bus 10.",
                "restauration": "RU Esplanade, restaurants centre-ville",
                "specificites": "Campus à dimension européenne, partenariats institutions EU"
            },
            "Toulouse": {
                "adresse": "14 Rue Claire Pauilhac, 31000 Toulouse",
                "tel": "05 64 13 05 31",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Métro ligne A - station Capitole. Bus 38.",
                "restauration": "RU Arsenal, nombreux restos centre-ville",
                "specificites": "Écosystème aéronautique et spatial (Airbus, CNES, Thales)"
            },
        }
    },

    "ISEG": {
        "description": "École de communication, marketing et digital. Diplôme visé Bac+5.",
        "domaine": "Marketing, communication, digital, publicité",
        "campus": {
            "Paris": {
                "adresse": "95 Avenue Parmentier, 75011 Paris",
                "tel": "01 84 07 41 10",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Métro ligne 3 - station Rue Saint-Maur. Métro ligne 9 - station Saint-Ambroise.",
                "restauration": "Nombreux restos et cafés avenue Parmentier, quartier Oberkampf",
                "specificites": "Campus Parmentier partagé avec e-artsup et Epitech Digital, 8000m²"
            },
            "Bordeaux": {
                "adresse": "85 Rue du Jardin Public, 33000 Bordeaux",
                "tel": "05 57 87 00 28",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram B - station Cours du Médoc. Bus 27.",
                "restauration": "Restos quartier des Chartrons, marché des Chartrons",
                "specificites": "Campus dans le quartier des Chartrons, réseau startups et agences bordelaises"
            },
            "Lille": {
                "adresse": "10-12 Rue du Bas Jardin, 59000 Lille",
                "tel": "03 20 15 84 41",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Métro ligne 1 - station République Beaux-Arts. Bus L1.",
                "restauration": "Restos Vieux-Lille, rue de Béthune",
                "specificites": "Campus partagé avec e-artsup Lille, fort réseau agences communication Nord"
            },
            "Lyon": {
                "adresse": "2 Rue du Professeur Charles Appleton, 69007 Lyon",
                "tel": "04 72 85 72 72",
                "horaires": "Lun-Ven 8h30-21h, Sam 9h-17h",
                "transport": "Métro B - station Gare de Jean Mace. T2 arrêt Centre Berthelot et T1 arrêt Quai Claude Benard.",
                "restauration": "RU Bourse du Travail, kebabs snacks et restos quai de Saône",
                "specificites": "Campus partagé avec e-artsup Lyon, réseau agences et médias lyonnais"
            },
            "Nantes": {
                "adresse": "8 Rue de Bréa, 44000 Nantes",
                "tel": "02 40 89 07 52",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne 1 - station Médiathèque. Bus C1.",
                "restauration": "Restos centre-ville Nantes, marché de Talensac",
                "specificites": "Campus centre-ville, fort réseau entreprises et agences de communication nantaises"
            },
            "Nice": {
                "adresse": "131 Boulevard René Cassin, 06200 Nice - Quartier de l'Arenas",
                "tel": "04 22 13 33 40",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne 2 - station Arénas. Bus 99 aéroport.",
                "restauration": "Restaurants quartier de l'Arenas, food court aéroport à 5 min",
                "specificites": "Campus proche de l'aéroport Nice Côte d'Azur, réseau tourisme et luxe"
            },
            "Strasbourg": {
                "adresse": "4 Rue du Dôme, 67000 Strasbourg",
                "tel": "03 88 36 02 88",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne A ou D - station Homme de Fer. Bus 2.",
                "restauration": "Winstubs et restos centre historique, marché de Noël en décembre",
                "specificites": "Campus centre historique, partenariats médias et institutions européennes"
            },
            "Toulouse": {
                "adresse": "40 Boulevard de la Marquette, 31000 Toulouse",
                "tel": "05 61 62 35 37",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Métro ligne A - station Capitole. Bus 38.",
                "restauration": "Restos rue Alsace-Lorraine, nombreux cafés centre-ville",
                "specificites": "Campus centre-ville, réseau agences et grands comptes toulousains"
            },
        }
    },

    "e-artsup": {
        "description": "École de création visuelle, design graphique, motion design, game art. Diplôme Bac+3 et Bac+5.",
        "domaine": "Design graphique, motion design, animation 2D/3D, game art, esport",
        "campus": {
            "Paris": {
                "adresse": "95 Avenue Parmentier, 75011 Paris",
                "tel": "01 84 07 13 00",
                "horaires": "Lun-Ven 8h30-20h",
                "transport": "Métro ligne 3 - station Rue Saint-Maur. Métro ligne 9 - station Saint-Ambroise.",
                "restauration": "Nombreux restos et cafés avenue Parmentier, quartier Oberkampf",
                "specificites": "Campus Parmentier partagé avec ISEG et Epitech Digital, équipements créatifs"
            },
            "Bordeaux": {
                "adresse": "51 Rue Camille Godard, 33300 Bordeaux",
                "tel": "05 57 87 33 61",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram C - station Cours du Médoc. Bus 27.",
                "restauration": "Restos quartier des Chartrons, marché des Chartrons",
                "specificites": "Campus Camille Godard, ateliers créatifs et équipements design"
            },
            "Lille": {
                "adresse": "10-12 Rue du Bas Jardin, 59000 Lille",
                "tel": "03 20 15 84 40",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Métro ligne 1 - station République Beaux-Arts. Bus L1.",
                "restauration": "Restos Vieux-Lille, rue de Béthune",
                "specificites": "Campus du Bas Jardin partagé avec ISEG Lille, studios créatifs"
            },
            "Lyon": {
                "adresse": "2 Rue du Professeur Charles Appleton, 69007 Lyon",
                "tel": "04 72 85 72 72",
                "horaires": "Lun-Ven 8h30-21h, Sam 9h-17h",
                "transport": "Métro B - station Gare de Jean Mace. T2 arrêt Centre Berthelot et T1 arrêt Quai Claude Benard.",
                "restauration": "RU Bourse du Travail, kebabs snacks et restos quai de Saône",
                "specificites": "Campus Appleton partagé avec ISEG Lyon, équipements motion design et 3D"
            },
            "Marseille": {
                "adresse": "61 Rue Saint-Joseph, 13006 Marseille",
                "tel": "04 91 36 66 37",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Métro ligne 1 - station Notre-Dame du Mont. Bus 80.",
                "restauration": "Restos Cours Julien à 2 min, street food quartier",
                "specificites": "Campus méditerranéen, forte communauté créative, lien avec scène artistique marseillaise"
            },
            "Montpellier": {
                "adresse": "Campus IONIS Montpellier, 34000 Montpellier",
                "tel": "04 67 07 07 08",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne 1 - station Place de l'Europe. Bus 12.",
                "restauration": "Cafétéria campus, restos quartier Antigone",
                "specificites": "Campus en développement, réseau créatif et digital montpelliérain"
            },
            "Nantes": {
                "adresse": "Campus IONIS Nantes, 44000 Nantes",
                "tel": "02 40 89 07 53",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne 1 - station Médiathèque. Bus C1.",
                "restauration": "Restos centre-ville Nantes",
                "specificites": "Campus créatif nantais, partenariats studios d'animation et jeu vidéo locaux"
            },
            "Nice": {
                "adresse": "131 Boulevard René Cassin, 06200 Nice - Quartier de l'Arenas",
                "tel": "04 22 13 33 41",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne 2 - station Arénas. Bus 99.",
                "restauration": "Restaurants quartier Arenas",
                "specificites": "Campus proche Monaco, réseau gaming et esport fort, lien avec industrie du luxe"
            },
            "Strasbourg": {
                "adresse": "4 Rue du Dôme, 67000 Strasbourg",
                "tel": "03 88 36 02 89",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne A ou D - station Homme de Fer.",
                "restauration": "Restos et winstubs centre historique",
                "specificites": "Campus centre historique, dimension européenne, partenariats studios créatifs"
            },
            "Toulouse": {
                "adresse": "40 Boulevard de la Marquette, 31000 Toulouse",
                "tel": "05 61 62 35 38",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Métro ligne A - station Capitole. Bus 38.",
                "restauration": "Restos centre-ville toulousain",
                "specificites": "Campus centre-ville, réseau studios jeu vidéo et animation toulousains"
            },
            "Tours": {
                "adresse": "Campus IONIS Tours, 37000 Tours",
                "tel": "02 47 00 00 00",
                "horaires": "Lun-Ven 8h30-19h",
                "transport": "Tram ligne A - station Jean Jaurès. Bus 4.",
                "restauration": "Restos centre-ville Tours",
                "specificites": "Seul campus e-artsup en région Centre-Val de Loire"
            },
        }
    },
}

def build_schools_context():
    lines = []
    for school, school_data in SCHOOLS_INFO.items():
        lines.append(f"\n{'='*60}")
        lines.append(f"ÉCOLE : {school}")
        lines.append(f"Description : {school_data['description']}")
        lines.append(f"Domaine : {school_data['domaine']}")
        lines.append(f"Campus disponibles : {', '.join(school_data['campus'].keys())}")
        for city, info in school_data['campus'].items():
            lines.append(f"\n  --- {school} {city} ---")
            lines.append(f"  Adresse : {info['adresse']}")
            lines.append(f"  Téléphone : {info['tel']}")
            lines.append(f"  Horaires : {info['horaires']}")
            lines.append(f"  Transports : {info['transport']}")
            lines.append(f"  Restauration : {info['restauration']}")
            lines.append(f"  Spécificités : {info['specificites']}")
    return "\n".join(lines)

SCHOOLS_CONTEXT = build_schools_context()

SCHOOL_NAMES = list(SCHOOLS_INFO.keys())
IONIS_GROUP_DESC = "IONIS Education Group est le premier groupe d'enseignement supérieur privé en France avec plus de 29 écoles et 35 000 étudiants."

SYSTEM_PROMPT = f"""Tu es IONISBot, l'assistant officiel du groupe IONIS Education Group pour toutes ses écoles en France.
{IONIS_GROUP_DESC}

Tu connais les écoles suivantes du groupe IONIS : {", ".join(SCHOOL_NAMES)}.

Voici les informations détaillées sur chaque école et leurs campus :
{SCHOOLS_CONTEXT}

Règles de comportement STRICTES :
- RÈGLE N°1 ABSOLUE ET PRIORITAIRE SUR TOUT : Tu DOIS répondre UNIQUEMENT et EXCLUSIVEMENT dans la langue détectée : {{DETECTED_LANGUAGE}}. Peu importe que les données soient en français, tu TRADUIS ta réponse dans {{DETECTED_LANGUAGE}}. Ne jamais répondre en français si {{DETECTED_LANGUAGE}} n'est pas le français.
- Utilise UNIQUEMENT les informations fournies ci-dessus. N'invente JAMAIS de lignes de transport, d'adresses, de restaurants ou d'informations supplémentaires non présentes dans les données.
- Si une information n'est pas présente dans les données ci-dessus, réponds EXACTEMENT (traduit dans {{DETECTED_LANGUAGE}}) : "Je n'ai pas cette information précise, je te conseille de contacter directement l'administration du campus concerné."
- Si l'utilisateur mentionne une école ET un campus précis, utilise uniquement les infos de ce campus.
- Si l'utilisateur mentionne seulement une école, tu peux parler de tous ses campus.
- Sois précis, concis et utile.
- Tu peux répondre sur : horaires, transports, restauration, vie étudiante, formations, admission, stages, alternance, vie associative, spécificités de chaque école.
- Ne parle que des écoles du groupe IONIS listées ci-dessus.
"""

request_counts = defaultdict(list)
RATE_LIMIT = 20
RATE_WINDOW = 60

def is_rate_limited(ip):
    now = time.time()
    request_counts[ip] = [t for t in request_counts[ip] if now - t < RATE_WINDOW]
    if len(request_counts[ip]) >= RATE_LIMIT:
        return True
    request_counts[ip].append(now)
    return False

response_cache = {}
CACHE_MAX = 100

def get_cache_key(school, campus, message):
    return f"{school}::{campus}::{message.lower().strip()}"

LANG_CODE_TO_NAME = {
    "af": "afrikaans", "ar": "arabe", "bg": "bulgare", "bn": "bengali",
    "ca": "catalan", "cs": "tchèque", "cy": "gallois", "da": "danois",
    "de": "allemand", "el": "grec", "en": "anglais", "es": "espagnol",
    "et": "estonien", "fa": "persan", "fi": "finnois", "fr": "français",
    "gu": "gujarati", "he": "hébreu", "hi": "hindi", "hr": "croate",
    "hu": "hongrois", "id": "indonésien", "it": "italien", "ja": "japonais",
    "kn": "kannada", "ko": "coréen", "lt": "lituanien", "lv": "letton",
    "mk": "macédonien", "ml": "malayalam", "mr": "marathi", "ne": "népalais",
    "nl": "néerlandais", "no": "norvégien", "pa": "pendjabi", "pl": "polonais",
    "pt": "portugais", "ro": "roumain", "ru": "russe", "sk": "slovaque",
    "sl": "slovène", "so": "somali", "sq": "albanais", "sv": "suédois",
    "sw": "swahili", "ta": "tamoul", "te": "télougou", "th": "thaï",
    "tl": "tagalog", "tr": "turc", "uk": "ukrainien", "ur": "ourdou",
    "vi": "vietnamien", "zh-cn": "chinois", "zh-tw": "chinois traditionnel",
    "zh": "chinois",
}

DARIJA_WORDS = {'wach', 'wash', 'nta', 'ntia', 'bghit', 'kifach', 'hna', 'dyal',
               'bach', 'mzyan', 'zwina', 'kayn', 'makaynch', 'rani', 'walakin',
               'smit', 'fin', 'fain', 'ash', 'mnin', 'bzzaf', 'shwiya', 'safi'}

def detect_language(message):
    msg = message.strip().lower()
    # Darija check first (written in latin letters, often misdetected)
    words = set(msg.split())
    if len(words & DARIJA_WORDS) >= 1:
        return "darija (arabe marocain)"
    # Arabic script
    arabic_chars = sum(1 for c in message if '\u0600' <= c <= '\u06FF')
    if arabic_chars > 2:
        return "arabe"
    # Use langdetect if available
    if LANGDETECT_AVAILABLE:
        try:
            code = langdetect_detect(message)
            return LANG_CODE_TO_NAME.get(code, code)
        except Exception:
            pass
    # Fallback: basic unicode checks
    if sum(1 for c in message if '\u4e00' <= c <= '\u9fff') > 1:
        return "chinois"
    if sum(1 for c in message if '\u3040' <= c <= '\u30ff') > 1:
        return "japonais"
    if sum(1 for c in message if '\uac00' <= c <= '\ud7a3') > 1:
        return "coréen"
    return "français"


def build_prompt(message, history, school, campus):
    lang = detect_language(message)
    prompt_with_lang = SYSTEM_PROMPT.replace("{{DETECTED_LANGUAGE}}", lang)
    context = ""
    if school and campus:
        context += f"[L'étudiant est sur le campus {school} de {campus}]\n\n"
    elif school:
        context += f"[L'étudiant s'intéresse à l'école {school}]\n\n"
    for turn in history[-6:]:
        role = "Étudiant" if turn["role"] == "user" else "IONISBot"
        context += f"{role}: {turn['content']}\n"
    context += f"Étudiant: {message}\n"
    # Instruction de langue répétée JUSTE avant la réponse du bot — c'est la dernière
    # chose que le modèle lit avant de générer, donc elle a le plus de poids.
    context += f"[INSTRUCTION FINALE OBLIGATOIRE : ta réponse ci-dessous DOIT être rédigée ENTIÈREMENT en {lang}. Commence directement à répondre en {lang}.]\nIONISBot:"
    return f"{prompt_with_lang}\n\n{context}"

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/schools')
def schools():
    result = {}
    for school, data in SCHOOLS_INFO.items():
        result[school] = {
            "description": data["description"],
            "domaine": data["domaine"],
            "campus": list(data["campus"].keys())
        }
    return jsonify(result)

@app.route('/campus-list')
def campus_list():
    # Compatibilité avec l'ancien front — retourne tous les campus de toutes les écoles
    all_campus = []
    for school, data in SCHOOLS_INFO.items():
        for city in data["campus"].keys():
            all_campus.append(f"{school} - {city}")
    return jsonify({"campus": all_campus})

@app.route('/campus-info/<school>/<campus>')
def campus_info(school, campus):
    school_data = SCHOOLS_INFO.get(school)
    if not school_data:
        return jsonify({"error": "École introuvable"}), 404
    info = school_data["campus"].get(campus)
    if not info:
        return jsonify({"error": "Campus introuvable"}), 404
    return jsonify({"school": school, "campus": campus, **info})

@app.route('/chat', methods=['POST'])
def chat():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"reply": "⚠️ Trop de requêtes. Attends une minute avant de réessayer."}), 429

    data = request.get_json()
    message = data.get('message', '').strip()
    history = data.get('history', [])
    school = data.get('school', '')
    campus = data.get('campus', '')

    if not message:
        return jsonify({"reply": "❌ Message vide."}), 400
    if len(message) > 1000:
        return jsonify({"reply": "❌ Message trop long (max 1000 caractères)."}), 400

    cache_key = get_cache_key(school, campus, message)
    if cache_key in response_cache:
        logging.info(f"[CACHE] [{school}/{campus}] {message}")
        return jsonify({"reply": response_cache[cache_key], "cached": True})

    prompt = build_prompt(message, history, school, campus)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 300}
                }
            )
        reply = response.json().get("response", "").strip()
        if len(response_cache) < CACHE_MAX:
            response_cache[cache_key] = reply
        logging.info(f"[{school}/{campus}] USER: {message[:80]} | BOT: {reply[:80]}")
        return jsonify({"reply": reply})
    except Exception as e:
        logging.error(f"Erreur: {str(e)}")
        return jsonify({"reply": f"⚠️ Erreur serveur : {str(e)}"})

@app.route('/chat-stream', methods=['POST'])
def chat_stream():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"reply": "⚠️ Trop de requêtes."}), 429

    data = request.get_json()
    message = data.get('message', '').strip()
    history = data.get('history', [])
    school = data.get('school', '')
    campus = data.get('campus', '')

    if not message:
        return jsonify({"reply": "❌ Message vide."}), 400
    if len(message) > 1000:
        return jsonify({"reply": "❌ Message trop long."}), 400

    prompt = build_prompt(message, history, school, campus)

    def generate():
        try:
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", OLLAMA_URL, json={
                    "model": MODEL, "prompt": prompt, "stream": True,
                    "options": {"temperature": 0.2, "num_predict": 300}
                }) as r:
                    for line in r.iter_lines():
                        if line:
                            chunk = json.loads(line).get("response", "")
                            yield f"data: {json.dumps({'token': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    logging.info(f"[STREAM] [{school}/{campus}] USER: {message[:80]}")
    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    rating = data.get('rating', '')
    school = data.get('school', '')
    campus = data.get('campus', '')
    message = data.get('message', '')
    reply = data.get('reply', '')
    logging.info(f"[FEEDBACK {str(rating).upper()}] [{school}/{campus}] Q: {message[:80]} | R: {reply[:80]}")
    return jsonify({"status": "ok"})

@app.route('/health')
def health():
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get("http://localhost:11434/api/tags")
            models = r.json().get("models", [])
            has_mistral = any("mistral" in m["name"] for m in models)
        return jsonify({"ollama": True, "mistral": has_mistral})
    except:
        return jsonify({"ollama": False, "mistral": False})

if __name__ == '__main__':
    app.run(debug=True, port=8000)