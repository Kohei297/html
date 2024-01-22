# ! pip3 install --upgrade pip
# ! pip3 install pkg_resouces
# ! pip3 install openpyxl
# ! pip3 install pandas
# ! pip3 install scipy

import pip
import pkg_resources
import os
import openpyxl
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import japanize_matplotlib
from matplotlib.colors import ListedColormap 
import matplotlib



# pip関係, フォルダ関係
def pip_check(pip_name):        #pipでライブラリをインストールする関数
    list_ = [_lib.project_name for _lib in pkg_resources.working_set]
    if pip_name not in list_:
        pip.main(['install', '--upgrade', 'pip'])
        pip.main(['install', pip_name])
        print('Installed: ' + pip_name)
    else:
        print('Already installed: ' + pip_name)

def check_dir(fig_dir):     #フォルダの有無を確認なければ作る
    try:
        os.makedirs(fig_dir)
    except FileExistsError:
        pass




# openpyxl関係
def write_list_xlsx_sheet(sheet, input_list, start_row = 1, start_col = 1):     #リストをエクセルに書き込む関数 
    for y, row_data in enumerate(input_list):
        for x, cell_data in enumerate(row_data):
            sheet.cell(row=start_row + y, column = start_col + x, value = input_list[y][x])




# 検定関係
def make_pair(target_list, delta):#リストから指定の間隔をあけて二つを取り出す
    pairs = [[target_list[i], target_list[i + delta]] for i in range(len(target_list) - delta)]
    return pairs

def facter_binarization(df, facter_th = ['HbA1c', '>= 5.6']):        #カテゴリー変数を２値化、trueが１、true_valueはリスト
    df[f'{facter_th[0]}_'] = list(eval(f"(df['{facter_th[0]}']\
                                       .mask(df['{facter_th[0]}'] {facter_th[1]}, 1)\
                                       .mask(~(df['{facter_th[0]}'] {facter_th[1]}), 0)\
                                       .mask(df['{facter_th[0]}'].isnull(), np.nan))"
                                       ))

def average_delta_check_for_binary_data(df, decimal_point = 3): #０、１カラムを検定
    column_names = df.columns.to_list()
    for column_name in column_names:
        if df[column_name].unique() == [0, 1]:
            average_delta_check(column_name, df, decimal_point, save_xlsx_name = f'{column_name}検定結果')

def average_delta_check(aim_facter, df, decimal_point = 3, save_xlsx_name = '検定結果'):  #平均値の差があるかどうか
    column_names = df.columns.to_list()
    data_size = len(df)     ####   
    df_hit = df[df[aim_facter] == 1]    #異常あり
    df_miss = df[df[aim_facter] == 0]   #異常なし
    df_lists = [['column_name', 'method', 'hit_p', 'miss_p', 'method_t', 'ttest_p']]
    for column_name in column_names:
        if df[column_name].dtypes == 'float':
            if len(df[column_name].unique()) < 5:
                continue
        else:
            continue
        if data_size > 1000:
            method = 'ks'
            hit_ks_p = round(stats.kstest(df_hit[column_name], 'norm')[1], decimal_point)
            miss_ks_p = round(stats.kstest(df_miss[column_name], 'norm')[1], decimal_point)
            if hit_ks_p > 0.05 or miss_ks_p > 0.05:
                result = 'not_normal'
            else:
                result = 'normal'
        else:
            method = 'shapiro'
            hit_shapiro_p = round(stats.shapiro(df_hit[column_name])[1], decimal_point)
            miss_shapiro_p = round(stats.shapiro(df_miss[column_name])[1], decimal_point)
            if hit_shapiro_p > 0.05 or miss_shapiro_p > 0.05:
                result = 'not_normal'
            else:
                result = 'normal'
        if result == 'not_normal':      #正規分布でない場合
            mannwhitneyu_p = round(stats.mannwhitneyu(df_hit[column_name], df_miss[column_name])[1], decimal_point)
            df_lists.append([column_name, method, eval(r'hit_{0}_p'.format(method)), eval(r'miss_{0}_p'.format(method)), 'Man_U', mannwhitneyu_p])
        elif result == 'normal':        #正規分布の場合
            f_p = stats.f_oneway(df_hit[column_name], df_miss[column_name])[1]      #F検定、0.05以上ならば等分散
            if f_p < 0.05:
                method_t = 'welch'
                ttest_p = round(stats.ttest_ind(df_hit[column_name], df_miss[column_name], equal_var = False)[1], decimal_point)      #等分散でない場合、ウェルチのt検定
            else :
                method_t = 'student'
                ttest_p = round(stats.ttest_ind(df_hit[column_name], df_miss[column_name], equal_var = True)[1], decimal_point)       #等分散の場合、スチューデントのt検定 
            df_lists.append([column_name, method,  eval(r'hit_{0}_p'.format(method)), eval(r'miss_{0}_p'.format(method)), method_t, ttest_p])
    #一枚エクセルに書き込み
    # save_df = pd.DataFrame(df_lists, columns = ['column_name', 'method', 'hit_p', 'miss_p', 'method_t', 'ttest_p'])
    # with pd.ExcelWriter('検定結果.xlsx') as writer:
    #     save_df.to_excel(writer, sheet_name = '検定結果')

    #excelに書き込み
    book = openpyxl.Workbook()
    sheet = book['Sheet']
    sheet.title = '検定結果'
    write_list_xlsx_sheet(sheet, df_lists)
    book.save(f'{save_xlsx_name}.xlsx')  





