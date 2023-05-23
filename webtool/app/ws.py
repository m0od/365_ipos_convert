import asyncio
from typing import Optional
from urllib.request import Request

import aioredis
from fastapi import APIRouter, Query, Form
from fastapi.websockets import WebSocket, WebSocketDisconnect

router = APIRouter()
@router.websocket("")
async def ws_serve(websocket: WebSocket, task: Optional[str] = Query(None)):
    print(task)
    await websocket.accept()
    await redis_connector(websocket, task)

async def redis_connector(
    websocket: WebSocket, chanel, redis_uri: str = "redis://127.0.0.1:6379"
):
    print(chanel)
    async def consumer_handler(ws: WebSocket, r):
        try:
            while True:
                message = await ws.receive_text()
                if message:
                    await r.publish(chanel, message)
        except WebSocketDisconnect:
            pass

    async def producer_handler(r, ws: WebSocket):
        (channel,) = await r.subscribe(chanel)
        assert isinstance(channel, aioredis.Channel)
        try:
            while True:
                message = await channel.get()
                if message:
                    print(message)
                    await ws.send_text(message.decode("utf-8"))
        except Exception as exc:
            # TODO this needs handling better
            print('producer_handler: Err', exc)

    redis = await aioredis.create_redis_pool(redis_uri)

    consumer_task = consumer_handler(websocket, redis)
    producer_task = producer_handler(redis, websocket)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    redis.close()
    await redis.wait_closed()
