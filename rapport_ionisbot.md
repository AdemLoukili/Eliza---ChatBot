# IONISBot — Rapport Projet ELIZA
**EPITECH Lyon — B-AIA-210 — Groupe 2**
**Adem Loukili — Mars 2026**

---

## 1. Présentation du produit

**IONISBot** est un chatbot intelligent conçu pour le groupe IONIS Education Group, destiné à accompagner les étudiants et prospects dans leur parcours d'information sur les campus, formations et services des écoles du groupe (EPITECH, EPITA, ISEG, E-Artsup, etc.).

Le chatbot est accessible via :
- Une **interface web** responsive (full-screen, dark mode)
- Un **bot Discord** intégré avec commandes slash

Le moteur de génération repose sur **Mistral** via **Ollama** (LLM open-source hébergé localement), garantissant une maîtrise totale de l'intelligence et de la logique sans dépendance à une API tiers comme ChatGPT.

---

## 2. Stratégie Marketing

### 2.1 Cible

| Segment | Profil |
|---|---|
| **Primaire** | Lycéens en terminale (16–18 ans) cherchant une école post-bac |
| **Secondaire** | Étudiants en réorientation (BTS, IUT, licence) |
| **Tertiaire** | Parents d'élèves cherchant des informations pratiques |

### 2.2 Besoins identifiés

- Accès rapide aux informations pratiques (horaires, transports, restauration)
- Réponses disponibles 24h/24, sans attente d'un conseiller humain
- Personnalisation par école et campus
- Interface accessible depuis Discord (plateforme principale des 15–25 ans)

### 2.3 Objectifs du chatbot

| Objectif | Description |
|---|---|
| **Acquisition** | Convertir les prospects en candidats via un parcours informatif fluide |
| **Rétention** | Fidéliser les étudiants en répondant à leurs questions quotidiennes |
| **Automatisation** | Réduire la charge des services d'accueil et d'admission |
| **Communication** | Véhiculer l'image innovante et tech du groupe IONIS |

### 2.4 Chaîne de valeur

```
Prospect/Étudiant
       ↓
Pose une question (Discord / Web)
       ↓
IONISBot sélectionne l'école + campus
       ↓
Mistral génère une réponse contextualisée
       ↓
Réponse personnalisée en temps réel
       ↓
Engagement + conversion + satisfaction
```

---

## 3. Retour sur Investissement (ROI) & KPIs

### 3.1 Indicateurs clés de performance

| KPI | Valeur cible | Description |
|---|---|---|
| **Taux de réponse automatique** | > 85% | Questions traitées sans intervention humaine |
| **Temps de réponse moyen** | < 5 secondes | Délai entre question et réponse |
| **Satisfaction utilisateur** | > 4/5 | Mesurée via le système de feedback (👍/👎) |
| **Taux de conversion** | +15% | Prospects ayant soumis un dossier après interaction |
| **Réduction des appels** | −30% | Baisse des appels aux services d'admission |
| **Sessions Discord actives** | > 200/mois | Engagement sur la plateforme Discord |

### 3.2 ROI estimé

- **Coût d'un conseiller humain** : ~2 500 €/mois (équivalent 0.5 ETP)
- **Coût d'hébergement IONISBot** : ~50 €/mois (serveur + Ollama local)
- **Économie annuelle estimée** : ~28 800 €
- **ROI projeté sur 12 mois** : **~576x**

> En automatisant 85% des questions fréquentes, IONISBot libère les conseillers pour des missions à plus forte valeur ajoutée (entretiens, événements, suivi personnalisé).

---

## 4. Fonctionnalités techniques

### 4.1 Interface web
- Sélection interactive école → campus (grille responsive)
- Chat en temps réel avec historique de conversation
- Suggestions de questions rapides (horaires, transports, restauration…)
- Design full-screen responsive (mobile, tablette, desktop)
- Ticker informatif animé avec les campus du groupe

### 4.2 Bot Discord
- Commandes slash : `/campus`, `/chat`, `/horaires`, `/reset`
- Menus déroulants interactifs pour sélectionner école et campus
- Historique de conversation par utilisateur
- Message d'accueil automatique pour les nouveaux membres
- Réponse aux mentions et messages directs (DM)

### 4.3 Backend Flask
- API REST : `/chat`, `/schools`, `/campus-info`, `/health`
- Rate limiting (20 req/min/IP)
- Cache LRU (100 entrées max)
- Logging complet dans `campusbot.log`
- CORS activé pour le front-end web
- Variables d'environnement via `.env` (token Discord, port, modèle Ollama)

### 4.4 Modèle IA
- **Mistral 7B** via Ollama (hébergement local)
- Prompt système contextualisé avec les données des 40+ campus IONIS
- Température 0.2 pour des réponses précises et factuelles
- Historique glissant sur 8 derniers échanges pour maintenir le contexte

---

## 5. Identité visuelle & Expérience utilisateur