# 保険関係
def mets_judge(df, metS_facter = [['性別', '腹囲'], ['収縮期血圧', '拡張期血圧'], ['空腹時血糖', 'HbA1c'], ['中性脂肪', 'HDL']]):   #メタボ判定
    #腹囲判定
    df['腹囲_'] = (df[metS_facter[0][1]].mask((df[metS_facter[0][0]] == 1) & (df[metS_facter[0][1]] >= 85), True) # 男性       #どちらもデータがあってTrueの場合True
                            .mask((df[metS_facter[0][0]] == 0) & (df[metS_facter[0][1]] >= 90), True) # 女性    　
                            .mask((df[metS_facter[0][0]] == 1) & (df[metS_facter[0][1]] < 85), False)  # 男性      #どちらもデータがあってFalseの場合False
                            .mask((df[metS_facter[0][0]] == 0) & (df[metS_facter[0][1]] < 90), False)  # 女性
                            .mask((df[metS_facter[0][0]].isnull()) | (df[metS_facter[0][1]].isnull()), np.nan)    #性別 or 腹囲がない場合nan
    )

    #血圧判定
    df['血圧_'] = (df[metS_facter[1][0]].mask((df[metS_facter[1][0]] >= 130) | (df[metS_facter[1][1]] >= 85), True)      # どちらかがTrueの場合True
                            .mask((df[metS_facter[1][0]] < 130) & (df[metS_facter[1][1]] < 85), False)            # どちらもFalseの場合False
                            .mask((~(df[metS_facter[1][0]] >= 130) & ~(df[metS_facter[1][1]] >= 85))                    # どちらもFalseかnanであって
                                  & ((df[metS_facter[1][0]].isnull()) | (df[metS_facter[1][1]].isnull())), np.nan)      # どちらもnanの場合nan
    )

    #血糖判定
    df['血糖_'] = (df[metS_facter[2][0]].mask((df[metS_facter[2][0]] >= 110) | (df[metS_facter[2][1]] >= 6.0), True)          # どちらかがTrueの場合True
                            .mask((df[metS_facter[2][0]] < 110) & (df[metS_facter[2][1]] < 6.0), False)                # どちらもFalseの場合False
                            .mask((~(df[metS_facter[2][0]] >= 110) & ~(df[metS_facter[2][1]] >= 6.0))                   # どちらもFalseかnanであって
                                  & ((df[metS_facter[2][0]].isnull()) | (df[metS_facter[2][1]].isnull())), np.nan)      # どちらもnanの場合nan
    )

    #脂質判定
    df['脂質_'] = (df[metS_facter[3][0]].mask((df[metS_facter[3][0]] >= 150) | (df[metS_facter[3][1]] <= 40), True)           # どちらかがTrueの場合True
                            .mask((df[metS_facter[3][0]] < 150) & (df[metS_facter[3][1]] > 40), False)               # どちらもFalseの場合False
                            .mask((~(df[metS_facter[3][0]] >= 150) & ~(df[metS_facter[3][1]] <= 40))                 # どちらもFalseかnanであって     
                                  & ((df[metS_facter[3][0]].isnull()) | (df[metS_facter[3][1]].isnull())), np.nan)      # どちらもnanの場合nan
    )

    df['MetS'] = (df['腹囲'] 
                .mask((df['腹囲_'].isnull()) |                                                           # 腹囲がない or                      # 4-1
                     ((df['腹囲_'] == 1) &                                                               # 腹囲がある &
                     ((df['血圧_'].isnull()) & (df['血糖_'].isnull()) & (df['脂質_'].isnull()) |          # 3項目がない(nanがある) or           # 4-2 
                     ((df[['腹囲_', '血圧_', '血糖_', '脂質_']].sum(axis = 1) <= 1) &                                    # 1つの項目が異常 &
                     ((df['血圧_'].isnull()) | (df['血糖_'].isnull()) | (df['脂質_'].isnull())))))         # nanがある                         # 4-3
                       , 'N/A')                                                                         # 判定なし         

                .mask((df['腹囲_'] == 0) |                                                               # 腹囲正常　or                       # 3-1
                     ((df['腹囲_'] == 1) &                                                               # 腹囲異常　&
                      (df[['腹囲_', '血圧_', '血糖_', '脂質_']].sum(axis = 1) == 0) &                                    # 3項目が正常 &
                      (df['血圧_'].notnull()) & (df['血糖_'].notnull()) & (df['脂質_'].notnull()))        # 3項目がある(nanがない)              # 3-2
                       , 'not_MetS')                                                                    # 腹囲がない & 異常なし

                .mask((df['腹囲_'] == 1) &                                                               # 腹囲異常　& 
                      (df[['腹囲_', '血圧_', '血糖_', '脂質_']].sum(axis = 1) == 1) &                                    # 1つの項目が異常 &
                      (df['血圧_'].notnull()) & (df['血糖_'].notnull()) & (df['脂質_'].notnull())         # 3項目がある(nanがない)              # 2-1
                       , 's/o_MetS')                                                                    # 腹囲がある & 1つの項目が異常
                  
                .mask(((df['腹囲_'] == 1) & (df[['腹囲_', '血圧_', '血糖_', '脂質_']].sum(axis = 1) >= 2))                # 1-1, 1-2
                       , 'MetS')                                                                        # 腹囲がある & 2つ以上の項目が異常                                                                     
    )
    
    df_metS = df[df['MetS'] == 'MetS']
    df_so_metS = df[df['MetS'] == 's/o_MetS']
    df_non_metS = df[df['MetS'] == 'not_MetS']
    df_na_metS = df[df['MetS'] == 'N/A']
    return df_metS, df_so_metS, df_non_metS, df_na_metS





