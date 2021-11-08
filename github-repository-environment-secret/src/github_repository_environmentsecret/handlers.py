import logging
import json
import urllib3
import urllib.parse

from base64 import b64encode
from nacl import encoding, public

from typing import Any, MutableMapping, Optional, Tuple, Dict

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy
)

from .models import ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "GitHub::Repository::EnvironmentSecret"
GITHUB_BASE = "https://api.github.com"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint

http = urllib3.PoolManager()

def read_repository(model: ResourceModel) -> Tuple[ProgressEvent, Optional[Dict]]:
    access_token = model.AccessToken
    owner = urllib.parse.quote_plus(model.Owner)
    repo = urllib.parse.quote_plus(model.Repository)

    try:
        response = http.request(
            "GET",
            f"{GITHUB_BASE}/repos/{owner}/{repo}", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        LOG.exception(exc_info=e)
        failure = ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )
        return (failure, None)


    if response.status != 200:
        failure = ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="Repository not Found"
        )
        return (failure, None)

    success = ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model
    )
    return (success, response)

def read(model: ResourceModel) -> ProgressEvent:
    #
    # Step 1: Fetch repository ID
    #
    event, response = read_repository(model)
    if event.status != OperationStatus.SUCCESS:
        return event

    data = json.loads(response.data.decode("utf-8"))
    repository_id = data.get("id")

    access_token = model.AccessToken
    environment_name = urllib.parse.quote_plus(model.EnvironmentName)
    secret_name = urllib.parse.quote_plus(model.SecretName)

    #
    # Step 2: Read secret
    #
    try:
        response = http.request(
            "GET",
            f"{GITHUB_BASE}/repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}", 
            headers={ "Authorization": f"token {access_token}" },
        )
    except urllib3.exceptions.HTTPError as e:
        LOG.exception(exc_info=e)
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    if response.status == 200:
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModel=model
        )

    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.NotFound
    ) 

def list_(model: ResourceModel) -> ProgressEvent:
    #
    # Step 1: Fetch repository ID
    #
    event, response = read_repository(model)
    if event.status != OperationStatus.SUCCESS:
        return event

    data = json.loads(response.data.decode("utf-8"))
    repository_id = data.get("id")

    access_token = model.AccessToken
    environment_name = urllib.parse.quote_plus(model.EnvironmentName)

    #
    # Step 2: List Secrets
    #
    try:
        response = http.request(
            "GET",
            f"{GITHUB_BASE}/repositories/{repository_id}/environments/{environment_name}/secrets", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        LOG.exception(exc_info=e)
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        environments = data.get("secrets", [])
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModels=[
                ResourceModel(
                    AccessToken=model.AccessToken,
                    Owner=model.Owner,
                    Repository=model.Repository,
                    EnvironmentName=model.EnvironmentName,
                    SecretName=data.get("secret_name"),
                    SecretValue=None
                ) 
            for environment in environments]
        )

    return ProgressEvent(
        status=OperationStatus.FAILED,
        errorCode=HandlerErrorCode.NotFound
    )

def create_update(model: ResourceModel) -> ProgressEvent:
    #
    # Step 1: Fetch repository ID
    #
    event, response = read_repository(model)
    if event.status != OperationStatus.SUCCESS:
        return event

    data = json.loads(response.data.decode("utf-8"))
    repository_id = data.get("id")

    access_token = model.AccessToken
    environment_name = urllib.parse.quote_plus(model.EnvironmentName)
    secret_name = urllib.parse.quote_plus(model.SecretName)
    secret_value = model.SecretValue

    #
    # Step 2: Fetch Environment Public Key
    #
    try:
        response = http.request(
            "GET",
            f"{GITHUB_BASE}/repositories/{repository_id}/environments/{environment_name}/secrets/public-key", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        LOG.exception(exc_info=e)
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )  

    if response.status != 200:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="Public Key not Found"
        )

    data = json.loads(response.data.decode("utf-8"))
    key_id = data.get("key_id")
    public_key = data.get("key")

    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    encrypted_value = b64encode(encrypted).decode("utf-8")

    #
    # Step 3: Create / Update Secret
    #
    try:
        response = http.request(
            "PUT",
            f"{GITHUB_BASE}/repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}", 
            headers={ "Authorization": f"token {access_token}" },
            body=json.dumps({
                "encrypted_value": encrypted_value,
                "key_id": key_id
            })
        )
    except urllib3.exceptions.HTTPError as e:
        LOG.exception(exc_info=e)
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InternalFailure,
            message=e.message,
            resourceModel=model,
        )   

    del model.SecretValue

    if response.status == 422:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.InvalidRequest,
            message=response.data,
            resourceModel=model,
        )   
      
    if response.status == 201 or response.status == 204:
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
    #
    # Step 1: Fetch repository ID
    #
    event, response = read_repository(model)
    if event.status != OperationStatus.SUCCESS:
        return event

    data = json.loads(response.data.decode("utf-8"))
    repository_id = data.get("id")

    access_token = model.AccessToken
    environment_name = urllib.parse.quote_plus(model.EnvironmentName)
    secret_name = urllib.parse.quote_plus(model.SecretName)

    try:
        response = http.request(
            "DELETE",
            f"{GITHUB_BASE}/repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}", 
            headers={ "Authorization": f"token {access_token}" }
        )
    except urllib3.exceptions.HTTPError as e:
        LOG.exception(exc_info=e)
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
    previous_model = request.previousResourceState
    model = request.desiredResourceState

    if (
        model.Owner != previous_model.Owner and
        model.Repository != previous_model.Repository and
        model.EnvironmentName != previous_model.EnvironmentName
    ):
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="Create only value should not be changed"
        )

    read_progress_event: ProgressEvent = read(model)
    if read_progress_event.status != OperationStatus.SUCCESS:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="Not Found."
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