- **Palette** : Fond noir `#0d0d0d`, accent bleu électrique `#2416e5`, texte crème `#f0ede8`
- **Typographie** : Bebas Neue (titres) + IBM Plex Mono (labels) + IBM Plex Sans (corps)
- **Ton** : Professionnel, précis, bienveillant — jamais familier
- **Nom** : IONISBot — immédiatement identifiable au groupe IONIS
- L'interface évite tout design générique : pas de bulles arrondies pastels, pas de purple gradient — un esthétique industriel/tech cohérent avec l'ADN EPITECH

---

## 6. Évaluation éthique

### 6.1 Effet ELIZA & risques identifiés

| Risque | Niveau | Mesure mise en place |
|---|---|---|
| **Anthropomorphisation** | Moyen | Le bot se présente explicitement comme un assistant automatique, jamais comme un humain |
| **Désinformation** | Faible | Données campus vérifiées manuellement, température basse (0.2) pour limiter les hallucinations |
| **Dépendance** | Faible | Le bot encourage à contacter directement les campus pour les démarches officielles |
| **Biais algorithmiques** | Moyen | Mistral peut avoir des biais de langue/culture ; le prompt système cadre strictement les réponses aux données IONIS |
| **Confidentialité** | Faible | Aucune donnée personnelle stockée ; seuls les logs techniques sont conservés (messages anonymisés) |
| **Données utilisateur** | Faible | Pas de compte, pas de tracking, historique en mémoire uniquement (session) |

### 6.2 Principes éthiques appliqués

- **Transparence** : Le bot s'identifie clairement comme un système automatique
- **Limitation du scope** : Il ne répond qu'aux questions relatives aux écoles IONIS, refusant tout hors-sujet
- **Révocabilité** : Commande `/reset` pour effacer l'historique à tout moment
- **Équité** : Informations identiques pour tous les campus, sans favoriser une école
- **Respect de la vie privée** : Aucune collecte de données personnelles, aucun cookie

### 6.3 Ce que le bot ne fait pas
- Il ne prétend pas être humain
- Il ne donne pas d'avis sur les écoles concurrentes
- Il ne stocke pas les conversations au-delà de la session
- Il ne prend pas de décisions à la place de l'utilisateur (admission, inscription)

---

## 7. Architecture technique

```
┌─────────────────────────────────────────────┐
│                  UTILISATEURS                │
│         Web Browser    Discord Client        │
└──────────┬──────────────────┬───────────────┘
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌───────────────────────┐
│   Interface Web  │  │     discord_bot.py     │
│   (index.html)   │  │  (commandes slash,     │
│   Flask static   │  │   menus déroulants)    │
└────────┬─────────┘  └──────────┬────────────┘
         │                       │
         └──────────┬────────────┘
                    ▼
         ┌─────────────────────┐
         │      app.py         │
         │   Flask REST API    │
         │  /chat /schools     │
         │  rate limit + cache │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │   Ollama + Mistral  │
         │  (LLM local :11434) │
         └─────────────────────┘
```

---

## 8. Documentation d'installation

### Prérequis
- Python 3.12+
- Ollama installé avec le modèle Mistral (`ollama pull mistral`)
- Un bot Discord créé sur le portail développeur

### Installation

```bash
git clone <repo>
cd <projet>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Remplir DISCORD_TOKEN dans .env
```

### Structure des fichiers

```
projet/
├── app.py              # Backend Flask
├── discord_bot.py      # Bot Discord
├── static/
│   └── index.html      # Interface web
├── .env                # Variables d'environnement (non committé)
├── .env.example        # Template .env
├── requirements.txt    # Dépendances Python
└── campusbot.log       # Logs générés automatiquement
```

### Lancement

```bash
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Flask
source venv/bin/activate
python app.py

# Terminal 3 — Discord Bot
source venv/bin/activate
python discord_bot.py
```

### Variables d'environnement (`.env`)

| Variable | Défaut | Description |
|---|---|---|
| `DISCORD_TOKEN` | — | Token du bot Discord |
| `FLASK_PORT` | `8000` | Port du serveur Flask |
| `FLASK_DEBUG` | `true` | Mode debug Flask |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Endpoint Ollama |
| `OLLAMA_MODEL` | `mistral` | Modèle LLM utilisé |

---

## 9. Conclusion

IONISBot répond aux 4 axes du projet ELIZA :

| Axe | Réalisé |
|---|---|
| **Business** | Cible définie, chaîne de valeur documentée, KPIs et ROI chiffrés |
| **Éthique** | Évaluation d'impact réalisée, mesures concrètes intégrées |
| **Fonctionnalités** | Chatbot testable sur Discord + web, LLM open-source contrôlé |
| **Expérience** | Identité visuelle forte, UX soignée, interface responsive |

> IONISBot n'est pas qu'un chatbot qui fonctionne — c'est un produit qui apporte une valeur tangible au groupe IONIS en automatisant l'information étudiante 24h/24, tout en respectant les principes éthiques d'un usage responsable de l'IA.
