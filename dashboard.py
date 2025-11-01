import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURATION ---
BASE_PATH = "./livrables_UA2"

# Titre du tableau de bord
st.set_page_config(layout="wide", page_title="Analyse Ventes MapReduce")
st.title("📊 Tableau de Bord d'Analyse des Ventes (Hadoop MapReduce)")
st.caption("Visualisation des Livrables 5.1 à 5.4 agrégés par MapReduce.")

# =========================================================
# UTILS : Fonction de chargement générique
# =========================================================

def load_data(file_name, sep='\t', header=None, names=None):
    """Charge un fichier CSV/TXT local et vérifie son existence."""
    file_path = os.path.join(BASE_PATH, file_name)
    if not os.path.exists(file_path):
        st.error(f"Fichier non trouvé: {file_path}. Veuillez vérifier l'exécution de run.sh.")
        return None
    try:
        df = pd.read_csv(file_path, sep=sep, header=header, names=names, skipinitialspace=True)
        return df
    except Exception as e:
        st.error(f"Erreur lors de la lecture de {file_path}. Le format est-il correct? Détail: {e}")
        return None

# =========================================================
# 1. LIVRABLE 5.1 : CA PAR PAYS ET MOIS
# =========================================================

st.header("1. 🌍 Chiffre d'Affaires Net par Pays et par Mois (Livrable 5.1)")

df_ca_brut = load_data("output_ca/ca_pays_mois.txt", names=['Key', 'CA Net'])

if df_ca_brut is not None:
    try:
        # Séparer la clé composée (Mois\tPays\tCA Net)
        # On suppose que le reducer_ca.py a déjà formaté la sortie en: ANNEE-MOIS \t PAYS \t CA_NET
        df_ca = df_ca_brut.rename(columns={'Key': 'Mois', 'CA Net': 'Pays_CA'})
        df_ca[['Pays', 'CA Net']] = df_ca['Pays_CA'].str.split('\t', expand=True).iloc[:, :2]
        df_ca = df_ca.drop(columns=['Pays_CA'])
        
        # Le format correct venant du reducer devrait être: ANNEE-MOIS \t PAYS \t CA_NET
        # Si le format du reducer est bien ANNEE-MOIS \t PAYS \t CA_NET (trois colonnes):
        df_ca = load_data("output_ca/ca_pays_mois.txt", names=['Mois', 'Pays', 'CA Net'])


        df_ca['CA Net'] = pd.to_numeric(df_ca['CA Net'], errors='coerce')
        df_ca = df_ca.dropna(subset=['CA Net'])
        
        # ANALYSE 1 : Total CA par Pays (Focus Principal)
        df_ca_total = df_ca.groupby('Pays')['CA Net'].sum().reset_index()
        df_ca_total['CA Net (M€)'] = (df_ca_total['CA Net'] / 1_000_000).round(2)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Total CA Net Global par Pays")
            fig_pays = px.bar(
                df_ca_total.sort_values(by='CA Net', ascending=True), 
                x='CA Net', 
                y='Pays', 
                orientation='h',
                title='CA Net Total par Pays',
                labels={'CA Net': "CA Net (Millions €)"},
                template="plotly_white",
                height=450
            )
            st.plotly_chart(fig_pays, use_container_width=True)

        with col2:
            st.subheader("Top Pays")
            df_top_pays = df_ca_total.nlargest(5, 'CA Net')
            st.dataframe(
                df_top_pays[['Pays', 'CA Net (M€)']].style.format({"CA Net (M€)": "{:.2f} M€"}), 
                hide_index=True
            )

        st.subheader("Évolution du CA Net par Mois")
        df_ca_mois_global = df_ca.groupby('Mois')['CA Net'].sum().reset_index()
        fig_mois = px.line(
            df_ca_mois_global, 
            x='Mois', 
            y='CA Net', 
            title='CA Net Global par Mois',
            labels={'CA Net': "CA Net (Millions €)"},
            template="plotly_white",
        )
        st.plotly_chart(fig_mois, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur d'analyse des données CA Pays/Mois. Erreur de parsing du fichier: {e}")

st.markdown("---")


# =========================================================
# 2. LIVRABLE 5.2 : TOP 10 PRODUITS
# =========================================================

st.header("2. 🥇 Top 10 Produits par Chiffre d'Affaires Net (Livrable 5.2)")

df_top10 = load_data("output_top10/classement_top10.txt", names=['Produit ID', 'CA Net'])

if df_top10 is not None:
    df_top10['CA Net'] = pd.to_numeric(df_top10['CA Net'], errors='coerce')
    df_top10 = df_top10.dropna(subset=['CA Net'])
    df_top10['CA Net (M€)'] = (df_top10['CA Net'] / 1_000_000).round(2)
    
    fig_top10 = px.bar(
        df_top10.sort_values(by='CA Net', ascending=True), 
        x='CA Net', 
        y='Produit ID', 
        orientation='h',
        title='Classement des 10 produits (CA Net)',
        labels={'CA Net': "CA Net (Millions €)"},
        template="plotly_white",
        color='CA Net',
        color_continuous_scale=px.colors.sequential.Agsunset,
    )
    st.plotly_chart(fig_top10, use_container_width=True)
    
    st.subheader("Tableau des Résultats")
    st.dataframe(df_top10[['Produit ID', 'CA Net (M€)']].style.format({"CA Net (M€)": "{:.2f} M€"}), hide_index=True)


st.markdown("---")


# =========================================================
# 3. LIVRABLE 5.3 : TAUX DE RETOUR GLOBAL
# =========================================================

st.header("3. 🔄 Taux de Retour Global (par Quantité) (Livrable 5.3)")

df_retours = load_data("output_retours/taux_global.txt", sep=':', names=['Metric', 'Value'])

if df_retours is not None:
    df_retours['Metric'] = df_retours['Metric'].str.strip()
    df_retours['Value'] = df_retours['Value'].str.strip().str.replace(',', '').str.replace('%', '')
    
    try:
        total_sold = pd.to_numeric(df_retours[df_retours['Metric'] == 'Quantité Totale Vendue']['Value'].iloc[0], errors='coerce')
        total_returned = pd.to_numeric(df_retours[df_retours['Metric'] == 'Quantité Totale Retournée']['Value'].iloc[0], errors='coerce')
        taux = pd.to_numeric(df_retours[df_retours['Metric'] == 'Taux de Retour Global (%)']['Value'].iloc[0], errors='coerce')

        col_met1, col_met2, col_met3 = st.columns(3)
        col_met1.metric("Quantité Totale Vendue", f"{int(total_sold):,}")
        col_met2.metric("Quantité Totale Retournée", f"{int(total_returned):,}")
        col_met3.metric("Taux de Retour Global", f"{taux:.2f}%")

        df_distrib = pd.DataFrame({
            'Statut': ['Vendu (Net)', 'Retourné'],
            'Quantité': [total_sold - total_returned, total_returned]
        })
        fig_distrib = px.pie(
            df_distrib, 
            values='Quantité', 
            names='Statut', 
            title='Distribution des Quantités (Retour vs Vente Nette)',
            color_discrete_sequence=['#28a745', '#dc3545']
        )
        st.plotly_chart(fig_distrib, use_container_width=True)

    except Exception as e:
        st.warning(f"Impossible d'analyser les données de retour : {e}")


st.markdown("---")


# =========================================================
# 4. LIVRABLE 5.4 : RÉPARTITION PAR PAIEMENT
# =========================================================

st.header("4. 💳 Répartition des Ventes par Mode de Paiement (Livrable 5.4)")

df_paiements = load_data("output_paiements/repartition_ca.txt", names=['Mode de Paiement', 'CA Net'])

if df_paiements is not None:
    df_paiements['CA Net'] = pd.to_numeric(df_paiements['CA Net'], errors='coerce')
    df_paiements = df_paiements.dropna(subset=['CA Net'])
    
    total_ca = df_paiements['CA Net'].sum()
    df_paiements['Pourcentage'] = (df_paiements['CA Net'] / total_ca) * 100
    df_paiements['CA Net (M€)'] = (df_paiements['CA Net'] / 1_000_000).round(2)
    
    fig_pie = px.pie(
        df_paiements, 
        values='Pourcentage', 
        names='Mode de Paiement', 
        title='Part du CA Net par Mode de Paiement',
        hole=.5, 
        template="plotly_white"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.subheader("Données de Répartition")
    st.dataframe(df_paiements[['Mode de Paiement', 'CA Net (M€)', 'Pourcentage']].sort_values(by='CA Net', ascending=False).style.format({"CA Net (M€)": "{:,.2f} M€", "Pourcentage": "{:.1f} %"}), hide_index=True)
