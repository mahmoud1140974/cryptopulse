# SETUP.md — Guide pas à pas

Ce guide est écrit pour un propriétaire non-codeur. Suivez les étapes dans l’ordre.

## 1. Créer le bot Telegram

📋 **ACTION HUMAINE REQUISE — Étape 1 sur 5**

1. Ouvrez Telegram.
2. Dans la recherche, tapez `@BotFather`.
3. Ouvrez le compte officiel **BotFather**.
4. Envoyez `/newbot`.
5. Choisissez un nom, par exemple `CryptoPulse`.
6. Choisissez un nom d’utilisateur qui finit par `bot`, par exemple `YourCryptoPulseBot`.
7. BotFather vous donne un token qui ressemble à `123456:ABC-DEF...`.
8. Copiez ce token.
9. Ouvrez le fichier `.env`.
10. Collez le token sur la ligne :

```env
BOT_TOKEN=collez_le_token_ici
```

11. Enregistrez le fichier.

## 2. Obtenir une clé Etherscan gratuite — optionnel

📋 **ACTION HUMAINE REQUISE — Étape 2 sur 5**

Cette clé améliore l’analyse des contrats EVM.

1. Ouvrez <https://etherscan.io>.
2. Cliquez sur **Sign In**.
3. Créez un compte gratuit.
4. Après connexion, ouvrez votre profil.
5. Cliquez sur **API Keys**.
6. Cliquez sur **Add**.
7. Donnez un nom, par exemple `CryptoPulse`.
8. Copiez la clé.
9. Ajoutez-la dans `.env` :

```env
ETHERSCAN_API_KEY=votre_cle_ici
```

## 3. Obtenir une clé Helius gratuite — optionnel

📋 **ACTION HUMAINE REQUISE — Étape 3 sur 5**

Cette clé améliore les données Solana.

1. Ouvrez <https://www.helius.dev>.
2. Créez un compte gratuit.
3. Créez une clé API.
4. Copiez la clé.
5. Ajoutez-la dans `.env` :

```env
HELIUS_API_KEY=votre_cle_ici
```

## 4. Créer Supabase — optionnel en local, recommandé en production

📋 **ACTION HUMAINE REQUISE — Étape 4 sur 5**

1. Ouvrez <https://supabase.com>.
2. Créez un compte gratuit.
3. Cliquez sur **New project**.
4. Choisissez un nom, par exemple `cryptopulse`.
5. Choisissez un mot de passe de base de données et conservez-le en dehors du code.
6. Attendez la création du projet.
7. Ouvrez **Project Settings**.
8. Ouvrez **API**.
9. Copiez `Project URL`.
10. Copiez la clé `anon public`.
11. Ajoutez-les dans `.env` :

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=votre_cle_anon
```

12. Dans Supabase, ouvrez **SQL Editor**.
13. Copiez le contenu de `database/migrations/0001_initial.sql`.
14. Collez-le dans l’éditeur SQL.
15. Cliquez sur **Run**.

## 5. Lancer le bot

📋 **ACTION HUMAINE REQUISE — Étape 5 sur 5**

1. Ouvrez un terminal dans le dossier du projet.
2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Lancez :

```bash
python main.py
```

4. Ouvrez Telegram.
5. Cherchez le nom d’utilisateur de votre bot.
6. Envoyez `/start`.

## Variables disponibles

Voir `.env.example`. Ne partagez jamais votre fichier `.env`.

## Dépannage simple

- **Le bot ne démarre pas** : vérifiez que `BOT_TOKEN` est rempli dans `.env`.
- **Le bot démarre mais certaines données sont absentes** : c’est normal si les clés optionnelles ne sont pas configurées.
- **Supabase ne fonctionne pas** : utilisez d’abord le mode local SQLite, puis vérifiez `SUPABASE_URL` et `SUPABASE_ANON_KEY`.
- **Render se met en veille** : configurez UptimeRobot sur `/health`.
