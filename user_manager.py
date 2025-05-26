"""
用戶管理模組 - 處理用戶資訊與權限
"""
import os
import json
import sqlite3
from typing import Dict, List, Optional, Any

# 資料庫路徑
DB_PATH = os.getenv("DB_PATH", "./users.db")

class UserManager:
    """
    用戶管理類 - 處理用戶資訊與權限
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """
        初始化資料庫
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 創建用戶表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: str, display_name: str, is_admin: bool = False) -> bool:
        """
        添加新用戶
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO users (user_id, display_name, is_admin) VALUES (?, ?, ?)",
                (user_id, display_name, 1 if is_admin else 0)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加用戶失敗: {e}")
            return False
    
    def set_admin(self, user_id: str, is_admin: bool) -> bool:
        """
        設置用戶管理員權限
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET is_admin = ? WHERE user_id = ?",
                (1 if is_admin else 0, user_id)
            )
            
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"設置管理員權限失敗: {e}")
            return False
    
    def is_admin(self, user_id: str) -> bool:
        """
        檢查用戶是否為管理員
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT is_admin FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None and result[0] == 1
        except Exception as e:
            print(f"檢查管理員權限失敗: {e}")
            return False
    
    def user_exists(self, user_id: str) -> bool:
        """
        檢查用戶是否存在
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT 1 FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            print(f"檢查用戶存在失敗: {e}")
            return False
    
    def get_user_name(self, user_id: str) -> Optional[str]:
        """
        獲取用戶顯示名稱
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT display_name FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"獲取用戶名稱失敗: {e}")
            return None
    
    def get_user_id_by_name(self, display_name: str) -> Optional[str]:
        """
        通過顯示名稱獲取用戶 ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT user_id FROM users WHERE display_name = ?",
                (display_name,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"通過名稱獲取用戶 ID 失敗: {e}")
            return None
    
    def get_all_admins(self) -> List[Dict[str, Any]]:
        """
        獲取所有管理員
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT user_id, display_name FROM users WHERE is_admin = 1"
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return [{"user_id": row[0], "display_name": row[1]} for row in results]
        except Exception as e:
            print(f"獲取所有管理員失敗: {e}")
            return []

# 便捷函數，用於檢查用戶是否為管理員
def is_admin(user_id: str) -> bool:
    """
    檢查用戶是否為管理員
    """
    user_manager = UserManager()
    return user_manager.is_admin(user_id)
