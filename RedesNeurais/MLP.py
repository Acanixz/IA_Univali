# Trabalho Final Inteligência Artificial I
# Redes Neurais Multi-Layer Perceptrons (MLPs)
# Luiz Augusto Inthurn e Herick Vitor Vieira Bittencourt
# 2025/1

# Outros/Dependencias
import os
import pandas as pd

# Pre-Processamento
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

# Rede neural
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier # MLP de Backpropagation

# Resultados
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def main():
    """Parte 1 - Extração de atributos e output"""
    # Dataframe de treinamento
    df_training = pd.read_csv("dataset_bank/bank.csv", sep=";")
    
    # Atributos não utilizados
    df_training = df_training.drop("duration", axis=1)

    # Mapeamento de atributos e alvo
    X = df_training.drop("y", axis=1) # Todos atributos (exceto y pois é output)
    Y = df_training["y"].map({"yes": 1, "no": 0})

    """Parte 2 - Mapeamento e transformação dos atributos por tipo de dado"""
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_cols = X.select_dtypes(include=["int64"]).columns.tolist()

    ## Colunas numéricas são normalizadas (pivotadas entre 0 e 1)
    ## Colunas de texto(categoricos) são codificados p/ vetores binários
    preprocessor = ColumnTransformer(transformers=[
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
    ])

    """Parte 3 - Treinamento"""
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", MLPClassifier(hidden_layer_sizes=(32,16), max_iter=3000, early_stopping=True, random_state=42))
    ])

    # Dividir os dados em treino e validação (80% treino, 20% validação)
    x_train, x_val, y_train, y_val = train_test_split(X, Y, test_size=0.2, random_state=42)

    pipeline.fit(x_train, y_train)

    # Prever usando o conjunto de validação
    y_pred = pipeline.predict(x_val)

    # Calcular as métricas
    print("Acurácia:", accuracy_score(y_val, y_pred))
    print("Precisão:", precision_score(y_val, y_pred))
    print("Recall:", recall_score(y_val, y_pred))
    print("F1 Score:", f1_score(y_val, y_pred))

    # Carregar o dataset completo para validação externa
    df_full = pd.read_csv('dataset_bank/bank-full.csv', sep=';')
    df_full = df_full.drop("duration", axis=1)
    X_full = df_full.drop("y", axis=1)
    y_full = df_full["y"].map({"yes": 1, "no": 0})

    # Prever e avaliar no dataset completo
    y_full_pred = pipeline.predict(X_full)
    accuracy_full = accuracy_score(y_full, y_full_pred)
    precision_full = precision_score(y_full, y_full_pred)
    recall_full = recall_score(y_full, y_full_pred)
    f1_full = f1_score(y_full, y_full_pred)

    accuracy_full, precision_full, recall_full, f1_full


if __name__ == "__main__":
    # CWD = Diretório do script .py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()