import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder

def save_artifact(obj, path):
    joblib.dump(obj, path)

def load_artifact(path):
    return joblib.load(path)

def create_scaler():
    return StandardScaler()

def create_label_encoder():
    return LabelEncoder()
