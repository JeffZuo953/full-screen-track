def check_all_files(self, callback=None):
    """在工作线程中检查所有文件"""
    def worker():
        try:
            files = self.get_files_paginated(1, self.get_total_count())
            for file in files:
                exists = os.path.exists(file.local_path)
                self.file_dao.update_existence(file.local_path, exists)
                if callback:
                    callback(file.local_path, exists)
        except Exception as e:
            logger.error(f"Check files error: {e}")
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()

def delete_old_files(self, days: int, progress_callback=None):
    """删除旧文件时提供进度反馈"""
    def worker():
        files = self.get_old_files(days)
        total = len(files)
        for i, file in enumerate(files):
            if progress_callback:
                progress_callback(i / total * 100)
            # ... 删除操作 ...
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
