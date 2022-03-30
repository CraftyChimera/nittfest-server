"""
parser route
"""
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from starlette.responses import FileResponse

from config.logger import logger
from config.settings import settings
from scripts.parser.parser import (
    generate_forms_responses,
    generate_preferences,
)
from server.controllers.auth import (
    JWTBearer,
    decode_jwt,
    sign_jwt_auth,
)
from server.models.admin import (
    AdminResponseModel,
    DownloadFormResponsesRequestModel,
    LoginRequestModel,
)
from server.models.errors import GenericError

router = APIRouter(
    prefix="/admin",
)


@router.post(
    "/downloadpreferences",
    dependencies=[Depends(JWTBearer())],
)
async def download_preferences(
    token: str = Depends(JWTBearer()),
) -> FileResponse:
    """
    Admin download preferences
    """
    try:
        roll = decode_jwt(token)["roll_number"]
        password = decode_jwt(token)["password"]
        is_admin = bool(
            roll == settings.admin_roll
            and password == settings.admin_password
        )
        if not is_admin:
            raise GenericError("Not Admin")
        filepath = await generate_preferences()
        return FileResponse(filepath)
    except GenericError as exception:
        logger.error(f"{roll}@nitt.edu attempted to download responses")
        raise HTTPException(
            status_code=400,
            detail=f"{exception}",
        ) from exception


@router.post(
    "/downloadresponses",
    dependencies=[Depends(JWTBearer())],
)
async def download_responses(
    request_responses: DownloadFormResponsesRequestModel,
    token: str = Depends(JWTBearer()),
) -> FileResponse:
    """
    Admin download form responses
    """
    try:
        roll = decode_jwt(token)["roll_number"]
        password = decode_jwt(token)["password"]
        is_admin = bool(
            roll == settings.admin_roll
            and password == settings.admin_password
        )
        if not is_admin:
            raise GenericError("Not Admin")
        filepath = await generate_forms_responses(
            request_responses.domain, request_responses.year
        )
        return FileResponse(filepath)
    except GenericError as exception:
        logger.error(f"{roll} attempted to download responses")
        raise HTTPException(
            status_code=400,
            detail=f"{exception}",
        ) from exception


@router.post("/")
def event_jwt(response: LoginRequestModel):
    """
    Admin login for events
    """
    if (
        response.roll_number == settings.admin_roll
        and response.password == settings.admin_password
    ):
        jwt_res = sign_jwt_auth(
            roll=response.roll_number, password=response.password
        )
        print(jwt_res)
        return AdminResponseModel(
            isAuthorized=True, jwt_token=jwt_res["jwt_token"]
        )
    return AdminResponseModel(isAuthorized=False, jwt_token="")
