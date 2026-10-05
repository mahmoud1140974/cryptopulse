# PROJECT_PLAN.md — CryptoPulse

**Statut :** APPROUVÉ — Phase 0 + Phase 1  
**Date :** 2026-10-05  
**Projet :** CryptoPulse — bot Telegram SaaS d’analyse de risque de tokens et d’intelligence de marché crypto  
**Mode de travail après validation :** autonome, par phases, avec tests avant chaque passage à la phase suivante

---

## 1. Résumé exécutif

CryptoPulse sera un bot Telegram production-ready permettant à un utilisateur d’envoyer une adresse de contrat ou, plus tard, une adresse de wallet, puis de recevoir une analyse structurée : prix, liquidité, activité, concentration des holders, signaux de risque contractuels, score de risque transparent, watchlist et alertes.

L’objectif du MVP est de livrer d’abord une **Phase 1 complète et fiable** :

- scan de token par adresse de contrat ;
- détection EVM / Solana ;
- récupération de données gratuites avec providers de secours ;
- scoring de risque transparent ;
- watchlist limitée ;
- alertes basiques par scheduler ;
- interface Telegram claire avec boutons inline ;
- documentation complète pour un propriétaire non-codeur ;
- tests automatisés avant toute phase suivante.

Aucune fonctionnalité payante ne sera utilisée. Si une donnée n’est pas disponible gratuitement, le bot affichera explicitement `Data unavailable.` ou une fonctionnalité dégradée, sans inventer de valeur.

---

## 2. Résultat de l’inspection préalable

Conformément à l’instruction utilisateur, le dépôt `mahmoud1140974/crypto-bot` est totalement ignoré et ne doit plus être modifié.

À ce stade :

- le projet est traité comme un **projet greenfield** ;
- aucun fichier existant du nouveau projet n’a été identifié ;
- aucun fichier ne sera écrasé ;
- un nouveau dépôt GitHub séparé est utilisé uniquement après autorisation explicite.

---

## 3. Contraintes non négociables

### Budget

- 0 $.
- Aucun service payant.
- Aucune carte bancaire.
- Aucune API payante.
- Utilisation exclusive de niveaux gratuits ou d’outils open source.

### Sécurité

- Aucun secret dans le code.
- Aucun secret dans Git.
- `.env`, `*.env`, bases locales, dossiers de dépendances et artefacts de build exclus via `.gitignore`.
- Les erreurs et logs ne doivent jamais afficher de token ou clé API.
- Accès admin uniquement par `ADMIN_TELEGRAM_ID`.

### Fiabilité

- Aucune donnée inventée.
- Si une API est indisponible : message clair à l’utilisateur.
- Tous les appels externes auront timeout, retry limité, backoff, cache et fallback quand c’est possible.
- Le bot doit démarrer avec seulement `BOT_TOKEN`; les autres clés activent des fonctions supplémentaires.

### Conformité UX / disclaimers

Chaque analyse se terminera par :

> Crypto assets are highly risky. This tool provides data and risk indicators for informational purposes only and does not constitute financial advice.

Le bot ne dira jamais qu’un token est « sûr ». Il fournira uniquement des indicateurs.

---

## 4. Architecture technique prévue

| Composant | Choix | Raison |
|---|---|---|
| Langage | Python 3.11+ | Écosystème crypto/Telegram adapté |
| Bot Telegram | aiogram v3 | Async, moderne, inline keyboards |
| Base de données | Supabase PostgreSQL free tier | Gratuit, managé |
| Base locale | SQLite | Développement local simple |
| Scheduler | APScheduler | Pas de Redis payant |
| Cache | cachetools TTL | Simple et gratuit |
| Hosting cible | Render free tier | Compatible budget 0 $ |
| Monitoring | UptimeRobot free tier | Ping HTTP gratuit |
| Tests | pytest + pytest-asyncio | Standard Python |

---

## 5. Arborescence prévue

```text
cryptopulse/
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── PROVIDERS.md
├── SETUP.md
├── PROJECT_PLAN.md
├── requirements.txt
├── Dockerfile
├── main.py
├── config.py
├── database/
├── bot/
├── providers/
├── analysis/
├── alerts/
├── utils/
└── tests/
```

---

## 6. Variables d’environnement prévues

```env
BOT_TOKEN=
ETHERSCAN_API_KEY=
HELIUS_API_KEY=
COINGECKO_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
ADMIN_TELEGRAM_ID=
FREE_SCAN_LIMIT=10
FREE_WATCHLIST_LIMIT=5
FREE_ALERT_INTERVAL_MINUTES=15
LOG_LEVEL=INFO
```

Règles :

- `BOT_TOKEN` est le seul secret obligatoire.
- Les clés optionnelles manquantes dégradent proprement les fonctionnalités.
- Les valeurs réelles seront uniquement dans `.env` ou dans les variables Render, jamais dans Git.

---

## 7. Stratégie de providers gratuits

### Prix / liquidité / pairs DEX

1. DexScreener — provider principal, gratuit, sans clé.
2. CoinGecko Demo API — fallback marché et prix.
3. CoinMarketCap Trial Pro — seulement si l’accès gratuit est confirmé.

### Contrats et on-chain EVM

1. Etherscan API V2 — provider principal multi-chain si clé fournie.
2. Blockscout API — fallback open-source multi-chain.

### Solana

1. Solana Tracker Data API.
2. Helius RPC free tier.

### Marché / trending

1. DexScreener trending / newest / pairs.
2. CoinGecko `/coins/markets`.

### News

