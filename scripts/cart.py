import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import GridSearchCV


def perform_cart_gridsearch(seed, X_train, X_test, y_train, y_test, log_conversion=False):
    """ Génère l'arbre CART optimal au sens de la squarred_error par GridSearch """
    # Grid Search
    param_grid = {
        'max_depth': [3, 5, 7, 10], 
        'min_samples_split': [10, 20],
        'min_samples_leaf': [10, 20, 30],
        'ccp_alpha': [0.0, 0.001]
    }

    model = DecisionTreeRegressor(criterion="squared_error", random_state=seed)

    grid = GridSearchCV(model, param_grid, cv=5, scoring='r2', n_jobs=-1)
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_

    # Prédictions sur le Test
    y_pred_log = best_model.predict(X_test)

    if log_conversion:
        y_pred_real = np.expm1(y_pred_log)
        # Calcul des métriques et performance
        r2 = r2_score(y_test, y_pred_real)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_real))
        mae = mean_absolute_error(y_test, y_pred_real)
        return best_model, y_pred_real, r2, rmse, mae
    else:
        # Calcul des métriques et performance
        r2 = r2_score(y_test, y_pred_log)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_log))
        mae = mean_absolute_error(y_test, y_pred_log)
        return best_model, y_pred_log, r2, rmse, mae
