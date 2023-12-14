## はじめに　　

- git init 
    - cdに.gitファイルが作成される

- git clone https://github.com/"usser_name"/"repositori_name"
    - リポジトリのクローン
    - 現在のカレントディレクトリに直接ファイル形式でコピーされる
    - 勝手に紐ずく

- git pull
    -  リモートリポジトリの状態をローカルリポジトリ全体に反映

- git fetch
    - リモートリポジトリの状態をローカルの上位ブランチに反映

- git marge
    - ローカルの上位ブランチの状態をローカルの下位ブランチに反映
- git branch 
    - ブランチを確認
    - masterに当たるブランチの名前を確認しておく    "master"

- git checkout "branch_name"
    - ブランチを作成し移動

- git status
    -  gitの状態を確認

- git add "ex_commit_file_pass"     git add .
    - ファイルがコミット準備される

- git commit
    - addされたものがコミットされる

- git log
    - コミット等のログを確認できる
    - [:q]でログの終了

- git push origin ”buranch_name”
    - ブランチを指定してpushできる
    - リポジトリは紐付けされたものになる

- git checkout "master"
- git marge "branch_name"
    - ”branch_name”がmasterにマージされる

- git rebase -i --autosquash develop
    - "--autosquash"
        -  全てのコミットを一つにまとめることができる

- git hash-object -w faile_name
    - ''は無しでいい
    - error: invalid object 100644 が出た時に行う
    - ファイルのハッシュオブジェクトが壊れているらしい
    - ハッシュオブジェクトを作り直せる
        

## Linuxコマンド
- cd "directory_path"
    - ディレクトリの移動

- ls
    - 中身を確認できる 
    


