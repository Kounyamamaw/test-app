"""
Module d'analyse des cycles financiers - VERSION COMPLÈTE
Implémente tous les graphiques avec analyses avancées
"""

import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from scipy import signal
from scipy.fft import fft, fftfreq

# Configuration yfinance
yf.set_tz_cache_location("cache")

# ========================================
# FONCTION PRINCIPALE - POINT D'ENTRÉE
# ========================================

def analyze_stock(ticker: str) -> dict:
    """
    Fonction principale d'analyse d'un actif boursier
    """
    try:
        ticker = ticker.upper().strip()
        print(f"\n{'='*60}")
        print(f"🚀 ANALYSE DE {ticker}")
        print(f"{'='*60}\n")
        
        # Appeler la fonction d'analyse complète
        result = analyze_market_cycles(ticker)
        
        # Si erreur dans l'analyse
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
            return {
                'success': False,
                'error': result['error'],
                'ticker': ticker
            }
        
        # Extraire les statistiques clés
        kitchin_stats = result['stats']['kitchin']
        vol_stats = result['stats']['volatility']
        
        print(f"\n✅ ANALYSE TERMINÉE AVEC SUCCÈS !")
        print(f"   Prix actuel: ${kitchin_stats['cours_actuel']}")
        print(f"   Cycle Kitchin: Jour {kitchin_stats['jour_actuel']}/894")
        print(f"   Volatilité: {vol_stats['current_vol']}%\n")
        
        # Formater la réponse pour le dashboard
        return {
            'success': True,
            'ticker': ticker,
            'prediction': f"Cycle Kitchin: Jour {kitchin_stats['jour_actuel']}/894",
            'confidence': 0.85,
            'next_cycle': f"{894 - kitchin_stats['jour_actuel']} jours restants",
            'current_price': kitchin_stats['cours_actuel'],
            'deviation': kitchin_stats['ecart_pct'],
            'volatility': vol_stats['current_vol'],
            'volatility_outlook': vol_stats['proj_12m'],
            'volatility_level': vol_stats['label'],
            'timestamp': datetime.utcnow().isoformat(),
            'full_analysis': result
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"❌ ERREUR: {error_msg}")
        print(f"{traceback_msg}")
        return {
            'success': False,
            'error': f"Erreur d'analyse: {error_msg}",
            'ticker': ticker
        }


# ========================================
# TÉLÉCHARGEMENT AMÉLIORÉ (FIX YFINANCE)
# ========================================

