import os
import shutil
from datetime import datetime
from typing import List

import requests
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse
from requests.exceptions import ConnectionError
from sqlmodel import Session, select

from database import get_session, get_media_from_database
from models.media import Media, MediaRead, MediaReadDetails


router = APIRouter(prefix="/media")


@router.get(
    "/",
    response_model=List[MediaRead],
)
async def get_all_media(session: Session = Depends(get_session)):
    return session.exec(select(Media)).all()


@router.get(
    "/{barcode}",
    response_model=MediaReadDetails,
)
async def get_media(
    media: Media = Depends(get_media_from_database)
):
    return media
