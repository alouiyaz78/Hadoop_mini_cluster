import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================================================
# CONFIGURATION & UTILITAIRES
# =========================================================

DATA_BASE_PATH = "./livrables_UA2"

# Fonction pour charger les données de manière fiable avec mise en cache
@st.cache_data
def load_data_final(job_name, column_names):
    """
    Charge le fichier de données propre généré par run.sh.
    Retourne un DataFrame et un booléen indiquant si des erreurs ont été trouvées.
    """
    file_path = os.path.join(DATA_BASE_PATH, job_name, f"{job_name}_clean.txt")
    
    if not os.path.exists(file_path):
        return pd.DataFrame(), True
    
    try:
        df = pd.read_csv(
            file_path,
            sep='\t',
            header=None,
            names=column_names,
            on_bad_lines='skip',
            encoding='utf-8'
        )
        
        # Assurance du Typage Numérique (dernière colonne)
        value_col = column_names[-1]
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df = df.dropna(subset=[value_col])

        if df.empty:
            return pd.DataFrame(), True
            
        return df, False
    
    except Exception:
        return pd.DataFrame(), True

# Fonction pour charger les métriques simples (Livrable 5.3)
def load_retours_metrics():
    """Charge les 3 métriques de retours du fichier et les met dans un dictionnaire."""
    file_path = os.path.join(DATA_BASE_PATH, "output_retours", "output_retours_clean.txt")
    metrics = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                if '\t' in stripped_line:
                    parts = stripped_line.split('\t', 1) 
                    key = parts[0].strip()
                    value = parts[1].strip()
                    metrics[key] = value.replace(',', '').replace('%', '') 
        
        qte_vendue = float(metrics.get("Quantité Totale Vendue", 0))
        qte_retournee = float(metrics.get("Quantité Totale Retournée", 0))
        taux_retour = float(metrics.get("Taux de Retour Global (%)", 0.0))
        
        return qte_vendue, qte_retournee, taux_retour, False

    except Exception:
        return 0, 0, 0.0, True


# =========================================================
# MISE EN PAGE STREAMLIT
# =========================================================

st.set_page_config(layout="wide")
st.title("📊 Tableau de Bord d'Analyse des Ventes (Hadoop MapReduce)")
st.markdown("Visualisation des Livrables 5.1 à 5.4 agrégés par MapReduce.")
st.divider()

# =========================================================
# 1. LIVRABLE 5.1 : CA Net par Pays et par Mois (BARPLOT COMPOSÉ)
# =========================================================
st.header("1. 🌍 Chiffre d'Affaires Net par Pays et par Mois (Livrable 5.1)")

df_ca, error_ca = load_data_final("output_ca", column_names=['Mois', 'Pays', 'CA Net'])

if error_ca:
    st.warning("Le fichier du CA Net par Pays/Mois est vide ou contient des erreurs.")
