import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


def setup_styles():
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    sns.set_theme(style="whitegrid")


def plot_distributions(df, cols, display=False, output_dir="output/Desc_All_Cities"):
    """Affichage d'histogramme des colonnes spécifiées"""
    os.makedirs(output_dir, exist_ok=True)

    for col in cols:
        plt.figure(figsize=(9, 5))
        data = df[col].dropna()

        # Utilisation d'une échelle log
        if col not in ["nb_campings_2022", "nb_hotels_2022"]:
            data = data + 1e-6
            log_scale = True
            echelle_suffix = "(Échelle Log)"
        else:
            log_scale = False
            echelle_suffix = "(Échelle Linéaire)"

        sns.histplot(
            data, 
            kde=False,
            log_scale=log_scale,
            color="teal"
        )

        plt.title(f'Distribution de {col} {echelle_suffix}')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/hist_{col}.png", dpi=300)
        if display:
            plt.show()
        plt.close()


def plot_correlation_heatmap(df, output_dir="output/Desc_All_Cities", display=False, pol=None):
    """Génère et sauvegarde une matrice des corrélations"""
    # On ne garde que les colonnes numériques
    cols_corr = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[cols_corr].corr()

    plt.figure(figsize=(14, 12))
    cmap = sns.diverging_palette(240, 10, as_cmap=True)

    sns.heatmap(
        corr_matrix, cmap=cmap, vmax=1, vmin=-1, center=0,
        square=True, linewidths=.5, annot=True, fmt=".2f",
        cbar_kws={"shrink": .75}
    )
    plt.title('Matrice de Corrélation')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/correlogram_{pol}.png", dpi=300)
    if display:
        plt.show()
    plt.close()


def plot_comparative_distributions(df_sample, df_france, polluant_name, vars_eco, output_dir="output/plots_comparaison"):
    """
    Génère un graphique comparant les distributions de certaines colonnes pour
    toutes les villes de France et celles de nos échantillons
    """
    os.makedirs(output_dir, exist_ok=True)

    for var in vars_eco:
        if var not in df_france.columns or var not in df_sample.columns:
            continue

        data_france = df_france[var].dropna()
        data_sample = df_sample[var].dropna()

        plt.figure(figsize=(10, 6))

        log_scale = True if ("population" in var.lower() or "densite" in var.lower()) else False

        # Plot France
        sns.histplot(data_france, stat="density", kde=True, color="lightgray",
                     label="France entière", log_scale=log_scale, alpha=0.5)

        # Plot échantillon
        sns.histplot(data_sample, stat="density", kde=True, color="teal",
                     label=f"Échantillon ({polluant_name})", log_scale=log_scale, alpha=0.6)

        # Affichage des moyennes
        plt.axvline(data_france.mean(), color='gray', linestyle='--', label=f"Moyenne FR")
        plt.axvline(data_sample.mean(), color='teal', linestyle='-', label=f"Moyenne Éch")

        plt.title(f"Distribution : {var} ({polluant_name})")
        plt.legend()

        filename = f"{output_dir}/Distr_{polluant_name}_{var}.png"
        plt.savefig(filename, bbox_inches='tight')
        plt.close()


def plot_combined_distributions_per_var(samples_dict, df_france, vars_eco, output_dir="output/plots_comparaison"):
    """
    Génère un graphique par variable. Chaque graphique contient :
    - La distribution de la France entière (fond gris).
    - La distribution (courbe KDE) pour chaque polluant présent dans samples_dict.

    Args:
        samples_dict (dict): Dictionnaire { "Nom_Polluant": df_sample }
        df_france (pd.DataFrame): DataFrame de référence (France entière)
        vars_eco (list): Liste des colonnes à tracer
        output_dir (str): Dossier de sortie
    """
    os.makedirs(output_dir, exist_ok=True)

    # Définition d'une palette de couleurs pour les polluants
    # "viridis", "deep", ou une liste manuelle de couleurs
    palette = sns.color_palette("viridis", n_colors=len(samples_dict))

    for var in vars_eco.keys():
        # Nettoyage données France
        data_france = df_france[var].dropna()
        plt.figure(figsize=(12, 7))
        # Détection échelle log
        is_log = True if ("population" in var.lower() or "densite" in var.lower()) else False

        # --- 1. Plot France (Histogramme de fond) ---
        # On utilise stat="density" pour que l'échelle soit comparable aux courbes KDE
        sns.histplot(data_france, stat="density", kde=False, color="lightgray", 
                     label="France entière (Ref)", log_scale=is_log, alpha=0.4, element="step")
        
        # Ajout moyenne France (ligne verticale discrète)
        plt.axvline(data_france.mean(), color='gray', linestyle=':', linewidth=1, alpha=0.8)

        # --- 2. Boucle sur les polluants (Courbes KDE seulement) ---
        for i, (polluant_name, df_sample) in enumerate(samples_dict.items()):
            if var not in df_sample.columns:
                continue
                
            data_sample = df_sample[var].dropna()
            if data_sample.empty:
                continue
            
            color = palette[i]
            
            # On utilise kdeplot (courbe) au lieu de histplot pour éviter le chaos visuel
            sns.kdeplot(data_sample, color=color, label=polluant_name, 
                        log_scale=is_log, linewidth=2, warn_singular=False)
            
            # Optionnel : Ajouter un marqueur pour la moyenne sur l'axe X ou une petite ligne
            plt.axvline(data_sample.mean(), color=color, linestyle='--', linewidth=1.5, alpha=0.7)

        # Finalisation du graphique
        plt.title(f"Distribution comparative : {var}", fontsize=14)
        plt.xlabel(var)
        plt.ylabel("Densité")
        plt.legend(title="Populations")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)

        filename = f"{output_dir}/Combined_Distr_{var}.png"
        plt.savefig(filename, bbox_inches='tight', dpi=100)
        if vars_eco[var]:
            plt.show()
        plt.close()

    print(f"Graphiques générés dans : {output_dir}")