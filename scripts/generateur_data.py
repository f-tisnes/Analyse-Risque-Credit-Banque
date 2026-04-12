import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
n_clients = 5000
mois_historique = 12
agences = ['Strasbourg', 'Colmar', 'Mulhouse', 'Epinal']
types_credit = {
    'Habitat': {'poids': 0.5, 'montant': (150000, 450000), 'duree': (180, 300), 'taux': (3.5, 4.5)},
    'Consommation': {'poids': 0.3, 'montant': (5000, 25000), 'duree': (12, 60), 'taux': (5.5, 7.5)},
    'Auto': {'poids': 0.2, 'montant': (15000, 45000), 'duree': (36, 84), 'taux': (4.8, 6.0)}
}

print(f"Génération de {n_clients} clients...")

# --- TABLE 1 : REFERENTIEL CREDITS ---
data_ref = []
for i in range(1, n_clients + 1):
    client_id = f"CLI-{i:04d}"
    credit_id = f"CRE-{i:04d}"
    agence = np.random.choice(agences)
    type_c = np.random.choice(list(types_credit.keys()), p=[v['poids'] for v in types_credit.values()])
    
    config = types_credit[type_c]
    montant_initial = np.random.randint(config['montant'][0], config['montant'][1])
    duree = np.random.randint(config['duree'][0], config['duree'][1])
    
    # Logique PNB : Plus le montant est élevé, plus le taux baisse légèrement
    taux_base = np.random.uniform(config['taux'][0], config['taux'][1])
    remise = (montant_initial / 450000) * 0.5
    taux = round(taux_base - remise, 2)
    
    assurance = np.random.choice([0, 1], p=[0.3, 0.7]) # 70% de taux d'équipement
    
    # Date de réalisation (étalée sur les 5 dernières années)
    jours_passe = np.random.randint(400, 1800)
    date_real = datetime(2023, 12, 31) - timedelta(days=jours_passe)
    
    # Calcul mensualité simplifiée (Capital / Durée + Intérêts mensuels)
    mensualite = round((montant_initial / duree) + (montant_initial * (taux/100/12)), 2)
    
    data_ref.append([client_id, credit_id, agence, type_c, date_real.strftime('%Y-%m-%d'), 
                     montant_initial, duree, taux, assurance, mensualite])

df_ref = pd.DataFrame(data_ref, columns=['Client_ID', 'Credit_ID', 'Agence', 'Type_Credit', 
                                         'Date_Realisation', 'Montant_Initial', 'Duree_Mois', 
                                         'Taux', 'Assurance', 'Echeance_Mensuelle'])

# --- TABLE 2 : SUIVI MENSUEL (60 000 lignes) ---
print("Génération de l'historique mensuel (60 000 lignes)...")
dates_2024 = pd.date_range(start='2024-01-01', periods=12, freq='MS').strftime('%Y-%m-%d').tolist()
data_suivi = []

for _, row in df_ref.iterrows():
    # Capital restant au début de l'année (estimation simplifiée selon l'ancienneté)
    mois_ecoules_debut = (datetime(2024, 1, 1) - datetime.strptime(row['Date_Realisation'], '%Y-%m-%d')).days // 30
    capital_restant = max(0, row['Montant_Initial'] - (mois_ecoules_debut * (row['Montant_Initial'] / row['Duree_Mois'])))
    
    for mois in dates_2024:
        # Le capital baisse chaque mois
        capital_restant = max(0, capital_restant - (row['Montant_Initial'] / row['Duree_Mois']))
        
        # Logique de risque
        score_risque = np.random.randint(1, 100)
        statut = "OK"
        if score_risque > 95: statut = "Defaut"
        elif score_risque > 85: statut = "Retard"
        
        data_suivi.append([mois, row['Client_ID'], round(capital_restant, 2), score_risque, statut])

df_suivi = pd.DataFrame(data_suivi, columns=['Date_Mois', 'Client_ID', 'Capital_Restant_Du', 'Score_Risque', 'Statut'])

# Sauvegarde
df_ref.to_csv('referentiel_credits.csv', index=False, sep=';', encoding='utf-8')
df_suivi.to_csv('suivi_mensuel_credits.csv', index=False, sep=';', encoding='utf-8')

print("Terminé ! Fichiers 'referentiel_credits.csv' et 'suivi_mensuel_credits.csv' créés.")