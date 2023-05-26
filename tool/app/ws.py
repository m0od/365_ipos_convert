import asyncio
import json
from typing import Optional
from urllib.request import Request

import aioredis
from fastapi import APIRouter, Query, Form
from fastapi.websockets import WebSocket, WebSocketDisconnect

router = APIRouter()
@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, tid):
    await websocket.accept()
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f"Message text was: {data}")
    await redis_connector(websocket, tid)

async def redis_connector(
    websocket: WebSocket, tid, redis_uri: str = "redis://127.0.0.1:6380"
):
    async def consumer_handler(ws: WebSocket, r):
        try:
            while True:
                message = await ws.receive_text()
                if message:
                    await r.publish(tid, message)

        except WebSocketDisconnect as exc:
            # TODO this needs handling better
            print(exc)

    async def producer_handler(r, ws: WebSocket):
        (channel,) = await r.subscribe(tid)
        assert isinstance(channel, aioredis.Channel)
        try:
            while True:
                message = await channel.get()
                if message:
                    print(message)
                    await ws.send_text(message.decode("utf-8"))
        except Exception as exc:
            # TODO this needs handling better
            print(exc)

    redis = await aioredis.create_redis_pool(redis_uri)

    consumer_task = consumer_handler(websocket, redis)
    producer_task = producer_handler(redis, websocket)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    print(f"Done task: {done}")
    for task in pending:
        print(f"Canceling task: {task}")
        task.cancel()
    redis.close()
    await redis.wait_closed()
