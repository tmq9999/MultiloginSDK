"""Workspace and folder wire fields."""

from pydantic import Field

from .common import RequestModel, ResponseModel


class Workspace(ResponseModel):
    workspace_id: str
    name: str
    role: str


class WorkspacesData(ResponseModel):
    workspaces: list[Workspace]
    total_count: int


class Folder(ResponseModel):
    folder_id: str
    name: str
    comment: str = ""
    profiles_count: int = 0


class FoldersData(ResponseModel):
    folders: list[Folder]


class FolderCreateRequest(RequestModel):
    name: str = Field(min_length=1)
    comment: str = ""


class FolderUpdateRequest(RequestModel):
    folder_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    comment: str = ""


class FoldersRemoveRequest(RequestModel):
    ids: list[str] = Field(min_length=1)
