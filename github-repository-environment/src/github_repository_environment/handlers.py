import logging
import json
import urllib3

from typing import Any, MutableMapping, Optional
from dataclasses import dataclass
from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
)


from .models import ResourceHandlerRequest, ResourceModel


# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "GitHub::Repository::Environment"
GITHUB_BASE = "https://api.github.com"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint

http = urllib3.PoolManager()

def read(model: ResourceModel) -> ProgressEvent:
    access_token = model.AccessToken
    owner = model.Owner
    repo = model.Repository
    environment_name = model.EnvironmentName

    try:
        response = http.request(
            "GET",
            f"{GITHUB_BASE}/repos/{owner}/{repo}/environments/{environment_name}", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        model.Id = data.get("id")
        model.Url = data.get("url")
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModel=model
        )

    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.NotFound
    ) 

def list_(model: ResourceModel) -> ProgressEvent:
    access_token = model.AccessToken
    owner = model.Owner
    repo = model.Repository

    try:
        response = http.request(
            "GET",
            f"{GITHUB_BASE}/repos/{owner}/{repo}/environments", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        environments = data.get("environments", [])
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModels=[
                ResourceModel(
                    Id=environment.get("id"),
                    AccessToken=model.AccessToken,
                    Owner=model.Owner,
                    Repository=model.Repository,
                    EnvironmentName=environment.get("name"),
                    WaitTimer=None,
                    Reviewers=None,
                    Url=data.get("url")
                ) 
            for environment in environments]
        )

    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.NotFound
    )

def create_update(model: ResourceModel) -> ProgressEvent:
    access_token = model.AccessToken
    owner = model.Owner
    repo = model.Repository
    environment_name = model.EnvironmentName

    try:
        response = http.request(
            "PUT",
            f"{GITHUB_BASE}/repos/{owner}/{repo}/environments/{environment_name}", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    if response.status == 422:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InvalidRequest,
            message=response.data,
            resourceModel=model,
        )   
      
    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        model.Id = data.get("id")
        model.Url = data.get("url")
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModel=model
        )   

    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.InternalFailure,
        message=response.data,
        resourceModel=model,
    ) 

def delete(model: ResourceModel) -> ProgressEvent:
    access_token = model.AccessToken
    owner = model.Owner
    repo = model.Repository
    environment_name = model.EnvironmentName

    try:
        response = http.request(
            "DELETE",
            f"{GITHUB_BASE}/repos/{owner}/{repo}/environments/{environment_name}", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    if response.status == 204:
        return ProgressEvent(status=OperationStatus.SUCCESS)   

    
    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.NotFound,
    ) 

@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    read_progress_event: ProgressEvent = read(model)
    if read_progress_event.status == OperationStatus.SUCCESS:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.AlreadyExists
        )
    
    return create_update(model)

@resource.handler(Action.UPDATE)
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    read_progress_event: ProgressEvent = read(model)
    if read_progress_event.status != OperationStatus.SUCCESS:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="Not Found."
        )

    if read_progress_event.resourceModel.Id != model.Id:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="Id did not match."
        )    
    
    return create_update(model)


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    return delete(model)


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    return read(model)

    
@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    return list_(model)
