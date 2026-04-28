# 🎓 IONISBot — Assistant étudiant IONIS Group

> Chatbot intelligent pour les campus du groupe IONIS (EPITECH, EPITA, ISEG, E-ARTSUP…).  
> Disponible en **interface web** et sur **Discord**.

---

## 📋 Présentation

IONISBot est un assistant conversationnel dédié aux étudiants du groupe IONIS. Il répond aux questions sur les horaires, les transports, la restauration, les formations, l'admission et la vie étudiante — pour chaque école et chaque campus.

Il repose sur :
- **Flask** (backend API)
- **Ollama + Mistral** (modèle de langage local)
- **discord.py** (bot Discord avec commandes slash)

---

## 🗂️ Structure du projet

```
ionisbot/
├── app.py              # Serveur Flask (API + interface web)
├── discord_bot.py      # Bot Discord
├── requirements.txt    # Dépendances Python
└── static/
    └── index.html      # Interface web
```

---

## ⚙️ Prérequis

- Python **3.8+**
- [Ollama](https://ollama.com) installé et lancé
- Un token de bot Discord (si tu utilises le bot Discord)

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/ton-utilisateur/ionisbot.git
cd ionisbot
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Installer et lancer Ollama avec Mistral

```bash
ollama pull mistral
ollama serve
```

### 4. Placer l'interface web

Assure-toi que `index.html` est dans le dossier `static/` :

```bash
mkdir -p static
mv index.html static/
```

### 5. Lancer le serveur Flask

```bash
python app.py
```

Le serveur démarre sur **http://localhost:8000**.

---

## 🌐 Interface web

Ouvre ton navigateur sur :

```
http://localhost:8000
```

Tu peux alors sélectionner ton école, puis ton campus, et poser tes questions directement.

---

## 🤖 Bot Discord

### Configuration

Dans `discord_bot.py`, remplace le token par le tien :

```python
DISCORD_TOKEN = "MTQ5MTM2NTIzOTk0NDY0NjcyNw.GrL7Cw.DtljtpkMolCPgKuzBXktCMsa4BrWdwtwkz6ej4"
```

> ⚠️ Ne partage jamais ton token publiquement. Utilise une variable d'environnement en production.

### Lancer le bot

```bash
python discord_bot.py
```

### Commandes disponibles

| Commande | Description |
|---|---|
| `/campus` | Sélectionner ton école et ton campus |
| `/chat` | Poser une question à IONISBot |
| `/horaires` | Afficher les horaires de ton campus |
| `/reset` | Réinitialiser l'historique de conversation |

Le bot répond aussi aux **messages privés** et aux **mentions** dans les salons.

---

## 🔍 Vérifier que tout fonctionne

Une fois Flask lancé, accède à :

```
http://localhost:8000/health
```

Tu dois obtenir :

```json
{ "ollama": true, "mistral": true }
```

---

## 🏫 Écoles et campus supportés

| École | Domaine |
|---|---|
| **EPITECH** | Informatique, développement, innovation tech |
| **EPITA** | Intelligence artificielle, cybersécurité, réseaux |
| **ISEG** | Finance, management, marketing |
| **E-ARTSUP** | Design, art numérique, communication visuelle |
| *(et d'autres écoles du groupe IONIS)* | |

Chaque école couvre plusieurs campus en France (Paris, Lyon, Bordeaux, Toulouse, Marseille, Nantes, Lille, Strasbourg, Rennes, Montpellier, Nice, Sophia-Antipolis…).

---

## 🛠️ API — Endpoints Flask

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Interface web |
| `GET` | `/schools` | Liste des écoles et campus |
| `GET` | `/campus-info/<school>/<campus>` | Infos détaillées d'un campus |
| `POST` | `/chat` | Réponse synchrone |
| `POST` | `/chat-stream` | Réponse en streaming (SSE) |
| `POST` | `/feedback` | Enregistrer un feedback |
| `GET` | `/health` | Statut d'Ollama et Mistral |

### Exemple de requête `/chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quels sont les horaires du campus ?",
    "school": "EPITECH",
    "campus": "Paris",
    "history": []
  }'
```

---

## 🔒 Limitations & sécurité

- **Rate limiting** : 20 requêtes par minute par adresse IP
- **Cache** : jusqu'à 100 réponses mises en cache (en mémoire)
- **Longueur max** : 1000 caractères par message
- **Token Discord** : à stocker dans une variable d'environnement (`DISCORD_TOKEN`) en production

---

## 🧪 Tests

```bash
pytest --cov=app tests/
```

---

## 📄 Licence

Projet développé Par Adem Loukili