1. CryptoPanic free tier si disponible.
2. RSS gratuits via `feedparser`.
3. Si aucune source gratuite fiable ne fonctionne, la fonctionnalité News sera reportée.

---

## 8. Modèle de données prévu

Tables principales :

- `users`
- `scans`
- `watchlist`
- `alerts`
- `alert_state` ou colonnes équivalentes dans `watchlist`
- `subscriptions`
- `admin_logs`

Règles :

- migrations SQL versionnées ;
- Supabase en production ;
- SQLite en local ;
- limites appliquées côté serveur.

---

## 9. Moteur de scoring de risque

| Facteur | Poids | Source | Niveau |
|---|---:|---|---|
| Liquidité < 10 000 $ | 15 | DexScreener | Risque élevé |
| Top 10 holders > 50 % | 20 | Etherscan / Solana Tracker | Risque élevé |
| Contrat non vérifié | 10 | Etherscan | Risque moyen |
| Fonction mint présente | 15 | ABI | Risque élevé |
| Fonction blacklist présente | 10 | ABI | Risque élevé |
| Ownership non renounced | 10 | ABI + owner() | Risque moyen |
| Token âgé de moins de 7 jours | 8 | Timestamp pair | Risque moyen |
| Volume 24h < 1 000 $ | 7 | DexScreener | Liquidité faible |
| Buy/sell tax > 10 % | 10 | Honeypot.is si disponible | Risque élevé |
| Honeypot détecté | 25 | Honeypot.is si disponible | Risque extrême |
| Proxy / upgradeable | 8 | ABI | Risque moyen |
| Freeze authority active Solana | 15 | Solana Tracker | Risque élevé |

### Bandes de score

- `0–20` : 🟢 LOW RISK
- `21–45` : 🟡 MEDIUM RISK
- `46–70` : 🟠 HIGH RISK
- `71–100` : 🔴 EXTREME RISK

Si une source est indisponible, le facteur correspondant sera marqué `Data unavailable.` et ne sera pas inventé.

---

## 10. Plan par phases

### Phase 0 — Pré-flight et fondations

Livrables : `.gitignore`, `.env.example`, `requirements.txt`, docs, structure, Dockerfile.

Critères : secrets protégés, docs claires, installation possible.

### Phase 1 — MVP : scanner + watchlist + alertes basiques

Fonctionnalités : menu Telegram, scan, score, watchlist, alertes 15 minutes, boutons inline, messages sûrs.

Tests : validation, scoring, fallback, formatage, CRUD, rate limiter.

Critère de fin : tous les tests passent et le bot fonctionne avec au moins `BOT_TOKEN`.

### Phase 2 — Wallet analysis + whale tracking + market

Fonctionnalités : wallet, balances, whale alerts, trending, market, news gratuites.

### Phase 3 — Monétisation + admin

Fonctionnalités : plans, limites, Telegram Stars, admin commands, logs.

### Phase 4 — Optimisation, multi-chain, scaling

Fonctionnalités : ajout de chains, caches, retries, health, UptimeRobot, Oracle migration.

---

## 11. Tests et qualité

Outils : `pytest`, `pytest-asyncio`, `unittest.mock`, fixtures JSON.

Règles :

- aucun appel réseau réel dans les tests unitaires ;
- providers mockés ;
- messages Telegram testés sur données manquantes ;
- limites utilisateurs testées ;
- aucune erreur ne doit contenir de secret.

---

## 12. Documentation prévue

- `README.md`
- `SETUP.md`
- `ARCHITECTURE.md`
- `PROVIDERS.md`

---

## 13. Actions humaines prévues

- création du bot Telegram via @BotFather ;
- récupération des clés API gratuites ;
- création Supabase ;
- configuration Render ;
- configuration UptimeRobot ;
- configuration payout Telegram Stars si Phase 3 activée.

---

## 14. Risques identifiés et mitigations

| Risque | Mitigation |
|---|---|
| API gratuite indisponible | fallback provider, cache, message clair |
| Clé API absente | fonctionnalité dégradée, pas de crash |
| Render free tier se met en veille | UptimeRobot ping, documentation |
| Supabase non configuré | mode réduit, SQLite local |
| Données holders indisponibles | `Data unavailable.` |
| Telegram Stars payout complexe | documentation guidée en Phase 3 |
| Rate limits | cache TTL, retry, backoff, limites |
| Fausses news | skip si aucune source gratuite fiable |

---

## 15. Ordre d’exécution après approbation

1. Créer la structure du nouveau projet.
2. Créer `.gitignore`, `.env.example`, docs initiales.
3. Implémenter validation, config, logging sécurisé.
4. Implémenter providers et fallback manager.
5. Implémenter scoring et tests du scoring.
6. Implémenter base de données et migrations.
7. Implémenter handlers Telegram et claviers.
8. Implémenter watchlist.
9. Implémenter alert engine et scheduler.
10. Exécuter tous les tests Phase 1.
11. Corriger les échecs.
12. Finaliser documentation Phase 1.
13. Commit propre.
14. Attendre validation avant Phase 2.

---

## 16. Points validés

1. Nouveau projet vide, sans toucher à l’ancien dépôt.
2. Phase 0 + Phase 1 uniquement.
3. Python 3.11+ / aiogram v3 / Supabase / SQLite local / APScheduler / cachetools / Render free tier.
4. Aucun paiement avant la Phase 3.
5. Nouveau dépôt GitHub uniquement après autorisation explicite.

---

## 17. Approbation

Plan approuvé par l’utilisateur :

**APPROUVÉ — Phase 0 + Phase 1**
