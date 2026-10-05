# ARCHITECTURE.md — CryptoPulse

## Vue d’ensemble

CryptoPulse est organisé en couches indépendantes :

1. **Telegram bot** (`bot/`) : commandes, menus, boutons inline, middlewares.
2. **Analyse** (`analysis/`) : orchestration, analyse de contrat, scoring.
3. **Providers** (`providers/`) : APIs gratuites avec fallback.
4. **Base de données** (`database/`) : SQLite local ou Supabase PostgreSQL.
5. **Alertes** (`alerts/`) : scheduler APScheduler et moteur de détection.
6. **Utils** (`utils/`) : validation et formatage.

## Choix techniques

### Python 3.11+

Python offre un bon écosystème Telegram et crypto, avec un code facile à tester et à faire évoluer.

### aiogram v3

aiogram est async, moderne, et adapté aux menus inline et callbacks Telegram.

### Supabase + SQLite

- Supabase PostgreSQL est utilisé en production free tier.
- SQLite est utilisé automatiquement en local si Supabase n’est pas configuré.
- Le code expose une interface `Database` commune.

### APScheduler

APScheduler tourne dans le processus du bot. Cela évite Redis ou un worker payant.

### cachetools

Les réponses courtes sont mises en cache en mémoire. Le cache n’est pas persistant et ne contient pas de secrets.

## Flux d’analyse de token

1. L’utilisateur envoye une adresse.
2. `utils/validators.py` détecte EVM ou Solana.
3. `TokenAnalyzer` demande un snapshot de marché via la chaîne de fallback.
4. Des données complémentaires sont demandées en parallèle : holders, contrat, autorité Solana.
5. Les champs disponibles sont fusionnés.
6. `risk_scorer.py` applique des poids documentés.
7. `formatters.py` affiche un message Telegram avec `Data unavailable.` si nécessaire.

## Gestion des erreurs

- Timeout sur chaque requête HTTP.
- Retry limité avec backoff.
- Fallback provider.
- Exceptions providers converties en message utilisateur sûr.
- Erreurs internes enregistrées sans secret.

## Limites Free

- 10 scans/jour.
- 5 tokens en watchlist.
- alertes toutes les 15 minutes.
- 5 commandes par 10 secondes par utilisateur.

Ces limites seront étendues en Phase 3 avec les plans Pro et Premium.

## Sécurité

- `.env` et fichiers de secrets exclus par `.gitignore`.
- Aucun secret n’est écrit dans les logs.
- L’accès admin futur sera basé uniquement sur `ADMIN_TELEGRAM_ID`.
- Les entrées utilisateur sont validées avant tout appel provider.
