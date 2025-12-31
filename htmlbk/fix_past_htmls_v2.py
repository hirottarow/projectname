import os
import glob
import re
from datetime import datetime

HTMLBK_DIR = "htmlbk"
TIMESTAMP = int(datetime.now().timestamp())

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
        var target = selectedFile.split('/').pop();
        if (location.pathname.indexOf("/htmlbk/") !== -1) {{
             window.location.href = target;
        }} else {{
             window.location.href = "htmlbk/" + target;
        }}
    }}
}}
"""

def fix_html_file(filepath):
    # BOM対策のため utf-8-sig で開く
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read()

    # 1. script src 更新
    pattern_script = re.compile(r'<script src=".*backups\.js.*?"></script>')
    new_script_tag = f'<script src="backups.js?v={TIMESTAMP}"></script>'
    
    if pattern_script.search(content):
        content = pattern_script.sub(new_script_tag, content)
    else:
        # なければ追加
        content = content.replace('</head>', f'{new_script_tag}\n</head>')

    # 2. JS注入
    # "window.BACKUP_FILES.forEach" が含まれていなければ注入する
    if "window.BACKUP_FILES.forEach" not in content:
        print(f"Injecting logic into {filepath}...")
        
        # 既存の </script> の直前に入れる
        parts = content.rsplit('</script>', 1)
        if len(parts) == 2:
            content = parts[0] + f'\n{COMMON_JS}\n</script>' + parts[1]
        else:
            # scriptタグがなければbodyの最後に追加
            content = content.replace('</body>', f'<script>{COMMON_JS}</script>\n</body>')
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
