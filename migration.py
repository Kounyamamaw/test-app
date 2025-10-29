"""
MIGRATION - Ajout du système d'approbation
Adapté pour trading_app.db et le modèle User existant
"""

import sqlite3
import os

def migrate_database():
    """Ajoute la colonne is_approved à la table user"""
    
    # Chemin de ta base de données
    db_path = './instance/trading_app.db'
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée!")
        print(f"   Chemin attendu: {os.path.abspath(db_path)}")
        print("\n💡 Solution: Lance d'abord ton app.py pour créer la base:")
        print("   python app.py")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Colonnes actuelles: {columns}")
        
        if 'is_approved' in columns:
            print("✅ La colonne 'is_approved' existe déjà!")
            conn.close()
            return True
        
        # Ajouter la colonne
        print("\n📝 Ajout de la colonne 'is_approved'...")
        cursor.execute("""
            ALTER TABLE user 
            ADD COLUMN is_approved BOOLEAN DEFAULT 0
        """)
        
        # Approuver automatiquement tous les comptes existants
        print("🔓 Approbation automatique des comptes existants...")
        cursor.execute("""
            UPDATE user 
            SET is_approved = 1
        """)
        
        conn.commit()
        
        # Vérifier le résultat
        cursor.execute("SELECT username, is_approved FROM user")
        users = cursor.fetchall()
        
        print(f"\n✅ Migration réussie !")
        print(f"   {len(users)} compte(s) approuvé(s) automatiquement:")
        for username, approved in users:
            status = "✅" if approved else "❌"
            print(f"   {status} {username}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🔧 MIGRATION - Système d'approbation")
    print("   Base de données: trading_app.db")
    print("="*60)
    print()
    
    success = migrate_database()
    
    if success:
        print("\n" + "="*60)
        print("🎉 Migration terminée avec succès!")
        print("="*60)
        print("\n📋 Prochaines étapes:")
        print("   1. Remplace app.py par app_UPDATED.py")
        print("   2. Remplace templates/admin.html par admin_UPDATED.html")
        print("   3. Redémarre l'application")
        print("   4. Va sur /admin pour voir les nouveautés")
        print()
    else:
        print("\n❌ La migration a échoué.")
        print("   Assure-toi que l'app a été lancée au moins une fois.")
        print()
