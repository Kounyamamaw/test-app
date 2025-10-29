# 🔧 Guide d'intégration de votre code Python

## 📋 Objectif

Ce guide explique comment intégrer **votre code Python existant** (celui qui tourne actuellement sur PythonAnywhere) dans cette nouvelle application Flask.

---

## 🎯 Localisation du code

Votre code d'analyse doit être intégré dans le fichier : **`analysis.py`**

---

## 🔄 Étapes d'intégration

### 1️⃣ Récupérer votre code actuel

Depuis PythonAnywhere, récupérez :
- Vos fichiers Python d'analyse
- Vos fichiers de modèles ML (si vous en avez)
- Vos dépendances (requirements.txt)

### 2️⃣ Structure actuelle à remplacer

Dans `analysis.py`, remplacez la fonction `analyze_stock()` :

```python
def analyze_stock(ticker: str) -> dict:
    """
    REMPLACER CETTE FONCTION PAR VOTRE CODE
    """
    
    # Votre code ici...
    # Exemple : utilisation de votre modèle
    from votre_module import votre_fonction_prediction
    
    prediction_result = votre_fonction_prediction(ticker)
    
    # La fonction DOIT retourner un dictionnaire avec ce format :
    return {
        'success': True,              # ou False si erreur
        'ticker': ticker,             # Symbole analysé
        'prediction': "...",          # Votre prédiction (texte)
        'confidence': 0.85,           # Confiance (0.0 à 1.0)
        'next_cycle': "15 jours",     # Durée estimée
        'timestamp': datetime.utcnow().isoformat()
    }
```

### 3️⃣ Exemples d'intégration

#### Exemple 1 : Code simple avec pandas

```python
def analyze_stock(ticker: str) -> dict:
    import yfinance as yf
    import pandas as pd
    
    # Votre logique
    data = yf.download(ticker, period="1y")
    
    # Vos calculs de cycles
    cycle_prediction = calculate_cycles(data)  # Votre fonction
    
    return {
        'success': True,
        'ticker': ticker,
        'prediction': cycle_prediction['type'],
        'confidence': cycle_prediction['confidence'],
        'next_cycle': f"{cycle_prediction['days']} jours"
    }
```

#### Exemple 2 : Code avec modèle ML

```python
def analyze_stock(ticker: str) -> dict:
    import joblib
    
    # Charger votre modèle
    model = joblib.load('models/cycle_predictor.pkl')
    
    # Préparer les données
    features = prepare_features(ticker)  # Votre fonction
    
    # Prédiction
    prediction = model.predict(features)
    confidence = model.predict_proba(features).max()
    
    return {
        'success': True,
        'ticker': ticker,
        'prediction': prediction[0],
        'confidence': confidence,
        'next_cycle': calculate_cycle_duration(prediction)
    }
```

#### Exemple 3 : Code avec API externe

```python
def analyze_stock(ticker: str) -> dict:
    import requests
    
    # Appel à votre API/service
    response = requests.post(
        'https://votre-api.com/analyze',
        json={'ticker': ticker}
    )
    
    data = response.json()
    
    return {
        'success': True,
        'ticker': ticker,
        'prediction': data['prediction'],
        'confidence': data['confidence'],
        'next_cycle': data['cycle_duration']
    }
```

---

## 📦 Gestion des dépendances

### Si vous utilisez des bibliothèques supplémentaires :

1. **Ajoutez-les dans `requirements.txt`** :
   ```txt
   # Exemple
   tensorflow==2.13.0
   scikit-learn==1.3.0
   ta-lib==0.4.28
   ```

2. **Pour les bibliothèques système** (comme TA-Lib) :
   - Sur Render/Railway, créer un fichier `packages.txt` :
     ```
     ta-lib
     ```

---

## 🗂️ Organisation des fichiers

### Structure recommandée :

```
trading-analysis-app/
├── app.py                    # Application Flask
├── analysis.py               # VOTRE CODE ICI
├── models/                   # Vos modèles ML (optionnel)
│   ├── cycle_predictor.pkl
│   └── scaler.pkl
├── utils/                    # Fonctions utilitaires (optionnel)
│   ├── data_preparation.py
│   └── indicators.py
├── templates/                # Pages HTML
└── requirements.txt          # Dépendances
```

### Créer des modules supplémentaires :

Si votre code est complexe, divisez-le :

```python
# utils/indicators.py
def calculate_rsi(data):
    # Votre code RSI
    pass

def calculate_macd(data):
    # Votre code MACD
    pass
```

Puis dans `analysis.py` :
```python
from utils.indicators import calculate_rsi, calculate_macd

def analyze_stock(ticker):
    # Utiliser vos fonctions
    rsi = calculate_rsi(data)
    macd = calculate_macd(data)
    # ...
```

---

## 🧪 Tests

### Tester votre intégration localement :

```python
# test_integration.py
from analysis import analyze_stock

# Test avec un ticker réel
result = analyze_stock('AAPL')

print(f"Success: {result['success']}")
print(f"Prédiction: {result['prediction']}")
print(f"Confiance: {result['confidence']}")
```

Ou directement dans Python :
```bash
python -c "from analysis import analyze_stock; print(analyze_stock('AAPL'))"
```

---

## ⚠️ Points d'attention

### 1. Gestion des erreurs
Toujours gérer les erreurs dans votre code :

```python
def analyze_stock(ticker: str) -> dict:
    try:
        # Votre code
        result = complex_analysis(ticker)
        return {'success': True, ...}
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ticker': ticker
        }
```

### 2. Temps de réponse
Si votre analyse prend >30 secondes :
- Optimiser le code
- Utiliser du caching
- Implémenter une queue asynchrone (Celery)

### 3. Données en cache
Pour améliorer les performances :

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_stock_data(ticker, date):
    # Cache les données pour éviter de re-télécharger
    pass
```

### 4. Variables d'environnement
Pour les clés API ou secrets :

```python
import os

API_KEY = os.environ.get('YOUR_API_KEY')
```

Puis sur Render/Railway, ajouter la variable d'environnement.

---

## 🔄 Migration depuis PythonAnywhere

### Étapes complètes :

1. **Télécharger votre code de PythonAnywhere**
   ```bash
   # Via SSH ou l'interface web
   ```

2. **Copier dans le nouveau projet**
   - Mettre le code principal dans `analysis.py`
   - Fichiers supplémentaires dans des dossiers appropriés

3. **Adapter les imports**
   ```python
   # Ancien (PythonAnywhere)
   from myapp.analysis import predict
   
   # Nouveau
   from analysis import analyze_stock
   ```

4. **Tester localement**
   ```bash
   python test_app.py
   python app.py
   ```

5. **Déployer sur Render/Railway**
   - Suivre le guide DEPLOYMENT.md

---

## 📞 Besoin d'aide ?

Si vous avez des questions sur l'intégration :

1. **Partagez votre code actuel** - je peux vous aider à l'adapter
2. **Décrivez les erreurs** que vous rencontrez
3. **Montrez les logs** de l'application

---

## ✅ Checklist d'intégration

- [ ] Code récupéré de PythonAnywhere
- [ ] Fonction `analyze_stock()` remplacée dans `analysis.py`
- [ ] Dépendances ajoutées dans `requirements.txt`
- [ ] Tests locaux réussis
- [ ] Modèles ML copiés (si applicable)
- [ ] Variables d'environnement configurées
- [ ] Déploiement effectué
- [ ] Test de l'analyse sur l'app déployée

---

**Votre code est prêt à être intégré ! 🚀**