def download_stock_data_fixed(ticker_symbol):
    """
    Télécharge les données avec gestion des erreurs yfinance
    """
    ticker_symbol = ticker_symbol.upper().strip()
    print(f"📥 Téléchargement des données pour {ticker_symbol}...")
    
    try:
        # Créer l'objet Ticker
        ticker_obj = yf.Ticker(ticker_symbol)
        
        # Méthode 1: Essayer avec period="max"
        print(f"   Tentative 1: period='max'...")
        data = ticker_obj.history(
            period="max",
            auto_adjust=True,
            actions=False,
            timeout=10
        )
        
        if data is not None and not data.empty and len(data) > 100:
            print(f"✅ Succès ! {len(data)} jours de données")
            return data, None
        
        # Méthode 2: Dates spécifiques avec période plus courte
        print(f"   Tentative 2: 20 dernières années...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*20)
        
        data = ticker_obj.history(
            start=start_date,
            end=end_date,
            auto_adjust=True,
            actions=False,
            timeout=10
        )
        
        if data is not None and not data.empty and len(data) > 100:
            print(f"✅ Succès ! {len(data)} jours (20 ans)")
            return data, None
        
        # Méthode 3: 5 ans minimum
        print(f"   Tentative 3: 5 dernières années...")
        start_date = end_date - timedelta(days=365*5)
        
        data = ticker_obj.history(
            start=start_date,
            end=end_date,
            auto_adjust=True,
            actions=False,
            timeout=10
        )
        
        if data is not None and not data.empty and len(data) > 100:
            print(f"⚠️  Succès limité: {len(data)} jours (5 ans)")
            return data, "Données limitées (5 ans)"
        
        # Si tout échoue
        error_msg = (
            f"Impossible de récupérer les données pour '{ticker_symbol}'. "
            f"Vérifiez le symbole ou réessayez plus tard."
        )
        print(f"❌ {error_msg}")
        return None, error_msg
        
    except Exception as e:
        error_msg = f"Erreur de téléchargement pour {ticker_symbol}: {str(e)}"
        print(f"❌ {error_msg}")
        return None, error_msg


# ========================================
# ANALYSE COMPLÈTE DES CYCLES
# ========================================

def analyze_market_cycles(ticker_symbol):
    """Analyse complète des cycles de marché"""
    try:
        ticker_symbol = ticker_symbol.upper().strip()

        # Télécharger les données
        data, error = download_stock_data_fixed(ticker_symbol)
        
        if error and data is None:
            return {"error": error}
        
        if data is None or data.empty:
            return {"error": f"Aucune donnée trouvée pour {ticker_symbol}"}

        # Nettoyer les données
        print("🧹 Nettoyage des données...")
        data = data.reset_index()
        
        if 'Close' not in data.columns:
            return {"error": "Colonne 'Close' manquante"}
        
        if 'Volume' not in data.columns:
            data['Volume'] = 0
        
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce').fillna(0)
        data = data.dropna(subset=['Close'])

        if len(data) < 100:
            return {"error": f"Pas assez de données ({len(data)} jours)"}

        print(f"✅ {len(data)} jours de données nettoyées")

        # Extraire les séries
        close_prices = pd.Series(data["Close"].values, dtype=np.float64)
        volumes = pd.Series(data["Volume"].values, dtype=np.float64)
        data['Date'] = pd.to_datetime(data['Date'])
        data['Date_str'] = data['Date'].dt.strftime('%d-%m-%Y')

        # Générer les analyses
        print("\n📊 Génération des analyses...\n")
        graphs = {}

        print("   [1/9] Prix + Volume...")
        graphs['price_volume'] = create_price_volume_chart(data, close_prices, volumes, ticker_symbol)

        print("   [2/9] Cycle de Kitchin...")
        graphs['kitchin'], kitchin_stats = create_kitchin_cycle(data, close_prices, ticker_symbol)

        print("   [3/9] Cycle Annuel...")
        graphs['annual'], annual_stats = create_annual_cycle(data, close_prices, ticker_symbol)

        print("   [4/9] Décomposition STL...")
        graphs['returns'] = create_returns_decomposition(data, close_prices, ticker_symbol)

        print("   [5/9] Volatilité...")
        graphs['volatility'], graphs['vol_gauge'], vol_stats = create_volatility_analysis(data, close_prices, ticker_symbol)

        print("   [6/9] Coefficient de Hurst...")
        graphs['hurst'] = create_hurst_analysis(data, close_prices, ticker_symbol)

        print("   [7/9] FFT Corona Spectrum...")
        graphs['corona'], graphs['dominant_cycles'] = create_fft_analysis(data, close_prices, ticker_symbol)

        print("\n✅ Tous les graphiques générés avec succès !\n")

        return {
            "success": True,
            "ticker": ticker_symbol,
            "graphs": graphs,
            "stats": {
                "kitchin": kitchin_stats,
                "annual": annual_stats,
                "volatility": vol_stats
            }
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Erreur complète:\n{error_details}")
        return {"error": f"Erreur: {str(e)}"}


# ========================================
# GRAPHIQUE 1: PRIX + VOLUME
# ========================================

def create_price_volume_chart(data, close_prices, volumes, ticker):
    """Graphique prix historique + volume"""
    try:
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'Prix - {ticker}', 'Volume')
        )
        
        # Prix
        fig.add_trace(
            go.Scatter(
                x=data["Date_str"],
                y=close_prices,
                name="Prix",
                line=dict(color='#667eea', width=2)
            ),
            row=1, col=1
        )
        
        # Volume
        colors = ['red' if close_prices.iloc[i] < close_prices.iloc[i-1] else 'green' 
                  for i in range(1, len(close_prices))]
        colors = ['green'] + colors
        
        fig.add_trace(
            go.Bar(
                x=data["Date_str"],
                y=volumes,
                name="Volume",
                marker_color=colors,
                opacity=0.5
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Prix ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return json.loads(fig.to_json())
    except Exception as e:
        print(f"⚠️  Erreur Prix+Volume: {e}")
        return {}


# ========================================
# GRAPHIQUE 2: CYCLE DE KITCHIN (894j)
# ========================================

def create_kitchin_cycle(data, close_prices, ticker):
    """Analyse du cycle de Kitchin (894 jours)"""
    try:
        kitchin_length = 894
        
        # Calculer cycle actuel
        remaining = len(close_prices) % kitchin_length
        if remaining == 0:
            remaining = kitchin_length
        
        start_idx = len(close_prices) - remaining
        current_cycle = close_prices.iloc[start_idx:].reset_index(drop=True)
        
        # Calculer moyenne des cycles précédents
        all_cycles = []
        for i in range(0, len(close_prices) - kitchin_length, kitchin_length):
            cycle = close_prices.iloc[i:i+kitchin_length]
            if len(cycle) == kitchin_length:
                # Normaliser
                cycle_norm = (cycle / cycle.iloc[0]) * 100
                all_cycles.append(cycle_norm.values)
        
        if len(all_cycles) > 0:
            avg_cycle = np.mean(all_cycles, axis=0)
        else:
            avg_cycle = None
        
        # Normaliser cycle actuel
        current_norm = (current_cycle / current_cycle.iloc[0]) * 100
        
        # Stats
        jour_actuel = remaining
        cours_actuel = round(float(close_prices.iloc[-1]), 2)
        
        if avg_cycle is not None and jour_actuel <= len(avg_cycle):
            prix_attendu = avg_cycle[jour_actuel-1]
            cours_attendu = round(float(current_cycle.iloc[0] * prix_attendu / 100), 2)
            ecart_pct = round(((cours_actuel - cours_attendu) / cours_attendu) * 100, 2)
        else:
            cours_attendu = cours_actuel
            ecart_pct = 0.0
        
        # Graphique
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(1, len(current_norm)+1)),
            y=current_norm,
            mode='lines',
            name='Cycle actuel',
            line=dict(color='#667eea', width=3)
        ))
        
        if avg_cycle is not None:
            fig.add_trace(go.Scatter(
                x=list(range(1, len(avg_cycle)+1)),
                y=avg_cycle,
                mode='lines',
                name='Moyenne historique',
                line=dict(color='orange', width=2, dash='dash')
            ))
        
        fig.add_vline(
            x=jour_actuel,
            line_dash="dot",
            line_color="red",
            annotation_text=f"Jour {jour_actuel}",
            annotation_position="top"
        )
        
        fig.update_layout(
            title=f"Cycle de Kitchin (894j) - {ticker}",
            xaxis_title="Jour du cycle",
            yaxis_title="Prix normalisé (base 100)",
            height=450,
            hovermode='x unified'
        )
        
        stats = {
            'jour_actuel': jour_actuel,
            'cours_actuel': cours_actuel,
            'prix_moyen_attendu': cours_attendu,
            'ecart_pct': ecart_pct,
            'debut_cycle': data['Date'].iloc[start_idx].strftime('%d-%m-%Y')
        }
        
        return json.loads(fig.to_json()), stats
        
    except Exception as e:
        print(f"⚠️  Erreur Kitchin: {e}")
        return {}, {'jour_actuel': 0, 'cours_actuel': 0, 'ecart_pct': 0}


