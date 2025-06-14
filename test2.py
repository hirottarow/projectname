import subprocess

def test_git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)

        try:
            subprocess.run(["git", "commit", "-m", "Test commit for push verification"], check=True)
        except subprocess.CalledProcessError:
            print("コミットすべき変更なし。")

        # pushの結果をキャプチャする
        result = subprocess.run(["git", "push"], check=True, capture_output=True, text=True)
        print("GitHubへのプッシュが成功しました！")
        print("---- git push output ----")
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
    test_git_push()
