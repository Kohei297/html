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