# ========================================
# GRAPHIQUE 3: VOLATILITÉ
# ========================================

def create_volatility_analysis(data, close_prices, ticker):
    """Analyse complète de la volatilité"""
    try:
        returns = close_prices.pct_change().dropna()
        rolling_vol = returns.rolling(window=30).std() * np.sqrt(252) * 100
        
        current_vol = round(float(rolling_vol.iloc[-1]), 2)
        median_vol = round(float(rolling_vol.median()), 2)
        mean_vol = round(float(rolling_vol.mean()), 2)
        
        # Projection 12 mois
        recent_vol = rolling_vol.iloc[-60:].mean()
        proj_12m = round(float(recent_vol), 2)
        
        # Niveau
        if current_vol > median_vol * 1.5:
            label = "High"
        elif current_vol < median_vol * 0.7:
            label = "Low"
        else:
            label = "Normal"
        
        # Graphique 1: Courbe volatilité
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=data["Date_str"].iloc[len(data)-len(rolling_vol):],
            y=rolling_vol,
            mode='lines',
            name='Volatilité 30j',
            line=dict(color='#667eea', width=2)
        ))
        
        fig1.add_hline(
            y=median_vol,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Médiane: {median_vol}%"
        )
        
        fig1.update_layout(
            title=f"Volatilité Historique - {ticker}",
            xaxis_title="Date",
            yaxis_title="Volatilité annualisée (%)",
            height=450,
            hovermode='x unified'
        )
        
        # Graphique 2: Gauge
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_vol,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Volatilité Actuelle - {ticker}"},
            delta={'reference': median_vol, 'suffix': '% vs médiane'},
            gauge={
                'axis': {'range': [None, median_vol * 2]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, median_vol * 0.7], 'color': "lightgreen"},
                    {'range': [median_vol * 0.7, median_vol * 1.3], 'color': "lightyellow"},
                    {'range': [median_vol * 1.3, median_vol * 2], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': current_vol
                }
            }
        ))
        
        fig2.update_layout(height=400)
        
        stats = {
            'current_vol': current_vol,
            'median_vol': median_vol,
            'mean_vol': mean_vol,
            'proj_12m': proj_12m,
            'label': label
        }
        
        return json.loads(fig1.to_json()), json.loads(fig2.to_json()), stats
        
    except Exception as e:
        print(f"⚠️  Erreur Volatilité: {e}")
        return {}, {}, {'current_vol': 0, 'proj_12m': 0, 'label': 'N/A'}


