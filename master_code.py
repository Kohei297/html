import pip
import pkg_resources
import os
def pip_check(pip_name):
    list_ = [_lib.project_name for _lib in pkg_resources.working_set]
    if pip_name not in list_:
        pip.main(['install', '--upgrade', 'pip'])
        pip.main(['install', pip_name])
        print('Installed: ' + pip_name)
    else:
        print('Already installed: ' + pip_name)

#フォルダの有無を確認なければ作る
def check_dir(fig_dir):
    try:
        os.makedirs(fig_dir)
    except FileExistsError:
        pass

