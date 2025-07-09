# Trabalho Final Inteligência Artificial I
# Redes Neurais Multi-Layer Perceptrons (MLPs)
# Luiz Augusto Inthurn e Herick Vitor Vieira Bittencourt
# 2025/1

import os
import pandas as pd

# Pre-Processamento
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Rede neural e pesquisa de hiperparâmetros
from sklearn.model_selection import train_test_split, GridSearchCV
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.neural_network import MLPClassifier  # MLP de Backpropagation

# Métricas
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def main():
    # Seed utilizada pelo modelo, defina None p/ resultados aleatórios
    random_seed = None

    """Parte 1 - Extração de atributos e output"""
    df_training = pd.read_csv("dataset_bank/bank.csv", sep=";")
    
    # Atributos não utilizados
    df_training = df_training.drop("duration", axis=1)  # Evita viés futuro

    # Separação de atributos e alvo
    X = df_training.drop("y", axis=1)
    Y = df_training["y"].map({"yes": 1, "no": 0})

    """Parte 2 - Mapeamento e transformação dos atributos por tipo de dado"""
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_cols = X.select_dtypes(include=["int64"]).columns.tolist()

    ## Colunas numéricas são padronizadas (média 0, desvio padrão 1)
    ## Colunas categóricas são codificadas em vetores binários (One-Hot)
    preprocessor = ColumnTransformer(transformers=[
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
    ])

    """Parte 3 - Pesquisa de Hiperparâmetros e Balanceamento"""
    # Pipeline com SMOTE para oversampling e MLPClassifier
    # SMOTE balanceia a classe minoritária gerando exemplos sintéticos antes de treinar a MLP
    # Iterações maximas em 3000 devido a early stopping (não há melhorias significativas p/ continuar)
    pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=random_seed)),
        ("classifier", MLPClassifier(max_iter=3000, early_stopping=True, random_state=random_seed))
    ])

    # Grid de parâmetros para ajuste fino
    param_grid = {
        'classifier__hidden_layer_sizes': [(32,16), (64,32,16)],    # Camadas ocultas
        'classifier__alpha': [0.0001, 0.001, 0.01],                 # Evita overfitting penalizando pesos maiores
        'classifier__learning_rate_init': [0.001, 0.01]             # Limite de aprendizado
    }

    # Divisão treino/validação interna
    x_train, x_val, y_train, y_val = train_test_split(X, Y, test_size=0.2, random_state=random_seed)

    # Configuração do GridSearch:
    # Busca o melhor modelo a partir do scoring e validação 3-fold
    # Nota: n_jobs=-1 (Usar todos os núcleos disponíveis)
    grid_search = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        scoring='f1',
        cv=3,
        n_jobs=-1
    )

    grid_search.fit(x_train, y_train)

    best_model = grid_search.best_estimator_
    print("Melhores Parâmetros:", grid_search.best_params_)

    """Parte 4 - Avaliação Interna"""
    y_pred = best_model.predict(x_val)
    print("=== Avaliação Interna (bank.csv) ===")
    print("Acurácia:", accuracy_score(y_val, y_pred))
    print("Precisão:", precision_score(y_val, y_pred))
    print("Recall:", recall_score(y_val, y_pred))
    print("F1 Score:", f1_score(y_val, y_pred))

    """Parte 5 - Validação Externa"""
    df_full = pd.read_csv('dataset_bank/bank-full.csv', sep=';')
    df_full = df_full.drop("duration", axis=1)
    X_full = df_full.drop("y", axis=1)
    y_full = df_full["y"].map({"yes": 1, "no": 0})

    y_full_pred = best_model.predict(X_full)
    print("=== Avaliação Externa (bank-full.csv) ===")
    print("Acurácia:", accuracy_score(y_full, y_full_pred))
    print("Precisão:", precision_score(y_full, y_full_pred))
    print("Recall:", recall_score(y_full, y_full_pred))
    print("F1 Score:", f1_score(y_full, y_full_pred))

if __name__ == "__main__":
    # CWD = Diretório do script .py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
