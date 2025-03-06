import asyncio
import sys

# import celery
# from fastapi import APIRouter, BackgroundTasks
# from common.messaging import celery
#
# @celery.task
# def add(x, y):
#     return x + y
#
# router = APIRouter(prefix='/bg-task-test')
#
# async def perform_task(task_id: int):
#     await asyncio.sleep(3)
#     print(f'{task_id} done!')
#
# @router.post('/{task_id}')
# def create_task(task_id: int, background_tasks: BackgroundTasks):
#     background_tasks.add_task(perform_task, task_id=task_id)
#     return {'message': 'Task created'}
#

import pickle
import binascii

if __name__ == '__main__':
    serialized_result = binascii.unhexlify('80054B032E')
    result = pickle.loads(serialized_result)
    print(result)