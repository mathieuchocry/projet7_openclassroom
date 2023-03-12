import streamlit as st
import numpy as np
import pandas as pd
import streamlit as st
import joblib
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.cm import RdYlGn
from PIL import Image
from random import randint

 ## Constante
 DEBUG = True 
     #adresse de l'API
 HOST = 'adresse.herokuapp.com'
     #Chargement dataset 
data_test = pd.read_csv("df_test_2.csv")
data_train = pd.read_csv("df_train_2.csv")
data_score = pd.read_csv("score solvabilité.csv")
image = Image.open('./img/Home-Credit-logo.jpg')

## Fonctions
    # Donne la prédiction du clients ( 0 solvable ; 1 défaut de paiement)
def predict(id_client: int):
    
    json_id_client = df_test_sample.loc[int(id_client)].to_json()
    response = requests.get(HOST + '/predict', data=json_id_client)
    prediction_default = eval(response.content)["prediction"]
    return prediction_default

    # Donne les valeurs shap des features du clients 
def shap(id_client: int):
    json_id_client = df_test_sample.loc[int(id_client)].to_json()
    response = requests.get(HOST + '/shap', data=json_id_client)
    df_shap = pd.read_json(eval(response.content), orient='index')
    return df_shap

    # Donne le score shap du client 
def shap(id_client: int):
    json_id_client = df_test_sample.loc[int(id_client)].to_json()
    response = requests.get(HOST + '/shap_score', data=json_id_client)
    score_shap = eval(response.content)["shap_score"]
    return score_shap

## Site Web

    # Formation d'une liste pour vérification de présence du client dans le dataframe 
liste_id = data_train['SK_ID_CURR'].tolist()

#affichage formulaire
st.title(' Score pour demande de crédit chez Home credit')
st.image(image, width=300)
st.subheader("Prédictions de scoring client et comparaison à l'ensemble des clients")

id_client = st.text_input('Veuillez saisir l\'identifiant d\'un client:', )
chaine = "l'id Saisi est " + str(id_client)
st.write(chaine)

sample_en_regle = str(list(data_train[data_train['TARGET'] == 0].sample(5)[['SK_ID_CURR', 'TARGET']]['SK_ID_CURR'].values)).replace('\'', '').replace('[', '').replace(']','')
chaine_en_regle = 'Exemples d\'id de clients en règle : ' +sample_en_regle
sample_en_defaut = str(list(data_train[data_train['TARGET'] == 1].sample(5)[['SK_ID_CURR', 'TARGET']]['SK_ID_CURR'].values)).replace('\'', '').replace('[', '').replace(']','')
chaine_en_defaut = 'Exemples d\'id de clients en défaut : ' + sample_en_defaut

if id_input == '': #lorsque rien n'a été saisi
    st.write(chaine_en_defaut)
    st.write(chaine_en_regle)

elif (int(id_client) in liste_id): 
    with st.spinner('Chargement du score du client...'):
        prediction = predict(id_client)
        score_shap = shap(id_client)
        if score_shap < 0.273 :
            st.success( f"  \n __Crédit Accepté__  \n  \nLa probabilité de défaillance du crédit demandé est de __{round(100*prediction,1)}__%. \n ")
        else :
            st.error( f"  \n __Crédit refusé__  \n  \nLa probabilité de défaillance du crédit demandé est de __{round(100*prediction,1)}__%. \n ")
        
    #Information clients: Genre, âge, statut du client et nombre d'enfant du client
    with st.spinner("information client"):
        infos_client = data_test[data_test["SK_ID_CURR"] == int(id_client)]
        st.write("Sexe :", infos_client["CODE_GENDER"].values[0])
        st.write("Âge : {:.0f} ans".format(int(infos_client["DAYS_BIRTH"]/365)))
        st.write("Statut familial : ", infos_client["NAME_FAMILY_STATUS"].values[0])
        st.write("Nombre d'enfants': {:.0f}".format(infos_client["CNT_CHILDREN"].values[0]))

        ## Distribution des ages des clients
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(data_train["DAYS_BIRTH"]/ 365, edgecolor = 'k', color="goldenrod", bins=20)
        ax.axvline(int(infos_client["DAYS_BIRTH"].values / 365), color="green", linestyle='--')
        ax.set(title='Âge des clients', xlabel='Âge(Year)', ylabel='Densité')
        st.pyplot(fig)
    
        ## Information des revenus du clients
        st.subheader("Revenu ( Dollar US ($))")
        st.write("Revenu total : {:.0f}".format(infos_client["AMT_INCOME_TOTAL"].values[0]))
        st.write("Montant du crédit : {:.0f}".format(infos_client["AMT_CREDIT"].values[0]))
        st.write("Mensualité du crédit : {:.0f}".format(infos_client["AMT_ANNUITY"].values[0]))
        st.write("Montant du bien pour le crédit: {:.0f}".format(infos_client["AMT_GOODS_PRICE"].values[0]))
        
        ##Distribution des revenus des clients
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(data_train["AMT_INCOME_TOTAL"], edgecolor = 'k', color="goldenrod", bins=10)
        ax.axvline(int(infos_client["AMT_INCOME_TOTAL"].values[0]), color="green", linestyle='--')
        ax.set(title=' Revenues clients', xlabel='Revenu (USD)', ylabel='Densité')
        st.pyplot(fig)
        
        ## Information des revenus du clients
        st.subheader("Evaluation shap Score")
        st.write("shap score du client : {:.0f}".format(score_shap))
        st.write("shap score critique : 0.273"
        
    
        ## Distribution des shap scores des clients
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.kdeplot(score.loc[score['TARGET']==0, 'score X_test'], label='Paiement à temps',
            fill=True, alpha=0.5, color='#022282')
        sns.kdeplot(score.loc[score['TARGET']==1, 'score X_test'], label='Difficultés de paiement',
           fill=True, alpha=0.3, color='#FF511A')
        ax.axvline(x=0.273, color='k', linestyle='--', label='Seuil r=0.273')
        ax.axvline(int(score_shap), color="green", linestyle='--')
        ax.set(title='Shap score clients', xlabel='Shap score', ylabel='Densité')
        st.pyplot(fig)  
    

    
    #Feature importance
    with st.spinner("Features importance du client"):
        df_shap = get_shap(id_client)

        fig, ax = plt.subplots(figsize=(10, 10))
        explainer = shap.TreeExplainer(load_model())
        shap_values = explainer.shap_values(X)
        shap.summary_plot(shap_values[0], X, plot_type ="bar", max_display=number, color_bar=False, plot_size=(5, 5))
        st.pyplot(fig)

        
    else:
        st.markdown("<i>…</i>", unsafe_allow_html=True)
            

  
else: 
    st.write('Identifiant non reconnu')
