from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AnyUrl
from starlette.responses import RedirectResponse

from config.config_redis import cache
from dependencies import get_login
from schemas import Link
from utils import create_random_key

shorter_router = APIRouter()


@shorter_router.post("/squeeze", response_model=Link)
async def squeeze(link: AnyUrl, login=Depends(get_login)):
    random_key = create_random_key()
    while cache.get(f'link:{random_key}:value') is not None:
        random_key = create_random_key()
    link_id = cache.incr(f'link:global_id', 1)
    cache.set(f'link:{random_key}:id', link_id)
    cache.set(f'link:{random_key}:value', link)
    cache.set(f'link:{random_key}:counter', 0)
    cache.sadd(f'user:{login}:links', random_key)
    return Link(id=link_id, short=random_key, target=link, counter=0)


@shorter_router.get("/statistics", response_model=list[Link])
async def statistics(
        login=Depends(get_login),
        order: list[Literal["asc_short", "asc_target", "asc_counter",
                            "desc_short", "desc_target", "desc_counter"]]
        | None = Query([], description=''),
        offset: int = 0,
        limit: int = 0):
    shorts = cache.smembers(f'user:{login}:links')
    lines: list[Link] = [
        Link(
            **{
                'id': cache.get(f'link:{s.decode()}:id'),
                'short': s.decode(),
                'target': cache.get(f'link:{s.decode()}:value'),
                'counter': cache.get(f'link:{s.decode()}:counter')
            }) for s in shorts
    ]
    for single_order in order:
        ord, field = single_order.split('_')
        lines.sort(key=lambda x: x.__dict__[field], reverse=(ord == 'desc'))
    lines = lines[offset:]
    if limit:
        lines = lines[:limit]
    return lines


@shorter_router.get("/s/{key}", response_class=RedirectResponse)
async def redirect(key: str):
    target_url = cache.get(f'link:{key}:value')
    if target_url is None:
        raise HTTPException(status_code=404,
                            detail='not target for short path')
    cache.incr(f'link:{key}:counter', 1)
    return target_url
