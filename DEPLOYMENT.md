# 🚀 Guide de Déploiement Rapide

## Option 1 : Déploiement sur Render (Recommandé - Gratuit)

### Étapes :

1. **Créer un compte sur [render.com](https://render.com)**

2. **Créer un nouveau Web Service**
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre dépôt GitHub (ou uploadez le code)

3. **Configuration**
   ```
   Name: trading-analysis-app
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Variables d'environnement**
   Ajouter dans l'onglet "Environment" :
   ```
   SECRET_KEY = votre-cle-secrete-aleatoire-ici
   PYTHON_VERSION = 3.11.0
   ```

5. **Déployer**
   - Cliquez sur "Create Web Service"
   - Render va automatiquement déployer votre app
   - URL finale : `https://votre-app.onrender.com`

### ⏱️ Premier déploiement : ~5 minutes

---

## Option 2 : Déploiement sur Railway (Plus rapide)

### Étapes :

1. **Aller sur [railway.app](https://railway.app)**

2. **New Project**
   - "Deploy from GitHub repo"
   - Ou "Deploy from local repo"

3. **Configuration automatique**
   - Railway détecte Flask automatiquement
   - Pas besoin de configurer les commandes

4. **Ajouter variable d'environnement**
   Dans "Variables" :
   ```
   SECRET_KEY = votre-cle-secrete
   ```

5. **Déployer**
   - Railway déploie automatiquement
   - URL : `https://votre-app.up.railway.app`

### ⏱️ Déploiement : ~2 minutes

---

## Option 3 : Déploiement sur Heroku

### Étapes :

1. **Installer Heroku CLI**
   ```bash
   # Sur Mac
   brew tap heroku/brew && brew install heroku
   
   # Sur Windows
   # Télécharger depuis heroku.com
   ```

2. **Connexion**
   ```bash
   heroku login
   ```

3. **Créer l'app**
   ```bash
   cd trading-analysis-app
   heroku create votre-app-name
   ```

4. **Configurer les variables**
   ```bash
   heroku config:set SECRET_KEY=votre-cle-secrete
   ```

5. **Déployer**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

### ⏱️ Déploiement : ~10 minutes

---

## 🔑 Génération d'une clé secrète

Pour générer une SECRET_KEY sécurisée :

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Ou en ligne : https://randomkeygen.com/

---

## 📊 Base de données en production

### Sur Render :
1. Créer un PostgreSQL database (gratuit)
2. Copier l'URL de connexion
3. Ajouter comme variable : `DATABASE_URL`

### Sur Railway :
1. Ajouter un service PostgreSQL
2. Railway le connecte automatiquement

---

## ✅ Vérification post-déploiement

1. **Accéder à l'app** : `https://votre-app.votreplateforme.com`

2. **Tester la connexion admin** :
   - Username: `admin`
   - Password: `admin123`

3. **Changer le mot de passe admin** immédiatement !

---

## 🔧 Dépannage

### Erreur "Application Error"
- Vérifier les logs de la plateforme
- S'assurer que `gunicorn` est dans requirements.txt

### Base de données non créée
- Ajouter une commande de migration dans le déploiement
- Ou utiliser PostgreSQL externe

### Variables d'environnement
- Toujours définir `SECRET_KEY`
- Ne jamais commiter `.env` dans git

---

## 🎯 Checklist avant déploiement

- [ ] Tester localement avec `python app.py`
- [ ] Vérifier que requirements.txt est à jour
- [ ] Générer une SECRET_KEY sécurisée
- [ ] Ajouter .env dans .gitignore
- [ ] Pousser le code sur GitHub
- [ ] Configurer les variables d'environnement
- [ ] Déployer
- [ ] Changer le mot de passe admin

---

## 🌐 Intégration avec Framer

Une fois déployé, dans Framer :

1. **Supprimer l'iframe Infinityfree**

2. **Remplacer par un lien direct** :
   ```
   https://votre-app.onrender.com
   ```

3. **Ou garder une iframe unique** :
   ```html
   <iframe src="https://votre-app.onrender.com" 
           width="100%" height="800px"></iframe>
   ```

---

**Votre app est prête à être déployée ! 🚀**
