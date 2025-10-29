# 📈 Trading Analysis Platform

Application Flask complète pour l'analyse de cycles financiers avec système d'authentification et panel admin.

## 🚀 Fonctionnalités

- ✅ Authentification utilisateur (login/register/logout)
- ✅ Dashboard d'analyse des actifs boursiers
- ✅ Panel administrateur (gestion des utilisateurs)
- ✅ Base de données SQLite (facilement migratable vers PostgreSQL)
- ✅ Interface moderne et responsive (Bootstrap 5)
- ✅ Système de sessions sécurisé

## 📋 Prérequis

- Python 3.8+
- pip

## 🛠️ Installation locale

1. **Cloner/télécharger le projet**

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
```bash
cp .env.example .env
# Éditez .env et changez SECRET_KEY par une clé aléatoire
```

5. **Lancer l'application**
```bash
python app.py
```

6. **Accéder à l'application**
- Ouvrir : http://localhost:5000
- Compte admin par défaut : 
  - Username: `admin`
  - Password: `admin123`

## 🌐 Déploiement sur Render (Gratuit)

### Option 1 : Via GitHub

1. **Créer un repo GitHub** et pusher le code

2. **Aller sur [render.com](https://render.com)** et se connecter

3. **Créer un nouveau Web Service**
   - Connecter votre repo GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Ajouter les variables d'environnement**
   - `SECRET_KEY` : Générer une clé aléatoire
   - `PYTHON_VERSION` : 3.11.0

5. **Déployer** 🚀

### Option 2 : Via Railway

1. **Aller sur [railway.app](https://railway.app)**

2. **New Project → Deploy from GitHub**

3. Railway détecte automatiquement Flask et configure tout

4. **Ajouter la variable d'environnement**
   - `SECRET_KEY` : votre clé secrète

## 🔧 Migration vers PostgreSQL (Production)

1. **Ajouter psycopg2 dans requirements.txt**
```
psycopg2-binary==2.9.9
```

2. **Modifier app.py**
```python
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///trading_app.db')
```

3. **Render/Railway fournissent PostgreSQL gratuit**
   - Ajouter un service PostgreSQL
   - Utiliser l'URL fournie comme variable d'environnement

## 📁 Structure du projet

```
trading-analysis-app/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── .env.example          # Variables d'environnement (exemple)
├── templates/            # Templates HTML
│   ├── base.html        # Template de base
│   ├── index.html       # Page d'accueil
│   ├── login.html       # Page de connexion
│   ├── register.html    # Page d'inscription
│   ├── dashboard.html   # Dashboard utilisateur
│   └── admin.html       # Panel admin
├── static/              # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   └── js/
└── trading_app.db       # Base de données SQLite (générée auto)
```

## 🔐 Sécurité

- ⚠️ **IMPORTANT** : Changez `SECRET_KEY` en production
- Les mots de passe sont hashés avec Werkzeug
- Sessions sécurisées
- Protection CSRF (à ajouter avec Flask-WTF si besoin)

## 🧩 Intégrer votre code Python d'analyse

Dans `app.py`, modifiez la fonction `analyze()` (ligne ~100) :

```python
@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    ticker = request.form.get('ticker', '').upper()
    
    # REMPLACER CETTE SECTION PAR VOTRE CODE
    # Exemple :
    from your_analysis_module import predict_cycle
    
    result = predict_cycle(ticker)
    
    return jsonify({
        'ticker': ticker,
        'prediction': result['prediction'],
        'confidence': result['confidence'],
        'next_cycle': result['next_cycle']
    })
```

## 🎨 Personnalisation

### Changer les couleurs
Modifier les variables CSS dans `templates/base.html` :
```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #1e40af;
}
```

### Ajouter des fonctionnalités
L'application est modulaire, vous pouvez facilement :
- Ajouter des routes dans `app.py`
- Créer de nouveaux templates
- Ajouter des modèles de base de données

## 📞 Support

Pour toute question, n'hésitez pas !

## 📄 Licence

MIT License - Libre d'utilisation

---

**Prêt pour le déploiement ! 🚀**
