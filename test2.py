import subprocess

def git_sync_and_push():
    try:
        subprocess.run(["git", "add", "."], check=True)

        try:
            subprocess.run(["git", "commit", "-m", "Auto commit before push"], check=True)
        except subprocess.CalledProcessError:
            print("コミットすべき変更はありません。")

        # リモートの変更を取得してリベースで反映
        subprocess.run(["git", "pull", "--rebase"], check=True)

        # プッシュ実行
        result = subprocess.run(["git", "push"], check=True, capture_output=True, text=True)
        print("GitHubへのプッシュが成功しました！")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Git操作でエラーが発生しました:")
        print(e)
        if e.stdout:
            print("標準出力:")
            print(e.stdout)
        if e.stderr:
            print("標準エラー出力:")
            print(e.stderr)

if __name__ == "__main__":
    git_sync_and_push()
