@echo off
REM Script de démarrage rapide pour Trading Analysis App (Windows)

echo ==================================================
echo 🚀 Trading Analysis App - Démarrage rapide
echo ==================================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    echo    Installez Python depuis : https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python détecté : %PYTHON_VERSION%
echo.

REM Créer environnement virtuel si nécessaire
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
    echo ✅ Environnement virtuel créé
) else (
    echo ✅ Environnement virtuel existant
)

echo.

REM Activer l'environnement virtuel
echo 🔌 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.

REM Installer les dépendances
echo 📥 Installation des dépendances...
pip install -r requirements.txt --quiet

echo ✅ Dépendances installées
echo.

REM Créer .env si nécessaire
if not exist ".env" (
    echo 🔑 Création du fichier .env...
    copy .env.example .env
    echo ✅ Fichier .env créé
    echo ⚠️  N'oubliez pas de modifier SECRET_KEY dans .env
    echo.
)

REM Tester l'application
echo 🧪 Test de l'application...
python test_app.py

if errorlevel 1 (
    echo.
    echo ❌ Des erreurs ont été détectées
    echo    Vérifiez les messages ci-dessus
    pause
    exit /b 1
)

echo.
echo ==================================================
echo ✅ L'application est prête !
echo ==================================================
echo.
echo 🚀 Démarrage du serveur...
echo.
echo 📍 URL : http://localhost:5000
echo 👤 Admin : username = admin, password = admin123
echo.
echo ⚠️  Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo ==================================================
echo.

REM Lancer l'application
python app.py

pause
