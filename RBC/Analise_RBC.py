import os
import pandas as pd

# Matrizes de similaridade simbólica
CHEST_PAIN_SIM = {
    "ASY": {"ASY": 1.0, "ATA": 0.67, "NAP": 0.33, "TA": 0.0},
    "ATA": {"ASY": 0.67, "ATA": 1.0, "NAP": 0.67, "TA": 0.33},
    "NAP": {"ASY": 0.33, "ATA": 0.67, "NAP": 1.0, "TA": 0.67},
    "TA":  {"ASY": 0.0,  "ATA": 0.33, "NAP": 0.67, "TA": 1.0}
}

RESTING_ECG_SIM = {
    "Normal": {"Normal": 1.0, "ST": 0.5, "LVH": 0.0},
    "ST": {"Normal": 0.5, "ST": 1.0, "LVH": 0.5},
    "LVH": {"Normal": 0.0, "ST": 0.5, "LVH": 1.0}
}

ST_SLOPE_SIM = {
    "Up": {"Up": 1.0, "Flat": 0.5, "Down": 0.0},
    "Flat": {"Up": 0.5, "Flat": 1.0, "Down": 0.5},
    "Down": {"Up": 0.0, "Flat": 0.5, "Down": 1.0}
}

def load_data(path):
    return pd.read_csv(path)

def numeric_similarity(x1, x2, attr, df):
    min_val = df[attr].min()
    max_val = df[attr].max()
    return 1 - abs(x1 - x2) / (max_val - min_val)

def binary_similarity(x1, x2):
    return 1.0 if x1 == x2 else 0.0

def symbolic_similarity(attr, x1, x2):
    SIM_TABLES = {
        "ChestPainType": CHEST_PAIN_SIM,
        "RestingECG": RESTING_ECG_SIM,
        "ST_Slope": ST_SLOPE_SIM
    }
    table = SIM_TABLES.get(attr)
    return table.get(x1, {}).get(x2, 0.0)

def get_weights(defaults):
    print("=== Ajuste de Pesos (pressione Enter para manter valor) ===")
    for attr, w in defaults.items():
        inp = input(f"Peso para {attr} (atual {w}): ").strip()
        if inp:
            try:
                defaults[attr] = float(inp)
            except ValueError:
                print(f"Entrada inválida para {attr}, usando {w}.")
    return defaults

def get_input_case(attrs):
    print("\n=== Inserção de Caso de Entrada ===")
    case = {}
    for attr in attrs:
        inp = input(f"Valor para {attr}: ").strip()
        if attr in ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']:
            case[attr] = inp
        else:
            case[attr] = float(inp)
    return case

def compute_global_similarity(df, case, weights):
    total_w = sum(weights.values())
    def sim_row(row):
        s = 0.0
        for attr, w in weights.items():
            x1, x2 = case[attr], row[attr]
            if attr in ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']:
                local = numeric_similarity(x1, x2, attr, df)
            elif attr in ['ChestPainType', 'RestingECG', 'ST_Slope']:
                local = symbolic_similarity(attr, x1, x2)
            else:
                local = binary_similarity(x1, x2)
            s += w * local
        return s / total_w
    return df.apply(sim_row, axis=1)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    df = load_data('heart.csv')
    default_weights = {
        'Cholesterol': 0.15,
        'ChestPainType': 0.14,
        'FastingBS': 0.12,
        'RestingBP': 0.11,
        'ExerciseAngina': 0.10,
        'MaxHR': 0.08,
        'Oldpeak': 0.07,
        'ST_Slope': 0.07,
        'Age': 0.06,
        'Sex': 0.04,
        'RestingECG': 0.03
    }
    weights = default_weights.copy()
    attrs = list(weights.keys())

    while True:
        print("\n=== Menu ===")
        print("1 - Ver pesos")
        print("2 - Alterar pesos")
        print("3 - Inserir caso de entrada e calcular similaridade")
        print("0 - Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == '1':
            print("\nAtributo | Padrão | Atual")
            for attr in attrs:
                print(f"{attr:15} {default_weights[attr]:>6} -> {weights[attr]:>6}")

        elif choice == "2":
            weights = get_weights(weights)

        elif choice == '3':
            case = get_input_case(attrs)
            df['Similarity'] = compute_global_similarity(df, case, weights)
            df_sorted = df.sort_values(by='Similarity', ascending=False)
            top_10 = df_sorted.head(10)
            cols = attrs + ['HeartDisease', 'Similarity']

            print("\nCaso de entrada:\n", case)
            input("Aperte enter para calcular similaridade")
            print("\n=== Top 10 Casos Mais Similares ===")
            print(top_10[cols].to_string(index=False, float_format="{:.3f}".format))

        elif choice == '0':
            print("Encerrando...")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main()
