"""
快速导入 uploads 目录下的文档到数据库（跳过已存在的文件名）
用法: python import_docs.py
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import get_connection, init_db

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), 'uploads')

def get_existing_filenames():
    """获取数据库中已有的文件名"""
    with get_connection() as conn:
        cur = conn.execute("SELECT filename FROM files")
        return {row[0] for row in cur.fetchall()}

def extract_text(file_path):
    """简单文本提取"""
    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""

def import_uploads():
    init_db()
    existing = get_existing_filenames()
    print(f"数据库已有文档: {len(existing)} 个")

    files = [f for f in os.listdir(UPLOADS_DIR) if f.endswith('.txt')]
    print(f"uploads 目录发现 {len(files)} 个 txt 文件")

    added = 0
    with get_connection() as conn:
        for filename in files:
            if filename in existing:
                print(f"  跳过(已存在): {filename}")
                continue
            path = os.path.join(UPLOADS_DIR, filename)
            text = extract_text(path)
            if not text.strip():
                print(f"  跳过(空文件): {filename}")
                continue
            size = os.path.getsize(path)
            ext = filename.rsplit('.', 1)[-1].lower()
            # 先插入 files 表
            cur = conn.execute(
                "INSERT OR IGNORE INTO files (filename, filepath, file_type, file_size, category) "
                "VALUES (?, ?, ?, ?, ?)",
                (filename, path, ext, size, '考研资料')
            )
            file_id = cur.lastrowid
            # 再插入 file_contents 表
            conn.execute(
                "INSERT OR IGNORE INTO file_contents (file_id, content) VALUES (?, ?)",
                (file_id, text)
            )
            print(f"  导入: {filename} ({size} bytes, {len(text)} chars)")
            added += 1

    print(f"\n[OK] 导入完成，新增 {added} 个文档")

if __name__ == "__main__":
    import_uploads()
