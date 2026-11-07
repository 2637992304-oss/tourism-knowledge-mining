"""OpenAI-compatible Chat Completions HTTP client; no SDK or secret logging.

Protocol reference: https://developers.openai.com/api/docs/guides/function-calling
"""
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from mining_io import ROOT


class ModelError(RuntimeError):
    """Only sanitized errors may reach logs/case artifacts."""


@dataclass(repr=False)
class Config:
    api_key: str
    base_url: str
    model: str
    timeout: float = 90

    def __repr__(self):
        return f'Config(model={self.model!r}, api_key=<redacted>)'


def load_config(env_path=None,environ=None):
    """Read local .env without executing/interpolating values; real environment overrides file."""
    values={};path=Path(env_path or ROOT/'.env')
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            line=line.strip()
            if not line or line.startswith('#'):continue
            if line.startswith('export '):line=line[7:]
            key,sep,value=line.partition('=')
            if not sep:raise ModelError('config_invalid_line')
            value=value.strip()
            if len(value)>=2 and value[0]==value[-1] and value[0] in "\"'":value=value[1:-1]
            values[key.strip()]=value
    values.update(os.environ if environ is None else environ)
    required=['LLM_API_KEY','LLM_BASE_URL','LLM_MODEL']
    missing=[k for k in required if not values.get(k,'').strip()]
    if missing:raise ModelError('missing_config: '+', '.join(missing)+'；请在本地.env填写，不要把密钥发到聊天或提交Git')
    url=values['LLM_BASE_URL'].rstrip('/');parsed=urlparse(url)
    if parsed.scheme not in {'http','https'} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:raise ModelError('invalid_base_url')
    if parsed.scheme=='http' and parsed.hostname not in {'localhost','127.0.0.1','::1'}:raise ModelError('remote_base_url_requires_https')
    if parsed.path.endswith('/models'):raise ModelError('base_url_points_to_models：请填写API根路径，例如服务商确认的/v1，不要填写模型列表地址')
    try:timeout=float(values.get('LLM_TIMEOUT_SECONDS','90'))
    except ValueError:raise ModelError('invalid_timeout') from None
    if not 1<=timeout<=120:raise ModelError('invalid_timeout')
    return Config(values['LLM_API_KEY'],url,values['LLM_MODEL'],timeout)


class ChatClient:
    execution_mode='live_api'
    def __init__(self,config):self.config=config;self.requests=0

    @property
    def model(self):return self.config.model

    def complete(self,messages,tools=None,json_mode=False):
        c=self.config
        endpoint=c.base_url if c.base_url.endswith('/chat/completions') else c.base_url+'/chat/completions'
        payload={'model':c.model,'messages':messages,'stream':False}
        if tools:payload.update(tools=tools,tool_choice='auto')
        if json_mode:payload['response_format']={'type':'json_object'}
        body=json.dumps(payload,ensure_ascii=False).encode('utf8')
        for attempt in range(2):
            request=urllib.request.Request(endpoint,data=body,headers={'Authorization':'Bearer '+c.api_key,'Content-Type':'application/json'})
            try:
                self.requests+=1
                with urllib.request.urlopen(request,timeout=c.timeout) as response:
                    data=json.loads(response.read(4_000_001))
                message=data['choices'][0]['message']
                if data['choices'][0].get('finish_reason')=='length':raise ModelError('model_output_truncated')
                if not isinstance(message,dict):raise ModelError('invalid_model_response')
                # Drop reasoning_content / private fields before returning or persisting anything.
                return {k:message[k] for k in ['role','content','tool_calls'] if k in message}
            except urllib.error.HTTPError as exc:
                code=exc.code;exc.close()
                if attempt==0 and code in {429,502,503,504}:time.sleep(1);continue
                raise ModelError(f'llm_http_error_{code}：检查接口、模型权限或额度；响应体未记录') from None
            except (urllib.error.URLError,TimeoutError,OSError):
                if attempt==0:time.sleep(1);continue
                raise ModelError('llm_network_error_or_timeout') from None
            except (ValueError,KeyError,IndexError,TypeError):
                if attempt==0:time.sleep(1);continue
                raise ModelError('invalid_model_response') from None


def parse_json(content):
    if not isinstance(content,str):raise ModelError('expected_json_object')
    content=content.strip()
    if content.startswith('```'):
        content='\n'.join(content.splitlines()[1:-1])
    try:obj=json.loads(content)
    except (ValueError,TypeError):raise ModelError('invalid_model_json') from None
    if not isinstance(obj,dict):raise ModelError('expected_json_object')
    return obj