# マップ関係
def colors_scale(legend_unique, cmap_name = 'bwr_r', division_number = 5):                  #色の分け方の定義
    n_min = 1  #min(arr)
    n_max = division_number   #max(arr)
    cmap = plt.colormaps[cmap_name]
    norm = matplotlib.colors.Normalize(vmin=n_min, vmax=n_max)
    arr = [cmap(norm(r)) for r in legend_unique]
    return arr, cmap, norm

def plot_map_colors(df, facter_column = '区分'):                                            # マップの作製
    legend_unique = sorted(df[facter_column].unique().tolist())
    labels = {1: '有意に高い', 2: '有意で無いが高い', 3: 'なし' ,4: '有意で無いが低い', 5: '有意に低い'}
    ratio_legend = [labels[a] for a in legend_unique]
    target_colors, cmap, norm = colors_scale(legend_unique)
    cmaps = ListedColormap(target_colors, name="custom")
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axis('off')                      # 軸を表示しない
    df.plot(
        ax = ax, 
        column = facter_column, 
        categorical = True,
        cmap = cmaps,
        edgecolor = '#000000', 
        linewidth = 1, 
        legend = True, 
        legend_kwds={'labels': ratio_legend}
        )

    # #ラベルを付ける
    # for i, txt in enumerate(df['市町村名']):
    #     ax.annotate(txt, (df.geometry[i].centroid.x, df.geometry[i].centroid.y),fontsize= 6,horizontalalignment='center', verticalalignment='center')
    # fig.text(0.5, 0.1, '※本資料を活用するには、必ず、各市町村の表も合わせて解釈を行うこと。', ha='center',fontsize= 10, horizontalalignment="center",verticalalignment="center")







