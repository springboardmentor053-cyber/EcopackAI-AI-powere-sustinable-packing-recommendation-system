from xgboost import XGBRegressor

def train_co2_model(X, y):
    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )
    model.fit(X, y)
    return model
