#!/bin/bash

# Script de démarrage rapide pour Trading Analysis App
# Usage: ./start.sh

echo "=================================================="
echo "🚀 Trading Analysis App - Démarrage rapide"
echo "=================================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "   Installez Python depuis : https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python détecté : $(python3 --version)"
echo ""

# Créer environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant"
fi

echo ""

# Activer l'environnement virtuel
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

echo ""

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt --quiet

echo "✅ Dépendances installées"
echo ""

# Créer .env si nécessaire
if [ ! -f ".env" ]; then
    echo "🔑 Création du fichier .env..."
    cp .env.example .env
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/votre-cle-secrete-super-longue-et-aleatoire-changez-moi/$SECRET_KEY/" .env
    rm .env.bak 2>/dev/null
    echo "✅ Fichier .env créé avec SECRET_KEY aléatoire"
    echo ""
fi

# Tester l'application
echo "🧪 Test de l'application..."
python3 test_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ L'application est prête !"
    echo "=================================================="
    echo ""
    echo "🚀 Démarrage du serveur..."
    echo ""
    echo "📍 URL : http://localhost:5000"
    echo "👤 Admin : username = admin, password = admin123"
    echo ""
    echo "⚠️  Appuyez sur Ctrl+C pour arrêter le serveur"
    echo ""
    echo "=================================================="
    echo ""
    
    # Lancer l'application
    python3 app.py
else
    echo ""
    echo "❌ Des erreurs ont été détectées"
    echo "   Vérifiez les messages ci-dessus"
    exit 1
fi
