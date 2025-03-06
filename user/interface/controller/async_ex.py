import asyncio
from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix='/bg-task-test')

async def perform_task(task_id: int):
    await asyncio.sleep(3)
    print(f'{task_id} done!')

@router.post('/{task_id}')
def create_task(task_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(perform_task, task_id=task_id)
    return {'message': 'Task created'}