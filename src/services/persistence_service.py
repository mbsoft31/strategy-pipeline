"""Persistence service for saving and loading artifacts.

This module provides an abstraction for storing pipeline artifacts, allowing
different backends (files, databases, cloud storage) to be used interchangeably.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from ..models import ApprovalStatus  # Only need ApprovalStatus for enum serialization

T = TypeVar("T")


class PersistenceService(ABC):
    """Abstract interface for artifact persistence."""

    @abstractmethod
    def save_artifact(self, artifact: Any, project_id: str, artifact_type: str) -> None:
        pass

    @abstractmethod
    def load_artifact(self, artifact_type: str, project_id: str, artifact_class: Type[T]) -> Optional[T]:
        pass

    @abstractmethod
    def list_projects(self) -> List[str]:
        pass

    @abstractmethod
    def project_exists(self, project_id: str) -> bool:
        pass


class FilePersistenceService(PersistenceService):
    """File-based persistence implementation using JSON."""

    def __init__(self, base_dir: str = "./data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, project_id: str, create: bool = False) -> Path:
        project_dir = self.base_dir / project_id
        if create:
            project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def _get_artifact_path(self, project_id: str, artifact_type: str) -> Path:
        return self._get_project_dir(project_id, create=True) / f"{artifact_type}.json"

    def save_artifact(self, artifact: Any, project_id: str, artifact_type: str) -> None:
        artifact_path = self._get_artifact_path(project_id, artifact_type)
        artifact_dict = self._serialize_dataclass(artifact)
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_dict, f, indent=2, ensure_ascii=False)

    def load_artifact(self, artifact_type: str, project_id: str, artifact_class: Type[T]) -> Optional[T]:
        artifact_path = self._get_artifact_path(project_id, artifact_type)
        if not artifact_path.exists():
            return None
        with open(artifact_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data = self._deserialize_fields(data)
        try:
            return artifact_class(**data)
        except TypeError:
            return None

    def list_projects(self) -> List[str]:
        if not self.base_dir.exists():
            return []
        return [d.name for d in self.base_dir.iterdir() if d.is_dir()]

    def project_exists(self, project_id: str) -> bool:
        project_dir = self._get_project_dir(project_id, create=False)
        if not project_dir.exists():
            return False
        return any(project_dir.glob("*.json"))

    # ----------------------------
    # Serialization helpers
    # ----------------------------

    def _serialize_dataclass(self, obj: Any) -> Any:
        if is_dataclass(obj):
            raw = asdict(obj)
            return self._serialize_datetimes_and_enums(raw)
        if isinstance(obj, list):
            return [self._serialize_dataclass(o) for o in obj]
        if isinstance(obj, dict):
            return {k: self._serialize_dataclass(v) for k, v in obj.items()}
        return obj

    def _serialize_datetimes_and_enums(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: self._serialize_datetimes_and_enums(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._serialize_datetimes_and_enums(v) for v in obj]
        if hasattr(obj, "isoformat") and isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ApprovalStatus):
            return obj.value
        return obj

    def _deserialize_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        converted: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, str):
                # Try datetime parse
                try:
                    converted[k] = datetime.fromisoformat(v)
                    continue
                except ValueError:
                    pass
                # Try enum by value
                try:
                    converted[k] = ApprovalStatus(v)
                    continue
                except ValueError:
                    pass
            if isinstance(v, list):
                converted[k] = [self._deserialize_list_item(item) for item in v]
            else:
                converted[k] = v
        return converted

    def _deserialize_list_item(self, item: Any) -> Any:
        if isinstance(item, dict):
            return {k: self._deserialize_list_item(v) for k, v in item.items()}
        if isinstance(item, str):
            try:
                return datetime.fromisoformat(item)
            except ValueError:
                # Enum value attempt
                try:
                    return ApprovalStatus(item)
                except ValueError:
                    return item
        return item