else:
    try:
        df_ca['Mois'] = pd.to_datetime(df_ca['Mois'], format='%Y-%m', errors='coerce')
        df_ca = df_ca.dropna(subset=['Mois'])
        df_ca['Mois_Str'] = df_ca['Mois'].dt.strftime('%Y-%m') # Créer une chaîne pour les labels de couleur
        
        df_ca['CA Net (M€)'] = df_ca['CA Net'] / 1_000_000
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Total CA Net par Pays (Détaillé par Mois)")
            # Graphique à barres EMPILÉES / COMPOSÉES
            fig_pays = px.bar(
                df_ca.sort_values(by='CA Net', ascending=False), 
                x='CA Net (M€)', 
                y='Pays', 
                color='Mois_Str', # Segmentation par Mois (Couleur)
                orientation='h',
                title='CA Net Total par Pays (Octobre vs Novembre)',
                template="plotly_white",
            )
            st.plotly_chart(fig_pays, use_container_width=True)

        with col2:
            st.subheader("Évolution Mensuelle")
            ca_par_mois = df_ca.groupby('Mois')['CA Net (M€)'].sum().reset_index()
            fig_mois = px.line(
                ca_par_mois, 
                x='Mois', 
                y='CA Net (M€)', 
                title='CA Net Global par Mois', 
                template='plotly_white'
            )
            st.plotly_chart(fig_mois, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur de visualisation du Livrable 5.1 : {e}")

st.divider()


# =========================================================
# 2. LIVRABLE 5.2 : Top 10 Produits
# =========================================================
st.header("2. 🥇 Top 10 Produits par Chiffre d'Affaires Net (Livrable 5.2)")

df_top10, error_top10 = load_data_final("output_top10", column_names=['Produit ID', 'CA Net'])

if error_top10:
    st.warning("Le fichier du Top 10 produits est vide ou contient des erreurs.")
else:
    df_top10['CA Net (M€)'] = df_top10['CA Net'] / 1_000_000
    df_top10['Produit ID'] = df_top10['Produit ID'].astype(str) 
    
    st.subheader("Visualisation du Top 10")
    fig_top10 = px.bar(
        df_top10.sort_values(by='CA Net', ascending=True), 
        x='CA Net (M€)', 
        y='Produit ID', 
        orientation='h',
        title='Classement des 10 produits (CA Net)',
        labels={'CA Net (M€)': "CA Net (Millions €)"},
        template="plotly_white",
    )
    st.plotly_chart(fig_top10, use_container_width=True)
    
    st.subheader("Tableau des Résultats")
    st.dataframe(df_top10[['Produit ID', 'CA Net (M€)']].style.format({"CA Net (M€)": "{:,.2f} M€"}), hide_index=True)


st.divider()


# =========================================================
# 3. LIVRABLE 5.3 : Taux de Retour Global (CORRECTION CRITIQUE)
# =========================================================
st.header("3. 🔄 Taux de Retour Global (par Quantité) (Livrable 5.3)")

qte_vendue, qte_retournee, taux_retour_str, error_retours = load_retours_metrics()

if error_retours:
    st.warning("Le fichier du Taux de Retour est manquant ou contient des erreurs irrécupérables.")
else:
    
    # 🚨 CORRECTION CRITIQUE: Définir les variables de colonne pour éviter le NameError
    col1, col2, col3 = st.columns(3) 
    
    with col1:
        st.metric("Quantité Totale Vendue", f"{qte_vendue:,.0f}".replace(",", " "))
    with col2:
        st.metric("Quantité Totale Retournée", f"{qte_retournee:,.0f}".replace(",", " "))
    with col3:
        # Recalcul du taux pour affichage
        taux_calcule = (qte_retournee / qte_vendue) * 100 if qte_vendue else 0
        st.metric("Taux de Retour Global", f"{taux_calcule:.2f}%")


st.divider()


# =========================================================
# 4. LIVRABLE 5.4 : Répartition des Ventes par Mode de Paiement
# =========================================================
st.header("4. 💳 Répartition des Ventes par Mode de Paiement (Livrable 5.4)")

df_paiements, error_paiements = load_data_final("output_paiements", column_names=['Mode de Paiement', 'CA Net'])

if error_paiements:
    st.warning("Le fichier de répartition des paiements est vide ou contient des erreurs.")
else:
    df_paiements['CA Net (M€)'] = df_paiements['CA Net'] / 1_000_000
    total_ca_global = df_paiements['CA Net'].sum()
    df_paiements['Pourcentage'] = (df_paiements['CA Net'] / total_ca_global) * 100

    st.subheader("Données de Répartition")
    st.dataframe(
        df_paiements[['Mode de Paiement', 'CA Net (M€)', 'Pourcentage']]
            .sort_values(by='CA Net (M€)', ascending=False)
            .style.format({"CA Net (M€)": "{:,.2f} M€", "Pourcentage": "{:.1f} %"}), 
        hide_index=True
    )
    
    st.subheader("Graphique en Secteurs")
    fig_paiements = px.pie(
        df_paiements,
        names='Mode de Paiement',
        values='CA Net (M€)',
        title='Part du CA Net par Mode de Paiement',
        hole=.5, 
        template="plotly_white"
    )
    st.plotly_chart(fig_paiements, use_container_width=True)
