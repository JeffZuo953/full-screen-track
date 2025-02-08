def batch_update_existence(self, updates: List[Tuple[bool, str, datetime]]) -> None:
    """批量更新文件状态，减少数据库操作次数"""
    with sqlite3.connect(self.db_path) as conn:
        # 使用临时表和批量更新
        conn.executemany(
            "UPDATE files SET exists_locally = ?, last_check = ? WHERE local_path = ?",
            updates
        )
