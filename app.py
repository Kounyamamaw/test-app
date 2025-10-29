from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre-cle-secrete-changez-moi')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== MODÈLES ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)  # ⬅️ NOUVEAU CHAMP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ==================== DÉCORATEURS ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Accès refusé. Droits administrateur requis.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES PUBLIQUES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # ✅ VÉRIFICATION D'APPROBATION
            if not user.is_approved:
                flash('Votre compte est en attente d\'approbation. Vous recevrez un email quand il sera activé.', 'warning')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            if user.is_admin:
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur existe déjà', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé', 'danger')
            return redirect(url_for('register'))
        
        # ✅ CRÉATION AVEC is_approved=False
        new_user = User(username=username, email=email, is_approved=False)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # ✅ NOUVEAU MESSAGE
        flash('Compte créé avec succès ! Votre compte est en attente d\'approbation (sous 24h).', 'info')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('index'))

# ==================== ROUTES UTILISATEUR ====================
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Route pour l'analyse des actifs boursiers"""
    try:
        ticker = request.form.get('ticker', '').upper()
        
        if not ticker:
            return jsonify({'error': 'Veuillez entrer un symbole boursier'}), 400
        
        # Importer le module d'analyse
        from analysis import analyze_stock
        
        # Effectuer l'analyse
        result = analyze_stock(ticker)
        
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Erreur lors de l\'analyse')}), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES ADMIN ====================
@app.route('/admin')
@admin_required
def admin_panel():
    # ✅ SÉPARATION PENDING / APPROVED
    all_users = User.query.all()
    pending_users = User.query.filter_by(is_approved=False).all()
    approved_users = User.query.filter_by(is_approved=True).all()
    approved_count = len(approved_users)
    
    return render_template('admin.html', 
                         users=all_users,
                         pending_users=pending_users,
                         approved_users=approved_users,
                         approved_count=approved_count)

@app.route('/admin/add_user', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == 'on'
    auto_approve = request.form.get('auto_approve') == 'on'  # ✅ NOUVEAU
    
    if User.query.filter_by(username=username).first():
        flash('Ce nom d\'utilisateur existe déjà', 'danger')
        return redirect(url_for('admin_panel'))
    
    # ✅ CRÉATION AVEC auto_approve
    new_user = User(username=username, email=email, is_admin=is_admin, is_approved=auto_approve)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    flash(f'Utilisateur {username} créé avec succès', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Empêcher la suppression de son propre compte
    if user.id == session['user_id']:
        flash('Vous ne pouvez pas supprimer votre propre compte', 'danger')
        return redirect(url_for('admin_panel'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Utilisateur {user.username} supprimé', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "administrateur" if user.is_admin else "utilisateur standard"
    flash(f'{user.username} est maintenant {status}', 'success')
    return redirect(url_for('admin_panel'))

# ==================== NOUVELLES ROUTES D'APPROBATION ====================

@app.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@admin_required
def approve_user(user_id):
    """Approuve un compte en attente"""
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    flash(f'Compte de {user.username} approuvé avec succès !', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/reject_user/<int:user_id>', methods=['POST'])
@admin_required
def reject_user(user_id):
    """Rejette un compte en attente (supprime le user)"""
    user = User.query.get_or_404(user_id)
    
    # Empêcher de se rejeter soi-même
    if user.id == session['user_id']:
        flash('Vous ne pouvez pas rejeter votre propre compte', 'danger')
        return redirect(url_for('admin_panel'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Compte de {username} rejeté et supprimé', 'warning')
    return redirect(url_for('admin_panel'))

@app.route('/admin/revoke_user/<int:user_id>', methods=['POST'])
@admin_required
def revoke_user(user_id):
    """Révoque l'accès d'un utilisateur (le repasse en non-approuvé)"""
    user = User.query.get_or_404(user_id)
    
    # Empêcher de se révoquer soi-même
    if user.id == session['user_id']:
        flash('Vous ne pouvez pas révoquer votre propre compte', 'danger')
        return redirect(url_for('admin_panel'))
    
    user.is_approved = False
    db.session.commit()
    
    flash(f'Accès révoqué pour {user.username}', 'warning')
    return redirect(url_for('admin_panel'))

# ==================== INITIALISATION ====================
def init_db():
    with app.app_context():
        db.create_all()
        
        # Créer un admin par défaut si aucun utilisateur n'existe
        if User.query.count() == 0:
            admin = User(username='admin', email='admin@example.com', is_admin=True, is_approved=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin par défaut créé - Username: admin, Password: admin123")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)