import os
import glob
import re
from datetime import datetime

HTMLBK_DIR = "htmlbk"
TIMESTAMP = int(datetime.now().timestamp())

COMMON_JS = f"""
// バックアップファイルリストの初期化（JSから読み込み・修正版）
document.addEventListener('DOMContentLoaded', function() {{
    var selector = document.getElementById('backupFileSelector');
    if (!selector) return;
    
    // 既存のリストをクリアして再構築（重複防止 & 最新ロジック適用）
    selector.innerHTML = '<option value="">-- 過去のイベント --</option>';
    
    if (typeof window.BACKUP_FILES !== 'undefined') {{
        window.BACKUP_FILES.forEach(function(file) {{
            var option = document.createElement('option');
            option.value = file;
            option.textContent = file.split('/').pop(); 
            
            // 現在のファイルを選択状態にする
            var currentFile = window.location.pathname.split('/').pop();
            try {{ currentFile = decodeURIComponent(currentFile); }} catch(e) {{}}
            
            if (file.endsWith(currentFile)) {{
                option.selected = true;
            }}
            selector.appendChild(option);
        }});
    }}
}});

// バックアップファイルへのナビゲーション（上書き）
window.navigateToBackup = function() {{
    var selector = document.getElementById('backupFileSelector');
    var selectedFile = selector.value;
    if (selectedFile) {{
        var target = selectedFile.split('/').pop();
        if (location.pathname.indexOf("/htmlbk/") !== -1) {{
             window.location.href = target;
        }} else {{
             window.location.href = "htmlbk/" + target;
        }}
    }}
}};
"""

def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read()

    # 1. script src 更新
    pattern_script = re.compile(r'<script src=".*backups\.js.*?"></script>')
    new_script_tag = f'<script src="backups.js?v={TIMESTAMP}"></script>'
    
    if pattern_script.search(content):
        content = pattern_script.sub(new_script_tag, content)
    else:
        content = content.replace('</head>', f'{new_script_tag}\n</head>')

    # 2. JS注入判定
    # "option.selected = true" が含まれていない、または "window.BACKUP_FILES" 自体がない場合に注入
    # ただし、COMMON_JSを既に注入済みの場合はスキップしたい
    # COMMON_JSの特徴的なコメント "バックアップファイルリストの初期化（JSから読み込み・修正版）" で判定
    
    if "バックアップファイルリストの初期化（JSから読み込み・修正版）" not in content:
        print(f"Injecting logic into {filepath}...")
        
        # 末尾の </script> の直前ではなく、</body> の直前に追加する（確実に最後にするため）
        # <script>タグで囲って追加
        
        if '</body>' in content:
            content = content.replace('</body>', f'<script>\n{COMMON_JS}\n</script>\n</body>')
        else:
            # bodyタグがない変なファイルなら末尾に
            content += f'\n<script>\n{COMMON_JS}\n</script>'
    else:
        print(f"Logic already present in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    files = glob.glob(os.path.join(HTMLBK_DIR, "*.html"))
    for f in files:
        fix_html_file(f)

if __name__ == "__main__":
    main()