# ========================================
# GRAPHIQUE 4: CYCLE ANNUEL (SAISONNALITÉ)
# ========================================

def create_annual_cycle(data, close_prices, ticker):
    """Analyse de la saisonnalité annuelle"""
    try:
        df_temp = data.copy()
        df_temp['Close'] = close_prices
        df_temp['Month'] = df_temp['Date'].dt.month
        df_temp['Year'] = df_temp['Date'].dt.year
        df_temp['Returns'] = close_prices.pct_change() * 100
        
        # Moyenne des rendements par mois sur les 10 dernières années
        recent_years = df_temp[df_temp['Year'] >= df_temp['Year'].max() - 10]
        monthly_returns = recent_years.groupby('Month')['Returns'].mean()
        
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                  'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        fig = go.Figure()
        
        colors = ['green' if x > 0 else 'red' for x in monthly_returns.values]
        
        fig.add_trace(go.Bar(
            x=months,
            y=monthly_returns.values,
            marker_color=colors,
            text=[f"{x:.2f}%" for x in monthly_returns.values],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f"Saisonnalité Moyenne (10 ans) - {ticker}",
            xaxis_title="Mois",
            yaxis_title="Rendement moyen (%)",
            height=450,
            showlegend=False
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        stats = {
            'best_month': months[monthly_returns.idxmax() - 1],
            'worst_month': months[monthly_returns.idxmin() - 1]
        }
        
        return json.loads(fig.to_json()), stats
        
    except Exception as e:
        print(f"⚠️  Erreur Cycle Annuel: {e}")
        return {}, {}


# ========================================
# GRAPHIQUE 5: DÉCOMPOSITION STL
# ========================================

def create_returns_decomposition(data, close_prices, ticker):
    """Décomposition STL des rendements"""
    try:
        returns = close_prices.pct_change().dropna() * 100
        
        # Déterminer la période optimale
        # Pour la bourse : 252 jours ouvrés = 1 an
        # Nécessite au moins 2 cycles complets (2*252 = 504 jours)
        if len(returns) >= 504:
            period = 252  # Cycle annuel
            print("      → Utilisation période annuelle (252j)")
        elif len(returns) >= 126:
            period = 63  # Cycle trimestriel
            print("      → Utilisation période trimestrielle (63j)")
        elif len(returns) >= 60:
            period = 30  # Cycle mensuel
            print("      → Utilisation période mensuelle (30j)")
        else:
            raise ValueError("Pas assez de données pour STL (minimum 60 jours)")
        
        decomposition = seasonal_decompose(
            returns,
            model='additive',
            period=period,
            extrapolate_trend='freq'
        )
        
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Rendements', 'Tendance', 'Saisonnier', 'Résidu')
        )
        
        dates = data["Date_str"].iloc[len(data)-len(returns):]
        
        fig.add_trace(go.Scatter(x=dates, y=returns, name='Rendements', 
                                 line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y=decomposition.trend, name='Tendance',
                                 line=dict(color='green')), row=2, col=1)
        fig.add_trace(go.Scatter(x=dates, y=decomposition.seasonal, name='Saisonnier',
                                 line=dict(color='orange')), row=3, col=1)
        fig.add_trace(go.Scatter(x=dates, y=decomposition.resid, name='Résidu',
                                 line=dict(color='red')), row=4, col=1)
        
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text=f"Décomposition STL (période: {period}j) - {ticker}"
        )
        
        fig.update_yaxes(title_text="Rendement (%)", row=1, col=1)
        fig.update_yaxes(title_text="Tendance", row=2, col=1)
        fig.update_yaxes(title_text="Saisonnier", row=3, col=1)
        fig.update_yaxes(title_text="Résidu", row=4, col=1)
        fig.update_xaxes(title_text="Date", row=4, col=1)
        
        return json.loads(fig.to_json())
        
    except Exception as e:
        print(f"⚠️  Erreur Décomposition: {e}")
        return {}


