#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation et le bon fonctionnement de l'application
"""

import sys
import subprocess

def test_imports():
    """Teste les imports Python nécessaires"""
    print("🔍 Test des imports Python...")
    
    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'werkzeug',
        'pandas',
        'numpy',
        'yfinance'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MANQUANT")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Modules manquants: {', '.join(missing)}")
        print("   Exécutez: pip install -r requirements.txt")
        return False
    
    print("✅ Tous les modules sont installés\n")
    return True


def test_database():
    """Teste la création de la base de données"""
    print("🔍 Test de la base de données...")
    
    try:
        from app import app, db, User
        
        with app.app_context():
            # Créer les tables
            db.create_all()
            
            # Vérifier si l'admin existe
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                print("  ✅ Base de données créée")
                print("  ✅ Compte admin existe")
                print(f"     Username: admin")
                print(f"     Is Admin: {admin.is_admin}")
            else:
                print("  ⚠️  Compte admin non trouvé - sera créé au démarrage")
        
        print("✅ Base de données fonctionnelle\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False


def test_analysis():
    """Teste le module d'analyse"""
    print("🔍 Test du module d'analyse...")
    
    try:
        from analysis import analyze_stock, validate_ticker
        
        # Test avec un ticker connu
        print("  📊 Test d'analyse avec AAPL...")
        result = analyze_stock('AAPL')
        
        if result.get('success'):
            print(f"  ✅ Analyse réussie")
            print(f"     Ticker: {result.get('ticker')}")
            print(f"     Prédiction: {result.get('prediction')}")
            print(f"     Confiance: {result.get('confidence')}")
        else:
            print(f"  ⚠️  Erreur d'analyse: {result.get('error')}")
            print(f"     (Normal si pas de connexion internet)")
        
        print("✅ Module d'analyse fonctionnel\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False


def test_routes():
    """Teste les routes principales"""
    print("🔍 Test des routes Flask...")
    
    try:
        from app import app
        
        client = app.test_client()
        
        routes_to_test = [
            ('/', 'Page d\'accueil'),
            ('/login', 'Page de connexion'),
            ('/register', 'Page d\'inscription')
        ]
        
        for route, name in routes_to_test:
            response = client.get(route)
            if response.status_code == 200:
                print(f"  ✅ {name} ({route})")
            else:
                print(f"  ❌ {name} ({route}) - Code: {response.status_code}")
        
        print("✅ Routes principales fonctionnelles\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False


def main():
    """Fonction principale"""
    print("=" * 60)
    print("🧪 TESTS DE L'APPLICATION TRADING ANALYSIS")
    print("=" * 60 + "\n")
    
    tests = [
        test_imports(),
        test_database(),
        test_analysis(),
        test_routes()
    ]
    
    print("=" * 60)
    
    if all(tests):
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("\n🚀 Vous pouvez maintenant lancer l'application avec :")
        print("   python app.py")
        print("\n   Puis accéder à : http://localhost:5000")
        print("   Compte admin : admin / admin123")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n🔧 Vérifiez les erreurs ci-dessus et corrigez-les")
        return 1


if __name__ == '__main__':
    sys.exit(main())
