import master_code as mc

# Health class

def categorize_(df, categorize_facter):# カテゴリー変数を２値化、trueが１、true_valueはリスト
    facters = list(categorize_facter.keys())
    true_values = list(categorize_facter.values())
    for i, true_value in enumerate(true_values):
        k += f"df['{facters[i]}'] == {true_value} |"
    df[f'categorize_{facters[i]}'] = list(eval(k[: -1]))
    return df