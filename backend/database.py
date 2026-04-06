"""
数据库操作模块
使用SQLite数据库
"""

import sqlite3
from datetime import datetime

DB_PATH = 'zhixue.db'

def init_db():
    """
    初始化数据库
    创建必要的表结构
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建文件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建对话记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def add_file(filename, filepath, file_type, file_size):
    """
    添加文件记录
    
    参数：
        filename: 文件名
        filepath: 文件路径
        file_type: 文件类型
        file_size: 文件大小（字节）
    
    返回：
        新插入记录的ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (filename, filepath, file_type, file_size)
        VALUES (?, ?, ?, ?)
    ''', (filename, filepath, file_type, file_size))
    conn.commit()
    file_id = cursor.lastrowid
    conn.close()
    return file_id

def get_all_files():
    """
    获取所有文件列表
    
    返回：
        文件记录列表，按时间倒序
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files ORDER BY created_at DESC')
    files = cursor.fetchall()
    conn.close()
    return files

def get_file_by_id(file_id):
    """
    根据ID获取文件信息
    
    参数：
        file_id: 文件ID
    
    返回：
        文件记录，不存在返回None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file = cursor.fetchone()
    conn.close()
    return file

def delete_file(file_id):
    """
    删除文件记录
    
    参数：
        file_id: 文件ID
    
    返回：
        是否删除成功
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def add_chat(question, answer, sources=None):
    """
    添加对话记录
    
    参数：
        question: 用户问题
        answer: AI回答
        sources: 参考来源（可选）
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chats (question, answer, sources)
        VALUES (?, ?, ?)
    ''', (question, answer, sources))
    conn.commit()
    conn.close()

def get_chat_history(limit=50):
    """
    获取对话历史
    
    参数：
        limit: 返回记录数量上限
    
    返回：
        对话记录列表，按时间倒序
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM chats ORDER BY created_at DESC LIMIT ?',
        (limit,)
    )
    chats = cursor.fetchall()
    conn.close()
    return chats

def clear_chat_history():
    """清空对话历史"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chats')
    conn.commit()
    conn.close()

# 测试代码
if __name__ == "__main__":
    init_db()
    print("数据库测试完成")
