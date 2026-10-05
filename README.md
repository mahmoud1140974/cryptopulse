# CryptoPulse

CryptoPulse est un bot Telegram d’analyse de risque de tokens crypto et d’intelligence de marché.

## Fonctionnalités Phase 1

- Scanner une adresse de contrat EVM ou Solana.
- Afficher prix, liquidité, volume 24h, market cap et données disponibles.
- Calculer un score de risque transparent et documenté.
- Ajouter jusqu’à 5 tokens à une watchlist gratuite.
- Vérifier les tokens suivis toutes les 15 minutes.
- Envoyer une alerte si le prix varie de plus de 10 %, la liquidité de plus de 20 %, ou le volume dépasse 3x la moyenne stockée.
- Fonctionner avec seulement `BOT_TOKEN`; les autres clés activent plus de données.
- Utiliser SQLite en local ou Supabase en production.

## Installation locale

### 1. Installer Python

Installez Python 3.11 ou plus récent depuis le site officiel :

<https://www.python.org/downloads/>

Pendant l’installation Windows, cochez la case **Add Python to PATH**.

### 2. Télécharger le projet

Placez le dossier `cryptopulse` sur votre ordinateur.

### 3. Ouvrir un terminal dans le dossier

- Windows : ouvrez le dossier, cliquez dans la barre d’adresse, tapez `cmd`, puis Entrée.
- macOS : ouvrez Terminal, tapez `cd `, glissez le dossier dans la fenêtre, puis Entrée.

### 4. Créer l’environnement et installer

```bash
python -m venv .venv
```

Windows :

```bash
.venv\Scripts\activate
```

macOS / Linux :

```bash
source .venv/bin/activate
```

Puis :

```bash
pip install -r requirements.txt
```

### 5. Créer le fichier de configuration

Windows :

```bash
copy .env.example .env
```

macOS / Linux :

```bash
cp .env.example .env
```

Ouvrez `.env` avec un éditeur de texte et ajoutez au minimum :

```env
BOT_TOKEN=votre_token_telegram
```

### 6. Lancer le bot

```bash
python main.py
```

Laissez la fenêtre ouverte. Dans Telegram, ouvrez votre bot et envoyez `/start`.

## Tests

```bash
pytest
```

Tous les tests doivent passer avant de modifier ou déployer une nouvelle phase.

## Déploiement Render free tier

1. Créez un compte gratuit sur <https://render.com>.
2. Créez un **Web Service**.
3. Connectez le dépôt Git du projet.
4. Choisissez Python 3.11+.
5. Build command :

   ```bash
   pip install -r requirements.txt
   ```

6. Start command :

   ```bash
   python main.py
   ```

7. Ajoutez les variables d’environnement dans Render :
   - `BOT_TOKEN`
   - `BOT_MODE=webhook`
   - `WEBHOOK_URL=https://votre-service.onrender.com`
   - `PORT=10000`
   - clés optionnelles si disponibles

8. Déployez.
9. Configurez UptimeRobot pour appeler `https://votre-service.onrender.com/health` toutes les 5 minutes.

## Structure

Voir `PROJECT_PLAN.md` pour le plan complet et `ARCHITECTURE.md` pour les choix techniques.

## Avertissement

CryptoPulse ne fournit pas de conseil financier. Les données peuvent être indisponibles, incomplètes ou erronées. Vérifiez toujours indépendamment.
