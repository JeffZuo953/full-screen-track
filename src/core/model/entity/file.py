from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class File:
    """File entity representing a record in the database"""
    id: Optional[int]
    local_path: str
    remote_path: str
    file_size: int
    last_modified: datetime
    status: str
    upload_time: Optional[datetime]
    last_check: datetime
    exists_locally: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> 'File':
        """Create a File instance from a dictionary"""
        return cls(
            id=data.get('id'),
            local_path=data['local_path'],
            remote_path=data['remote_path'],
            file_size=data['file_size'],
            last_modified=data['last_modified'],
            status=data.get('status', 'pending'),
            upload_time=data.get('upload_time'),
            last_check=data.get('last_check', datetime.now()),
            exists_locally=data.get('exists_locally', True)
        )

    def to_dict(self) -> dict:
        """Convert File instance to dictionary"""
        return {
            'id': self.id,
            'local_path': self.local_path,
            'remote_path': self.remote_path,
            'file_size': self.file_size,
            'last_modified': self.last_modified,
            'status': self.status,
            'upload_time': self.upload_time,
            'last_check': self.last_check,
            'exists_locally': self.exists_locally
        }
