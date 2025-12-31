import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import base64
import numpy as np
import os
import streamlit.components.v1 as components

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #8A2BE2;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e3f2fd;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# titre de l'application

st.markdown("<h1 style='text-align: center; color: black;'>MON APPLICATION DE DONNÉES SUR LES ANIMAUX</h1>", unsafe_allow_html=True)

st.markdown("""
Cette application effectue le web scraping de données d'animaux sur CoinAfrique sur plusieurs pages.
Les utilisateurs peuvent choisir la catégorie et le nombre de pages à extraire.
* **Bibliothèques Python :** pandas, streamlit, requests, bs4, base64
* **Source de données:** [coinafrique sénégal](https://sn.coinafrique.com)
""")

# fonction pour ajouter une image en arrière-plan

# def add_bg_from_local(image_file):
#  if os.path.exists(image_file):
#      with open(image_file, "rb") as f:
#            encoded_string = base64.b64encode(f.read()).decode()
#       st.markdown(
#            f"""
#           <style>
#            .stApp {{
#                background-image: url(data:image/jpg;base64,{encoded_string});
#                background-size: cover;
#            }}
#            </style>
#           """,
#           unsafe_allow_html=True 
#        )


# mise en cache pour le téléchargement csv

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


# fonction d'affichage et de téléchargement

def load(dataframe, title, key, key1):

    if st.button(title, key1):
        st.subheader("Afficher les dimensions des données")

        st.write(
            f"Dimensions des données : {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes"
        )

        # Appliquer un style : fond bleu clair et texte noir
        dataframe_styled = dataframe.style.set_properties(**{
            'background-color': '#32CD32',  # couleur de fond
            'color': 'black',                  # couleur du texte
            'font-size': '16px'                # taille du texte
        })
      
      
        st.dataframe(
            dataframe_styled,
            use_container_width=True,
            height=700
        )

        csv = convert_df(dataframe)

        st.download_button(
            label="Télécharger les données au format CSV",
            data=csv,
            file_name="animals_data.csv",
            mime="text/csv",
            key=key
        )



# fonction de scraping coinafrique

def load_coinafrique_animals(categorie_choisie, nb_pages):
    # creation d'un dataframe vide
    df = pd.DataFrame()

    # dictionnaire des urls par categorie
    urls = {
        "Chiens": "https://sn.coinafrique.com/categorie/chiens",
        "Moutons": "https://sn.coinafrique.com/categorie/moutons",
        "Poules/Lapins/Pigeons": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
        "Autres animaux": "https://sn.coinafrique.com/categorie/autres-animaux"
    }

    # recuperation de l'url selon la categorie choisie
    base_url = urls[categorie_choisie]

    # boucle sur le nombre de pages choisi par l'utilisateur
    for page in range(1, nb_pages + 1):
        url = f"{base_url}?page={page}"

        # recuperation du code html de la page
        res = get(url)

        # parsing du html avec beautifulsoup
        soup = bs(res.text, "html.parser")

        # recuperation des conteneurs des annonces
        containers = soup.find_all("div", class_="col s6 m4 l3")
        data = []

        for container in containers:
            try:
                # recuperation du nom de l'annonce
                title = container.find("p", class_="ad__card-description").text.strip()

                # recuperation et nettoyage du prix
                price = container.find("p", class_="ad__card-price").text.strip()
                price = price.replace("\u202f", "").replace("F CFA", "")

                # recuperation de l'adresse
                address = container.find("p", class_="ad__card-location").text.strip()

                # recuperation du lien de l'image
                image = container.find("img")["src"]

                # creation du dictionnaire de donnees
                data.append({
                    "categorie": categorie_choisie,
                    "nom": title,
                    "prix": price,
                    "adresse": address,
                    "image_lien": image
                })
            except:
                pass

        # conversion en dataframe et concatenation
        df = pd.concat([df, pd.DataFrame(data)], axis=0).reset_index(drop=True)

    return df


# sidebar - entrees utilisateur

st.sidebar.header("Caractéristiques de saisie utilisateur")

Pages = st.sidebar.selectbox(
    "Indexes des pages",
    [int(p) for p in np.arange(1, 17)]
)

Categorie = st.sidebar.selectbox(
    "Catégories d'animaux",
    [
        "Chiens",
        "Moutons",
        "Poules/Lapins/Pigeons",
        "Autres animaux"
    ]
)

Choices = st.sidebar.selectbox(
    "options",
    [
        "Scraper des données avec BeautifulSoup",
        "Télécharger les données scrapées",
        "Évaluez l'application"
    ]
)

# mapping categories -> fichiers CSV existants
csv_files = {
    "Chiens": "coinafrique_chiens.csv",
    "Moutons": "coinfrique_moutons.csv",
    "Poules/Lapins/Pigeons": "coinafrique_poules_lapins_et_pigeons.csv",
    "Autres animaux": "coinafrique_autres_animaux.csv"
}

# application du background

#add_bg_from_local("img_file3.jpg")


# logique principale de l'application

if Choices == "Scraper des données avec BeautifulSoup":

    animals_df = load_coinafrique_animals(Categorie, Pages)
    load(animals_df, f"Données concernant les {Categorie}", "1", "101")

elif Choices == "Télécharger les données scrapées":

    csv_file = csv_files[Categorie]

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        load(
            df,
            f"Données CSV existantes : {Categorie}",
            "download_existing_csv",
            "show_existing_csv"
        )
    else:
        st.warning(f"Le fichier {csv_file} est introuvable ")


else:
    st.markdown("<h3 style='text-align: center;'>Donnez votre avis</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Formulaire d'évaluation Kobo"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://ee.kobotoolbox.org/x/6v4bI5ac">',
                unsafe_allow_html=True
            )

    with col2:
        if st.button("Formulaire d'évaluation google forms"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://docs.google.com/forms/d/e/1FAIpQLSe3ym_3nI_jWfR6XBWu0Vc2m8ZVW6E8SbDrIsEJwDXpAc945w/viewform?usp=header">',
                unsafe_allow_html=True
            )

