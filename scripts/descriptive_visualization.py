import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

def setup_styles():
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    sns.set_theme(style="whitegrid")

def plot_distributions(df, cols, output_dir="output/Desc_All_Cities"):
    """Plots histograms for specified columns."""
    os.makedirs(output_dir, exist_ok=True)
    
    for col in cols:
        plt.figure(figsize=(9, 5))
        data = df[col].dropna()
        
        # Utilisation d'une échelle log
        if col not in ["nb_campings_2022", "nb_hotels_2022"] :
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
            color= "teal" #sns.color_palette("viridis")[0] if log_scale else sns.color_palette("pastel")[1]
        )
        
        plt.title(f'Distribution de {col} {echelle_suffix}')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/hist_{col}.png", dpi=300)
        plt.close()

def plot_correlation_heatmap(df, output_dir="output/Desc_All_Cities"):
    """Generates and saves the correlation matrix."""
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
    plt.savefig(f"{output_dir}/correlogram.png", dpi=300)
    plt.close()

def plot_comparative_distributions(df_sample, df_france, polluant_name, vars_eco, output_dir="output/plots_comparaison"):
    """Plots France vs Sample distributions."""
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
        
        # Plot Sample
        sns.histplot(data_sample, stat="density", kde=True, color="teal",
                     label=f"Échantillon ({polluant_name})", log_scale=log_scale, alpha=0.6)
        
        # Means
        plt.axvline(data_france.mean(), color='gray', linestyle='--', label=f"Moyenne FR")
        plt.axvline(data_sample.mean(), color='teal', linestyle='-', label=f"Moyenne Éch")
        
        plt.title(f"Distribution : {var} ({polluant_name})")
        plt.legend()
        
        filename = f"{output_dir}/Distr_{polluant_name}_{var}.png"
        plt.savefig(filename, bbox_inches='tight')
        plt.close()