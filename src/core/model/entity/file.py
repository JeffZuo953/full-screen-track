from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

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
    def from_dict(cls, data: Dict[str, str | int | datetime | bool]) -> File:
        """
        Create a File instance from a dictionary.

        Args:
            data: A dictionary containing file data.

        Returns:
            A File instance.
        """
        return cls(
            id=data.get("id"),
            local_path=str(data["local_path"]),
            remote_path=str(data["remote_path"]),
            file_size=int(data["file_size"]),
            last_modified=data["last_modified"],  # type: ignore
            status=str(data.get("status", "pending")),
            upload_time=data.get("upload_time"),  # type: ignore
            last_check=data.get("last_check", datetime.now()),  # type: ignore
            exists_locally=bool(data.get("exists_locally", True)),
        )

    def to_dict(self) -> Dict[str, Optional[int] | str | int | datetime | bool]:
        """
        Convert the File instance to a dictionary.

        Returns:
            A dictionary representation of the File instance.
        """
        return {
            "id": self.id,
            "local_path": self.local_path,
            "remote_path": self.remote_path,
            "file_size": self.file_size,
            "last_modified": self.last_modified,
            "status": self.status,
            "upload_time": self.upload_time,
            "last_check": self.last_check,
            "exists_locally": self.exists_locally,
        }
