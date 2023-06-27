# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from src.actions import workspace as WorkspaceActions
from src.exceptions.resource import APIException
from src.models.documents import Workspace, ResourceID
from src.schemas import workspace as WorkspaceSchemas
from src.schemas import policy as PolicySchemas
from src.schemas import group as GroupSchemas
from src.schemas import member as MemberSchemas
from src import dependencies as Dependencies
from src.utils import permissions as Permissions
from src.account_manager import current_active_user

# APIRouter creates path operations for user module
open_router = APIRouter()
router = APIRouter(dependencies=[Depends(Dependencies.check_workspace_permission)])


# TODO: Move to open router to a separate file
# Get all workspaces with user as a member or owner
@open_router.get("",
                 response_description="List of all workspaces",
                 response_model=WorkspaceSchemas.WorkspaceList)
async def get_workspaces():
    """
    Returns all workspaces where the current user is a member.
    The request does not accept any query parameters.
    """
    try:
        return await WorkspaceActions.get_workspaces()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Create a new workspace for current user
@open_router.post("",
                  response_description="Created workspaces",
                  status_code=201,
                  response_model=WorkspaceSchemas.WorkspaceCreateOutput)
async def create_workspace(input_data: WorkspaceSchemas.WorkspaceCreateInput = Body(...)):
    """
    Creates a new workspace for the current user.
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the created workspace information.
    """
    try:
        return await WorkspaceActions.create_workspace(input_data=input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


Workspace_resources = list[Literal["policies", "groups", "members", "all"]]


# Get a workspace with the given id
@router.get("/{workspace_id}",
            response_description="Workspace data",
            response_model=WorkspaceSchemas.Workspace,
            response_model_exclude_defaults=True
            )
async def get_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                        include: Annotated[Workspace_resources | None, Query()] = None
                        ) -> WorkspaceSchemas.Workspace:
    """
    Endpoint to get a workspace with the given id.
    By default, it returns the basic information of the workspace such as id, name, and description.
    The user can specify other resources to include in the response using the query parameters.
    For example, to include groups and members in the response, the user can send the following GET request:
    > `/workspaces/6497fdbafe12e8ff9017f253?include=groups&include=members`

    Path parameters:
    - **workspace_id** (str): id of the workspace

    Query parameters:
    - **groups** (bool): include groups in the response
    - **members** (bool): include members in the response
    - **policies** (bool): include policies in the response
    - **all** (bool): include all resources in the response

    Returns a workspace with the given id.
    """
    try:
        # await workspace.fetch_all_links()
        account = current_active_user.get()
        groups = None
        members = None
        policies = None

        if include:
            # Get the permissions(allowed actions) of the current user
            permissions = await Permissions.get_all_permissions(workspace, account)
            # If "all" is in the list, include all resources
            if "all" in include:
                include = ["policies", "groups", "members"]
            # Fetch the resources if the user has the required permissions
            if "groups" in include:
                req_permissions = Permissions.WorkspacePermissions["get_groups"]  # type: ignore
                if Permissions.check_permission(permissions, req_permissions):
                    groups = (await WorkspaceActions.get_groups(workspace)).groups
            if "members" in include:
                req_permissions = Permissions.WorkspacePermissions["get_workspace_members"]  # type: ignore
                if Permissions.check_permission(permissions, req_permissions):
                    members = (await WorkspaceActions.get_workspace_members(workspace)).members
            if "policies" in include:
                req_permissions = Permissions.WorkspacePermissions["get_workspace_policies"]  # type: ignore
                if Permissions.check_permission(permissions, req_permissions):
                    policies = (await WorkspaceActions.get_workspace_policies(workspace)).policies
        # Return the workspace with the fetched resources
        return WorkspaceSchemas.Workspace(id=workspace.id,
                                          name=workspace.name,
                                          description=workspace.description,
                                          groups=groups,
                                          members=members,
                                          policies=policies)

    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update a workspace with the given id
@router.patch("/{workspace_id}", response_description="Updated workspace")
async def update_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                           input_data: WorkspaceSchemas.WorkspaceCreateInput = Body(...)):
    """
    Updates the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the updated workspace.
    """
    try:
        return await WorkspaceActions.update_workspace(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a workspace with the given id
@router.delete("/{workspace_id}",
               response_description="Deleted workspace",
               status_code=204)
async def delete_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    """
    Deletes the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to delete

    Returns status code 204 if the workspace is deleted successfully.
    Response has no detail.
    """
    try:
        await WorkspaceActions.delete_workspace(workspace)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.get("/{workspace_id}/groups",
            response_description="List of all groups",
            response_model=GroupSchemas.GroupList)
async def get_groups(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    try:
        return await WorkspaceActions.get_groups(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.post("/{workspace_id}/groups",
             status_code=201,
             response_description="Created Group",
             response_model=GroupSchemas.GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                       input_data: GroupSchemas.GroupCreateInput = Body(...)):
    try:
        return await WorkspaceActions.create_group(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all members in the workspace
@router.get("/{workspace_id}/members",
            response_description="List of all groups",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
async def get_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    try:
        return await WorkspaceActions.get_workspace_members(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add members to the workspace
@router.post("/{workspace_id}/members",
             response_description="List added members",
             response_model=MemberSchemas.MemberList)
async def add_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                                member_data: MemberSchemas.AddMembers = Body(...)):
    try:
        return await WorkspaceActions.add_workspace_members(workspace, member_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove member from the workspace
@router.delete("/{workspace_id}/members/{account_id}",
               response_description="Updated list removed members",
               response_model_exclude_unset=True)
async def remove_workspace_member(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                                  account_id: ResourceID = Path(..., description="Account ID of the member to remove")):
    try:
        return await WorkspaceActions.remove_workspace_member(workspace, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace
@router.get("/{workspace_id}/policies",
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList)
async def get_workspace_policies(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    try:
        return await WorkspaceActions.get_workspace_policies(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List member's permissions in the workspace
@router.get("/{workspace_id}/policy",
            response_description="List member policy(permissions)",
            response_model=PolicySchemas.PolicyOutput)
async def get_workspace_policy(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                               account_id: ResourceID | None = None):
    try:
        return await WorkspaceActions.get_workspace_policy(workspace, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a member in a workspace
@router.put("/{workspace_id}/policy",
            response_description="Updated permissions",
            response_model=PolicySchemas.PolicyOutput)
async def set_workspace_policy(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                               permissions: PolicySchemas.PolicyInput = Body(...)):
    """
    Sets the permissions for a user in a workspace.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **user_id** (str): id of the user to update
    - **permissions** (int): new permissions for the user

    Returns the updated workspace.
    """
    try:
        return await WorkspaceActions.set_workspace_policy(workspace, permissions)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))