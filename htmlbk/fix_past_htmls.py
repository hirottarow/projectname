import os
import glob
import re
from datetime import datetime

HTMLBK_DIR = "htmlbk"
TIMESTAMP = int(datetime.now().timestamp())

# 注入する共通JSロジック
COMMON_JS = f"""
// バックアップファイルリストの初期化（JSから読み込み）
document.addEventListener('DOMContentLoaded', function() {{
    var selector = document.getElementById('backupFileSelector');
    if (!selector) return;
    
    // 一旦クリアしてデフォルトのみにする
    selector.innerHTML = '<option value="">-- 過去のイベント --</option>';
    
    if (typeof window.BACKUP_FILES !== 'undefined') {{
        window.BACKUP_FILES.forEach(function(file) {{
            var option = document.createElement('option');
            option.value = file;
            option.textContent = file.split('/').pop(); 
            
            // 現在のファイルを選択状態にする
            var currentFile = window.location.pathname.split('/').pop();
            // URLデコード（日本語ファイル名対策）
            try {{ currentFile = decodeURIComponent(currentFile); }} catch(e) {{}}
            
            if (file.endsWith(currentFile)) {{
                option.selected = true;
            }}
            selector.appendChild(option);
        }});
    }}
}});

// バックアップファイルへのナビゲーション
function navigateToBackup() {{
    var selector = document.getElementById('backupFileSelector');
    var selectedFile = selector.value;
    if (selectedFile) {{
        // ファイル名のみ抽出
        var target = selectedFile.split('/').pop();
        
        // 現在の場所(htmlbk内かどうか)に応じてパス調整
        if (location.pathname.indexOf("/htmlbk/") !== -1) {{
             window.location.href = target;
        }} else {{
             window.location.href = "htmlbk/" + target;
        }}
    }}
}}
"""

def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. backups.js scriptタグの更新（キャッシュバスター付与）とパス補正
    # htmlbkフォルダ内のファイルなので、backups.js は同階層にある
    # src="backups.js" または src="htmlbk/backups.js" を探す
    
    # すでにクエリパラメータがある場合も含めて正規表現で置換
    pattern_script = re.compile(r'<script src=".*backups\.js.*?"></script>')
    new_script_tag = f'<script src="backups.js?v={TIMESTAMP}"></script>'
    
    if pattern_script.search(content):
        content = pattern_script.sub(new_script_tag, content)
    else:
        # 見つからない場合は head の閉じタグ前に入れる
        content = content.replace('</head>', f'{new_script_tag}\n</head>')

    # 2. JSロジックの注入/置換
    # 既存の navigateToBackup 関数や event listener を探して削除し、新しいものを入れるのが確実
    
    # 古いロジックのパターン（簡易）
    # navigateToBackup 関数定義から次の showRanking 関数定義の前まで、あるいは scriptタグの終わりまでを置換したいが
    # 正規表現での完全マッチは難しいので、特定のキーワードが含まれていないか確認する
    
    if "document.addEventListener('DOMContentLoaded', function()" not in content:
        # ロジックがない場合、</body>直前の </script> の中に追加する
        # ただし、最後の <script> ブロックが showRanking などを閉じているはず
        
        # 既存の navigateToBackup があれば除去したいが、複雑になるので
        # 単純に「既存のnavigateToBackup関数を上書き」する形でJSを追加する
        
        # JSブロックの末尾に追加
        content = content.replace('</script>', f'\n{COMMON_JS}\n</script>')
        
        # ただしこれだと複数のScriptタグがある場合に全てに追加されかねない
        # 最後の </script> だけを狙う
        parts = content.rsplit('</script>', 1)
        if len(parts) == 2:
            content = parts[0] + f'\n{COMMON_JS}\n</script>' + parts[1]
            
    else:
        # 既にロジックがある場合（20251124など）
        # 内容をアップデートしたいので、DOMContentLoadedの部分を置換する
        # とはいえ、構造が一定でないので、少し強引だが
        # navigateToBackup関数定義を検索して、そこから少し広めに置換するか？
        
        # 簡易対応: Scriptタグの中身を解析するのはリスキーなので、
        # "20251124" のように既に動いているものは「そのまま」にするか、
        # あるいは「backups.js読み込みタグ」だけ更新してロジックは触らない手もある。
        # しかし今回の要望は「その他はなっていない」を直すこと。
        
        # ロジックが入っているファイルは修正済みとみなしてスキップしてもいいが、
        # 全体統一したほうが良い。
        
        # ここでは「DOMContentLoadedがないファイル」のみにロジックを注入する方針にする。
        # 20251124はユーザー曰く「反映されている」とのことなので、触らなくてよい（Scriptタグ更新だけ適用）
        pass

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed: {filepath}")

def main():
    files = glob.glob(os.path.join(HTMLBK_DIR, "*.html"))
    for f in files:
        fix_html_file(f)

if __name__ == "__main__":
    main()
