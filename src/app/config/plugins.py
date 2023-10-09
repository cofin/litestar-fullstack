from advanced_alchemy.extensions.litestar.plugins import SQLAlchemyPlugin
from litestar.contrib.pydantic import PydanticPlugin
from litestar_aiosql import AiosqlConfig, AiosqlPlugin
from litestar_saq import CronJob, QueueConfig, SAQConfig, SAQPlugin
from litestar_vite import ViteConfig, VitePlugin

from app import config
from app.config._settings import TEMPLATES_DIR, settings
from app.domain.system import tasks

sqlalchemy = SQLAlchemyPlugin(config=config.sqlalchemy)
pydantic = PydanticPlugin(prefer_alias=True)
aiosql = AiosqlPlugin(config=AiosqlConfig())
vite = VitePlugin(
    config=ViteConfig(
        static_dir=settings.APP_STATIC_DIR,
        templates_dir=TEMPLATES_DIR,
        hot_reload=settings.APP_DEV_MODE,
        port=3005,
    ),
)
saq = SAQPlugin(
    config=SAQConfig(
        redis_url=settings.REDIS_URL,
        web_enabled=True,
        worker_processes=1,
        queue_configs=[
            QueueConfig(
                name="system-tasks",
                tasks=[tasks.system_task, tasks.system_upkeep],
                scheduled_tasks=[CronJob(function=tasks.system_upkeep, unique=True, cron="0 * * * *", timeout=500)],
            ),
            QueueConfig(
                name="background-tasks",
                tasks=[tasks.background_worker_task],
                scheduled_tasks=[
                    CronJob(function=tasks.background_worker_task, unique=True, cron="* * * * *", timeout=300),
                ],
            ),
        ],
    ),
)
