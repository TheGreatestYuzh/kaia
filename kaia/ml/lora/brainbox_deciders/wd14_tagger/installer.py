from pathlib import Path
from .settings import WD14TaggerSettings
from kaia.brainbox.deciders.arch import LocalImageInstaller, DockerService, BrainBoxServiceRunner
from kaia.brainbox.deployment import SmallImageBuilder
from unittest import TestCase
from kaia.brainbox.core import BrainBoxApi, BrainBoxTask, IntegrationTestResult, File, BrainBoxTaskPack
from .api import WD14Tagger
import json

class WD14TaggerInstaller(LocalImageInstaller):
    def __init__(self, settings: WD14TaggerSettings):
        self.settings = settings

        service = DockerService(
            self, self.settings.port, self.settings.startup_time_in_seconds,
            BrainBoxServiceRunner(
                publish_ports={self.settings.port: 8084},
                mount_resource_folders={'models': '/home/app/.cache/huggingface'}
            ),
        )

        super().__init__(
            'wd14_tagger',
            Path(__file__).parent / 'container',
            DOCKERFILE,
            DEPENDENCIES,
            service)

        self.notebook_service = service.as_notebook_service()

    def create_brainbox_decider_api(self, parameters: str) -> WD14Tagger:
        return WD14Tagger(f'{self.ip_address}:{self.settings.port}')

    def create_api(self) -> WD14Tagger:
        return WD14Tagger(f'{self.ip_address}:{self.settings.port}')

    def post_install(self):
        api = self.run_in_any_case_and_create_api()
        for model in self.settings.models_to_download:
            api.tags()

    def _brainbox_self_test_internal(self, api: BrainBoxApi, tc: TestCase):
        file = File.read(Path(__file__).parent/'image.png')
        yield IntegrationTestResult(0, "Image", file)
        for model in self.settings.models_to_download:
            yield IntegrationTestResult(1, f"Interrogation with model {model}")
            interrogation = api.execute(BrainBoxTask.call(WD14Tagger).interrogate(image=file, model=model).to_task())
            js = File("response.json", json.dumps(interrogation), File.Kind.Json)
            yield IntegrationTestResult(1, None, js)

            yield IntegrationTestResult(1, f"Tags of model {model}")
            tags = api.execute(BrainBoxTask.call(WD14Tagger).tags(model=model))
            js = File("tags.json", json.dumps(tags[:3]+['...']), File.Kind.Json)
            yield IntegrationTestResult(1, None, js)



DOCKERFILE = f'''
FROM python:3.11

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

{{{SmallImageBuilder.ADD_USER_PLACEHOLDER}}}

{{{SmallImageBuilder.PIP_INSTALL_PLACEHOLDER}}}

WORKDIR /home/app

RUN git clone https://github.com/corkborg/wd14-tagger-standalone

WORKDIR /home/app/wd14-tagger-standalone

RUN git reset --hard f1114c877ed6d1b1311f7e485ec0466d5064eb0c

COPY . /home/app/wd14-tagger-standalone

WORKDIR /home/app/wd14-tagger-standalone

RUN touch tagger/__init__.py

RUN pip install -e .



ENTRYPOINT ["python3","/home/app/wd14-tagger-standalone/main.py"]
'''

DEPENDENCIES = '''
anyio==4.6.2.post1
argon2-cffi==23.1.0
argon2-cffi-bindings==21.2.0
arrow==1.3.0
asttokens==2.4.1
async-lru==2.0.4
attrs==24.2.0
babel==2.16.0
beautifulsoup4==4.12.3
bleach==6.1.0
blinker==1.8.2
certifi==2024.8.30
cffi==1.17.1
charset-normalizer==3.4.0
click==8.1.7
coloredlogs==15.0.1
comm==0.2.2
debugpy==1.8.7
decorator==5.1.1
deepdanbooru==1.0.2
defusedxml==0.7.1
executing==2.1.0
fastjsonschema==2.20.0
filelock==3.16.1
Flask==3.0.3
flatbuffers==24.3.25
fqdn==1.5.1
fsspec==2024.9.0
h11==0.14.0
httpcore==1.0.6
httpx==0.27.2
huggingface-hub==0.22.2
humanfriendly==10.0
idna==3.10
imageio==2.36.0
ipykernel==6.29.5
ipython==8.28.0
isoduration==20.11.0
itsdangerous==2.2.0
jedi==0.19.1
Jinja2==3.1.4
json5==0.9.25
jsonpointer==3.0.0
jsonschema==4.23.0
jsonschema-specifications==2024.10.1
jupyter-events==0.10.0
jupyter-lsp==2.2.5
jupyter_client==8.6.3
jupyter_core==5.7.2
jupyter_server==2.14.2
jupyter_server_terminals==0.5.3
jupyterlab==4.2.5
jupyterlab_pygments==0.3.0
jupyterlab_server==2.27.3
lazy_loader==0.4
MarkupSafe==3.0.2
matplotlib-inline==0.1.7
mistune==3.0.2
mpmath==1.3.0
nbclient==0.10.0
nbconvert==7.16.4
nbformat==5.10.4
nest-asyncio==1.6.0
networkx==3.4.1
notebook==7.2.2
notebook_shim==0.2.4
numpy==1.26.4
onnxruntime==1.17.3
opencv-python==4.9.0.80
overrides==7.7.0
packaging==24.1
pandas==2.2.2
pandocfilters==1.5.1
parso==0.8.4
pexpect==4.9.0
Pillow==10.0.1
platformdirs==4.3.6
prometheus_client==0.21.0
prompt_toolkit==3.0.48
protobuf==5.28.2
psutil==6.1.0
ptyprocess==0.7.0
pure_eval==0.2.3
pycparser==2.22
Pygments==2.18.0
python-dateutil==2.9.0.post0
python-json-logger==2.0.7
pytz==2024.2
PyYAML==6.0.2
pyzmq==26.2.0
referencing==0.35.1
requests==2.32.3
rfc3339-validator==0.1.4
rfc3986-validator==0.1.1
rpds-py==0.20.0
scikit-image==0.24.0
scipy==1.14.1
Send2Trash==1.8.3
six==1.16.0
sniffio==1.3.1
soupsieve==2.6
stack-data==0.6.3
sympy==1.13.3
terminado==0.18.1
tifffile==2024.9.20
tinycss2==1.3.0
tornado==6.4.1
tqdm==4.66.5
traitlets==5.14.3
types-python-dateutil==2.9.0.20241003
typing_extensions==4.12.2
tzdata==2024.2
uri-template==1.3.0
urllib3==2.2.3
wcwidth==0.2.13
webcolors==24.8.0
webencodings==0.5.1
websocket-client==1.8.0
Werkzeug==3.0.4
'''