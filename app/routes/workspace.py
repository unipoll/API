# FastAPI
from fastapi import APIRouter, Body, Depends
from app.actions import workspace as WorkspaceActions
from app.actions import group as GroupActions
from app.models.workspace import Workspace
from app.schemas.workspace import (WorkspaceID, WorkspaceList, MemberAdd, WorkspaceReadFull, WorkspaceReadShort,
                                   WorkspaceCreateInput, WorkspaceCreateOutput)
from app.models.user import User
# from app.schemas.user import UserID
from app.schemas.group import GroupList, GroupCreateInput, GroupCreateOutput
from app.exceptions import workspace as WorkspaceExceptions


# APIRouter creates path operations for user module
router = APIRouter()


# Dependency for getting a workspace with the given id
async def get_workspace(workspace_id: WorkspaceID) -> Workspace:
    """
    Returns a workspace with the given id.
    """
    workspace = await Workspace.get(workspace_id)
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspace_id)
    return workspace


# Get all workspaces with user as a member or owner
@router.get("", response_description="List of all workspaces", response_model=WorkspaceList)
async def get_workspaces() -> WorkspaceList:
    """
    Returns all workspaces, the current user is a member of. The request does not accept any query parameters.
    """
    return await WorkspaceActions.get_user_workspaces()


# Create a new workspace for current user
@router.post("", response_description="Created workspaces", response_model=WorkspaceCreateOutput)
async def create_workspace(input_data: WorkspaceCreateInput = Body(...)) -> WorkspaceCreateOutput:
    """
    Creates a new workspace for the current user.
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the created workspace with the current user as the owner.
    """
    return await WorkspaceActions.create_workspace(input_data=input_data)


# Get a workspace with the given id
@router.get("/{workspace_id}", response_description="Workspace data", response_model=WorkspaceReadFull)
async def get_workspace_info(workspace: Workspace = Depends(get_workspace)) -> WorkspaceReadFull:
    """
    Returns a workspace with the given id.
    """
    return await WorkspaceActions.get_workspace(workspace)


# Update a workspace with the given id
@router.put("/{workspace_id}", response_description="Updated workspace", response_model=WorkspaceReadShort)
async def update_workspace(workspace: Workspace = Depends(get_workspace),
                           input_data: WorkspaceCreateInput = Body(...)) -> WorkspaceReadShort:
    """
    Updates the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the updated workspace.
    """
    return await WorkspaceActions.update_workspace(workspace, input_data)


# Delete a workspace with the given id
@router.delete("/{workspace_id}", response_description="Deleted workspace")
async def delete_workspace(workspace: Workspace = Depends(get_workspace)):
    """
    Deletes the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to delete
    """
    return await WorkspaceActions.delete_workspace(workspace)


# Set permissions for a user in a workspace
@router.put("/{workspace_id}/permissions", response_description="Updated permissions")
async def set_permissions(workspace: Workspace = Depends(get_workspace), permissions: int = Body(...)):
    """
    Sets the permissions for a user in a workspace.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **user_id** (str): id of the user to update
    - **permissions** (int): new permissions for the user

    Returns the updated workspace.
    """
    # return await WorkspaceActions.set_permissions(workspace, permissions)
    return 200


# List all groups in the workspace
@router.get("/{workspace_id}/groups", response_description="List of all groups", response_model=GroupList)
async def list_groups(workspace: Workspace = Depends(get_workspace)) -> GroupList:
    return await GroupActions.get_user_groups(workspace)


# List all groups in the workspace
@router.post("/{workspace_id}/groups", response_description="Created Group", response_model=GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(get_workspace),
                       input_data: GroupCreateInput = Body(...)) -> GroupCreateOutput:
    return await GroupActions.create_group(workspace, input_data)


# List all members in the workspace
@router.get("/{workspace_id}/members", response_description="List of all groups", response_model=dict)
async def list_members(workspace: Workspace = Depends(get_workspace)) -> dict:
    return await WorkspaceActions.get_members(workspace)


# List all members in the workspace
@router.post("/{workspace_id}/members", response_description="List of all groups", response_model=User)
async def add_member(member_data: MemberAdd,
                     workspace: Workspace = Depends(get_workspace)):
    return await WorkspaceActions.add_member(workspace, member_data.user_id)