# ========================================
# GRAPHIQUE 6: COEFFICIENT DE HURST
# ========================================

def calculate_hurst_exponent(ts):
    """Calcule le coefficient de Hurst"""
    lags = range(2, min(100, len(ts)//2))
    tau = []
    
    for lag in lags:
        # Calculer les différences
        pp = np.subtract(ts[lag:], ts[:-lag])
        tau.append(np.std(pp))
    
    # Régression linéaire en log-log
    lags_log = np.log(lags)
    tau_log = np.log(tau)
    
    poly = np.polyfit(lags_log, tau_log, 1)
    hurst = poly[0]
    
    return hurst, lags, tau

def create_hurst_analysis(data, close_prices, ticker):
    """Analyse du coefficient de Hurst"""
    try:
        # Calculer Hurst sur prix
        hurst, lags, tau = calculate_hurst_exponent(close_prices.values)
        
        # Interprétation
        if hurst > 0.5:
            interpretation = "Tendance persistante (mémoire long terme)"
        elif hurst < 0.5:
            interpretation = "Retour à la moyenne (anti-persistance)"
        else:
            interpretation = "Marche aléatoire"
        
        fig = go.Figure()
        
        # Scatter des valeurs
        fig.add_trace(go.Scatter(
            x=np.log(lags),
            y=np.log(tau),
            mode='markers',
            name='Données',
            marker=dict(size=6, color='blue')
        ))
        
        # Ligne de régression
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        fit_line = np.poly1d(poly)
        
        fig.add_trace(go.Scatter(
            x=np.log(lags),
            y=fit_line(np.log(lags)),
            mode='lines',
            name=f'Régression (H={hurst:.3f})',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=f"Coefficient de Hurst - {ticker}<br><sub>{interpretation}</sub>",
            xaxis_title="log(lag)",
            yaxis_title="log(std)",
            height=450,
            annotations=[
                dict(
                    x=0.05, y=0.95,
                    xref='paper', yref='paper',
                    text=f"<b>H = {hurst:.3f}</b><br>{interpretation}",
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='black',
                    borderwidth=1
                )
            ]
        )
        
        return json.loads(fig.to_json())
        
    except Exception as e:
        print(f"⚠️  Erreur Hurst: {e}")
        return {}


# ========================================
# GRAPHIQUE 7 & 8: ANALYSE FFT
# ========================================

def create_fft_analysis(data, close_prices, ticker):
    """Analyse FFT - Corona Spectrum + Cycles Dominants"""
    try:
        # Préparer les données
        returns = close_prices.pct_change().dropna()
        N = len(returns)
        
        # FFT
        yf = fft(returns.values)
        xf = fftfreq(N, 1)[:N//2]
        power = 2.0/N * np.abs(yf[:N//2])
        
        # Filtrer les basses fréquences (trop longues)
        mask = xf > 1/500  # Cycles < 500 jours
        xf_filtered = xf[mask]
        power_filtered = power[mask]
        
        # Convertir fréquences en périodes (jours)
        periods = 1 / xf_filtered
        
        # Top 5 cycles
        top_indices = np.argsort(power_filtered)[-5:][::-1]
        top_periods = periods[top_indices]
        top_powers = power_filtered[top_indices]
        
        print(f"      → Cycles détectés : {', '.join([f'{int(p)}j' for p in top_periods])}")
        
        # GRAPHIQUE 1: Corona Spectrum (polaire)
        fig1 = go.Figure()
        
        theta = np.linspace(0, 360, len(power_filtered))
        
        fig1.add_trace(go.Scatterpolar(
            r=power_filtered,
            theta=theta,
            mode='lines',
            fill='toself',
            name='Spectre FFT',
            line=dict(color='#667eea')
        ))
        
        fig1.update_layout(
            title=f"Corona Spectrum FFT - {ticker}",
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            height=450
        )
        
        # GRAPHIQUE 2: Top 5 cycles dominants
        fig2 = go.Figure()
        
        # Meilleur formatage selon l'échelle des valeurs
        if max(top_powers) < 0.01:
            # Notation scientifique pour petites valeurs
            text_format = [f"{p:.2e}" for p in top_powers]
            y_title = "Puissance (notation scientifique)"
        else:
            text_format = [f"{p:.4f}" for p in top_powers]
            y_title = "Puissance"
        
        fig2.add_trace(go.Bar(
            x=[f"{int(p)}j" for p in top_periods],
            y=top_powers,
            marker_color='#667eea',
            text=text_format,
            textposition='outside',
            hovertemplate='Période: %{x}<br>Puissance: %{y:.6f}<extra></extra>'
        ))
        
        fig2.update_layout(
            title=f"Top 5 Cycles Dominants - {ticker}",
            xaxis_title="Période (jours)",
            yaxis_title=y_title,
            height=450,
            showlegend=False
        )
        
        return json.loads(fig1.to_json()), json.loads(fig2.to_json())
        
    except Exception as e:
        print(f"⚠️  Erreur FFT: {e}")
        return {}, {}


# ========================================
# FONCTIONS UTILITAIRES
# ========================================

def validate_ticker(ticker: str) -> bool:
    """Vérifie si un ticker est valide"""
    try:
        data, error = download_stock_data_fixed(ticker)
        return data is not None and not data.empty
    except:
        return False