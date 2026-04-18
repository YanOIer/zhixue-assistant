"""数据库操作模块。"""

import os
import sqlite3
from contextlib import contextmanager


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.getenv('ZHIXUE_DB_PATH', os.path.join(PROJECT_ROOT, 'zhixue.db'))
FALLBACK_DB_PATH = os.path.join(PROJECT_ROOT, '.runtime', 'zhixue_runtime.db')
ACTIVE_DB_PATH = None


def _ensure_db_directory(db_path):
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


def _connect(db_path):
    _ensure_db_directory(db_path)
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute('PRAGMA journal_mode=MEMORY')
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def get_db_path():
    """返回当前实际使用的数据库路径。"""
    global ACTIVE_DB_PATH
    if ACTIVE_DB_PATH:
        return ACTIVE_DB_PATH
    ACTIVE_DB_PATH = DEFAULT_DB_PATH
    return ACTIVE_DB_PATH


@contextmanager
def get_connection():
    """创建数据库连接并自动提交/关闭。"""
    global ACTIVE_DB_PATH
    primary_path = get_db_path()
    try:
        conn = _connect(primary_path)
    except sqlite3.OperationalError:
        if os.getenv('ZHIXUE_DB_PATH'):
            raise
        ACTIVE_DB_PATH = FALLBACK_DB_PATH
        print(f"主数据库不可写，切换到运行时数据库: {ACTIVE_DB_PATH}")
        conn = _connect(ACTIVE_DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """
    初始化数据库
    创建必要的表结构
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                category TEXT DEFAULT '其他',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_contents (
                file_id INTEGER PRIMARY KEY,
                content TEXT DEFAULT '',
                preview TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
            )
        ''')
    print("数据库初始化完成")

def add_file(filename, filepath, file_type, file_size, category='其他'):
    """
    添加文件记录

    参数：
        filename: 文件名
        filepath: 文件路径
        file_type: 文件类型
        file_size: 文件大小（字节）
        category: 文档分类（默认'其他'）

    返回：
        新插入记录的ID
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filename, filepath, file_type, file_size, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, filepath, file_type, file_size, category))
        return cursor.lastrowid

def update_file_category(file_id, category):
    """
    更新文件分类

    参数：
        file_id: 文件ID
        category: 新分类

    返回：
        是否更新成功
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE files SET category = ? WHERE id = ?', (category, file_id))
        return cursor.rowcount > 0


def save_file_content(file_id, content, preview=''):
    """保存或更新文件提取后的文本内容。"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO file_contents (file_id, content, preview, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_id) DO UPDATE SET
                content = excluded.content,
                preview = excluded.preview,
                updated_at = CURRENT_TIMESTAMP
        ''', (file_id, content, preview))


def get_all_file_contents():
    """获取所有文件的内容缓存。"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.id, f.filename, f.category, f.created_at, fc.content, fc.preview
            FROM files f
            LEFT JOIN file_contents fc ON f.id = fc.file_id
            ORDER BY f.created_at DESC
        ''')
        return cursor.fetchall()

def get_all_files():
    """
    获取所有文件列表
    
    返回：
        文件记录列表，按时间倒序
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files ORDER BY created_at DESC')
        return cursor.fetchall()

def get_file_by_id(file_id):
    """
    根据ID获取文件信息
    
    参数：
        file_id: 文件ID
    
    返回：
        文件记录，不存在返回None
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
        return cursor.fetchone()

def delete_file(file_id):
    """
    删除文件记录
    
    参数：
        file_id: 文件ID
    
    返回：
        是否删除成功
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM file_contents WHERE file_id = ?', (file_id,))
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        return cursor.rowcount > 0

def add_chat(question, answer, sources=None):
    """
    添加对话记录
    
    参数：
        question: 用户问题
        answer: AI回答
        sources: 参考来源（可选）
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chats (question, answer, sources)
            VALUES (?, ?, ?)
        ''', (question, answer, sources))

def get_chat_history(limit=50):
    """
    获取对话历史
    
    参数：
        limit: 返回记录数量上限
    
    返回：
        对话记录列表，按时间倒序
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM chats ORDER BY created_at DESC, id DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

def clear_chat_history():
    """清空对话历史"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chats')

# 测试代码
if __name__ == "__main__":
    init_db()
    print("数据库测试完成")
