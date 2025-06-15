import subprocess

git_dir = r"C:\Users\geten\Documents\GitHub\projectname\.git"
work_tree = r"C:\Users\geten\Documents\GitHub\projectname"
file_to_add = "README.md"  # ここをプッシュしたいファイル名に書き換えてください

try:
    # git add
    subprocess.run(
        ["git", "--git-dir", git_dir, "--work-tree", work_tree, "add", file_to_add],
        check=True
    )
    print(f"{file_to_add} をステージングしました。")

    # git commit
    commit_message = f"Add or update {file_to_add}"
    subprocess.run(
        ["git", "--git-dir", git_dir, "--work-tree", work_tree, "commit", "-m", commit_message],
        check=True
    )
    print("コミットしました。")

    # git push
    subprocess.run(
        ["git", "--git-dir", git_dir, "--work-tree", work_tree, "push"],
        check=True
    )
    print("プッシュ成功")

except subprocess.CalledProcessError as e:
    print("Git操作でエラー:", e)
