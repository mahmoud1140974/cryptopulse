# PROVIDERS.md — Providers gratuits et fallback

CryptoPulse ne dépend jamais d’une seule API. Chaque type de données utilise une chaîne de fallback quand c’est possible.

## Token / prix / liquidité

### 1. DexScreener

- URL : <https://api.dexscreener.com/latest/dex/tokens/{address}>
- Gratuit, sans clé.
- Utilisé pour pairs DEX, prix, liquidité, volume 24h, transactions et date de pair.

### 2. CoinGecko Demo API

- URL : <https://api.coingecko.com/api/v3>
- Utilisé en fallback pour prix, market cap, volume et données globales.
- La clé `COINGECKO_API_KEY` est optionnelle.

### 3. CoinMarketCap Trial Pro

- Prévu uniquement si l’accès gratuit est confirmé pendant l’implémentation.
- Non requis pour la Phase 1.

## Contrats EVM

### 1. Etherscan API V2

- Clé optionnelle `ETHERSCAN_API_KEY`.
- Utilisé pour source vérifiée, ABI et signaux de risque.
- Si la clé est absente, l’analyse contractuelle affiche des données indisponibles sans crasher.

### 2. Blockscout

- Prévu comme fallback open-source.
- Ajouté si nécessaire après validation des endpoints par chain.

## Solana

### 1. Solana Tracker Data API

- Utilisé pour métadonnées, holders et signaux Solana quand disponible.

### 2. Helius RPC

- Clé optionnelle `HELIUS_API_KEY`.
- Utilisé pour données RPC Solana.

## Données indisponibles

Si aucun provider gratuit ne fournit une donnée, le bot affiche :

```text
Data unavailable.
```

Il ne doit jamais inventer de prix, de holders, de liquidité ou de score.

## Cache

- Prix et snapshots token : 60 secondes.
- Contrats : prévu 300 secondes.
- Métadonnées : prévu 3600 secondes.

## Rate limits

Le bot limite aussi les utilisateurs :

- 5 commandes / 10 secondes.
- 10 scans / jour en Free.
- 5 tokens en watchlist Free.

Ces limites protègent les APIs gratuites.
