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
from sklearn.model_selection import StratifiedKFold, train_test_split, GridSearchCV
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.neural_network import MLPClassifier  # MLP de Backpropagation

# Métricas
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix

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
    pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=random_seed)),
        ("classifier", MLPClassifier(max_iter=300, early_stopping=True, random_state=random_seed))
    ])

    # Grid de parâmetros para ajuste fino
    param_grid = {
        'classifier__hidden_layer_sizes': [
        (64,32), (128,64), (256,128),
        (64,64,32), (128,128,64)
    ],
    'classifier__alpha': [0.0001, 0.001, 0.01, 0.1],
    'classifier__learning_rate_init': [0.0001, 0.001, 0.01, 0.1],
    'smote__sampling_strategy': [0.3, 0.5, 0.7]  # Controle de balanceamento
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
        cv=5,
        n_jobs=-1,
        verbose=2
    )

    grid_search.fit(x_train, y_train)

    best_model = grid_search.best_estimator_
    print("Melhores Parâmetros:", grid_search.best_params_)

    """Parte 4 - Avaliação Interna"""
    y_pred = best_model.predict(x_val)
    print("=== Avaliação Interna (bank.csv) ===")
    print("Acurácia:", round(accuracy_score(y_val, y_pred), 2))
    print("Precisão:", round(precision_score(y_val, y_pred), 2))
    print("Recall:", round(recall_score(y_val, y_pred), 2))
    print("F1 Score:", round(f1_score(y_val, y_pred), 2))

    """Parte 5 - Validação Externa"""
    df_full = pd.read_csv('dataset_bank/bank-full.csv', sep=';')
    df_full = df_full.drop("duration", axis=1)
    X_full = df_full.drop("y", axis=1)
    y_full = df_full["y"].map({"yes": 1, "no": 0})

    y_full_pred = best_model.predict(X_full)
    print("=== Avaliação Externa (bank-full.csv) ===")
    print("Acurácia:", round(accuracy_score(y_full, y_full_pred), 2))
    print("Precisão:", round(precision_score(y_full, y_full_pred), 2))
    print("Recall:", round(recall_score(y_full, y_full_pred), 2))
    print("F1 Score:", round(f1_score(y_full, y_full_pred), 2))

    print("=== Matriz de Confusão (bank-full.csv) ===")
    cm = confusion_matrix(y_full, y_full_pred)
    print("              Predito")
    print("           |  0  |  1")
    print("      -----------------")
    print(f"Real  0   | {cm[0][0]:>3} | {cm[0][1]:>3}  ← Falsos Positivos")
    print(f"      1   | {cm[1][0]:>3} | {cm[1][1]:>3}  ← Verdadeiros Positivos")
if __name__ == "__main__":
    # CWD = Diretório do script .py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
