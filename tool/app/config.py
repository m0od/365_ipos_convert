import os

from pydantic import BaseSettings

# from pydantic import BaseSettings
#
#
# class BaseConfig:
#     DATABASE_URL = 'mysql://root:7y!FY^netG!jn>f+@localhost/ipos365?charset=utf8mb3'
#
#
# class DevelopmentConfig(BaseConfig):
#     pass
#
#
# class ProductionConfig(BaseConfig):
#     pass
#
#
# class TestingConfig(BaseConfig):
#     pass
with open('../.secret_key', 'a+b') as secret:
    secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
    KEY = secret.read()
    if not KEY:
        KEY = os.urandom(64)
        secret.write(KEY)
        secret.flush()
# print(SECRET)

#
#
#
#
# settings = get_settings()

class Settings(object):
    DATABASE_URL = 'mysql://root:7y!FY^netG!jn>f+@localhost/ipos365?charset=utf8mb3'
    SECRET_KEY = KEY
    GOOGLE_CLIENT_ID = '263581281598-tkh7tha61k78kb55c670sjfu6651m3a1.apps.googleusercontent.com'
    CELERY_CONFIG = {'broker_url': 'redis://localhost:6380', 'result_backend': 'redis://localhost:6380'}
    CELERY_NAME = 'KT365'


settings = Settings()
# @lru_cache()
# # def get_settings():
# #     config_cls_dict = {
# #         "development": DevelopmentConfig,
# #         "production": ProductionConfig,
# #         "testing": TestingConfig
# #     }
# #
# #     config_name = os.environ.get("FASTAPI_CONFIG", "development")
# #     print(config_name)
# #     config_cls = config_cls_dict[config_name]
# #     return config_cls()
