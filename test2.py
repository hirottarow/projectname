import subprocess

def test_git_push():
    try:
        # 現在の変更をステージング（ここは確認用なので無理にコミットしなくてもOK）
        subprocess.run(["git", "add", "."], check=True)

        # ダミーコミット（何も変更がなければエラーになるので例外処理で無視）
        try:
            subprocess.run(["git", "commit", "-m", "Test commit for push verification"], check=True)
        except subprocess.CalledProcessError:
            print("コミットすべき変更なし。")

        # プッシュを試みる
        subprocess.run(["git", "push"], check=True)

        print("GitHubへのプッシュが成功しました！")

    except subprocess.CalledProcessError as e:
        print("Git操作でエラーが発生しました:", e)

if __name__ == "__main__":
    test_git_push()
