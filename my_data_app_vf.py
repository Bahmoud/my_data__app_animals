import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import base64
import numpy as np
import os

st.set_page_config(
    layout="wide"
)

#coueleur du sidebar
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #2563EB;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#couleur du background
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

# stuyle des boutons
st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #32CD32;   
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 600;
        border: none;
    }


    div.stButton > button:hover {
        background-color: #166534;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# style des boutons de téléchargement
st.markdown(
    """
    <style>

    div.stDownloadButton > button {
        background-color: #2563EB;   
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 15px;
        font-weight: 600;
        border: none;
    }

    div.stDownloadButton > button:hover {
        background-color: #1E40AF;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# titre de l'application

st.markdown("<h1 style='text-align: center; color: black;'>APPLICATION DE DONNÉES SUR LES ANIMAUX</h1>", unsafe_allow_html=True)

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
    "Options",
    [
        "Scraper des données avec BeautifulSoup",
        "Télécharger les données scrapées",
        "Tableau de bord",
        "Évaluez l'application"
    ],
    key="menu_principal"
)

# forcer le rafraîchissement quand l'utilisateur change de menu
if "menu_old" not in st.session_state:
    st.session_state.menu_old = Choices

if st.session_state.menu_old != Choices:
    st.session_state.menu_old = Choices
    st.rerun()

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

elif Choices == "Tableau de bord":

    st.subheader("TABLEAU DE BORD GLOBAL DES ANIMAUX")

    # chargement de tous les fichiers csv existants
    df_raw = pd.DataFrame()
    for categorie, file in csv_files.items():
        if os.path.exists(file):
            temp = pd.read_csv(file)
            temp["categorie"] = categorie  # ajouter la catégorie
            df_raw = pd.concat([df_raw, temp], ignore_index=True)

    # vérifier qu'on a des données
    if df_raw.empty:
        st.warning("aucun fichier csv valide trouvé pour le tableau de bord")
    else:
        # nettoyage des données 
        df_raw = df_raw.dropna(subset=["prix", "adresse"])
        
        # nettoyage du prix
        df_raw["prix"] = (
            df_raw["prix"]
            .astype(str)
            .str.replace(r"[^\d]", "", regex=True)
        )
        
        df_raw["prix"] = pd.to_numeric(df_raw["prix"], errors="coerce")
        
        # suppression des valeurs aberrantes (prix irréalistes)
        df_raw = df_raw[
            (df_raw["prix"] > 1_000) & (df_raw["prix"] < 50_000_000)
        ]
        
        # nettoyage des adresses
        df_raw["adresse"] = df_raw["adresse"].astype(str).str.strip().str.title()

        # vérifier qu'il reste des données après nettoyage
        if df_raw.empty:
            st.warning("Aucune donnée valide après nettoyage")
        else:

            df = df_raw.copy()

            # filtres du dashboard
            st.sidebar.subheader("Filtres du tableau de bord")
            categorie_filter = st.sidebar.multiselect(
                "catégories",
                df["categorie"].unique(),
                default=df["categorie"].unique()
            )
            df = df[df["categorie"].isin(categorie_filter)]

            # indicateurs clés
            col1, col2, col3 = st.columns(3)
            col1.metric("Total annonces", df.shape[0])

            mean_prix = df["prix"].mean()

            if not pd.isna(mean_prix):
                # arrondi à l'entier le plus proche
                mean_prix = round(mean_prix)
                # formater avec espace tous les 3 chiffres
                mean_prix_formate = f"{mean_prix:,}".replace(",", " ") + " CFA"
            else:
                mean_prix_formate = "N/A"

            col2.metric("Prix moyen", mean_prix_formate)

            col3.metric("Nombre de villes", df["adresse"].nunique())

            # graphiques
            st.markdown("### Annonces par catégorie")
            st.bar_chart(df["categorie"].value_counts())

            st.markdown("### Annonces par ville")
            st.bar_chart(df["adresse"].value_counts())

            #st.markdown("### Distribution des prix")
           # st.bar_chart(df["prix"].value_counts(bins=10))



else:
    st.markdown("<h3 style='text-align: center;'>Donnez votre avis</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <a href="https://ee.kobotoolbox.org/x/6v4bI5ac" target="_blank">
                <button style="
                    width:100%;
                    padding:12px;
                    font-size:16px;
                    border-radius:8px;
                    border:none;
                    background-color:#22C55E;
                    color:white;
                    cursor:pointer;
                ">
                    Formulaire d'évaluation Kobo
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSe3ym_3nI_jWfR6XBWu0Vc2m8ZVW6E8SbDrIsEJwDXpAc945w/viewform?usp=header"
               target="_blank">
                <button style="
                    width:100%;
                    padding:12px;
                    font-size:16px;
                    border-radius:8px;
                    border:none;
                    background-color:#2563EB;
                    color:white;
                    cursor:pointer;
                ">
                    Formulaire d'évaluation Google Forms
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )




