from sklearn.pipeline import Pipeline
import statsmodels.api as sm


def lasso_select_and_OLS(df_pol, lasso_pipeline):

    y_train = df_pol['valeur_brute']
    X_train = df_pol[['population_2022', 'mediane_niveau_vie_2021', 'densite_population_2022',
        'part_commerce_transport_services_2023', 'part_industrie_2023',
        'nb_hotels_2022', 'nb_etablissements_2023', 'taux_activite_2022',
        'part_construction_2023', 'nb_campings_2022']]

    lasso_optimal = lasso_pipeline.fit(X_train, y_train)

    features_selec = X_train.columns[lasso_optimal.named_steps['model'].coef_ != 0]
    
    print("Variables sélectionnées:")
    for var in features_selec:
        print(var)

    if len(features_selec) > 0:

        X_train_sm = sm.add_constant(X_train[features_selec])
        model_sm = sm.OLS(y_train, X_train_sm).fit()
        print(model_sm.get_robustcov_results().summary())

    else:
        print("Aucune variable explicative sélectionnée.")