import os
import json
import time
import hashlib
from pathlib import Path

from openai import (
    OpenAI, RateLimitError, APIConnectionError, InternalServerError
)
from diskcache import Cache
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type
)

PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",        # ⚠️ 以官方文档为准
        "key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
    },
    "github": {
        "base_url": "https://models.github.ai/inference",
        "key_env": "GH_MODELS_TOKEN",
        "model": "openai/gpt-4.1-mini",
    },
}

PROVIDER = os.environ.get("LLM_PROVIDER", "deepseek")
_cfg = PROVIDERS[PROVIDER]
DEFAULT_MODEL = _cfg["model"]

_key = (os.environ.get(_cfg["key_env"]) or "").strip()
if not _key:
    raise RuntimeError(f"环境变量 {_cfg['key_env']} 未设置")

_client = OpenAI(base_url=_cfg["base_url"], api_key=_key, timeout=90)
_cache = Cache(".cache/llm")
_LOG_FILE = Path("logs/llm_calls.jsonl")
_LOG_FILE.parent.mkdir(exist_ok=True)


@retry(
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, InternalServerError)
    ),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    reraise=True,
)
def _call_api(**kwargs):
    return _client.chat.completions.create(**kwargs)


def _log(record: dict):
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def chat(prompt, system=None, model=None, temperature=0,
         json_mode=False, max_tokens=None, use_cache=True):
    model = model or DEFAULT_MODEL
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    params = {"model": model, "messages": messages, "temperature": temperature}
    if json_mode:
        params["response_format"] = {"type": "json_object"}
    if max_tokens:
        params["max_tokens"] = max_tokens

    # 缓存键：所有会影响输出的东西都要放进去
    key = hashlib.sha256(
        json.dumps([_cfg["base_url"], params], ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()

    if use_cache and key in _cache:
        _log({"ts": time.time(), "cache": True, "model": model, "messages": messages})
        return _cache[key]

    start = time.time()
    try:
        resp = _call_api(**params)
        if isinstance(resp, str):   # 防护：返回的不是响应对象
            raise RuntimeError(f"接口返回了非 JSON 内容：{resp[:100]!r}")
    except Exception as e:
        _log({"ts": start, "error": repr(e), "model": model, "messages": messages})
        raise

    choice = resp.choices[0]
    text = choice.message.content
    if choice.finish_reason == "length":
        print("⚠️ 输出被 max_tokens 截断")

    _cache[key] = text
    _log({
        "ts": start,
        "cache": False,
        "provider": PROVIDER,
        "model": model,
        "latency_s": round(time.time() - start, 2),
        "finish_reason": choice.finish_reason,
        "usage": resp.usage.model_dump() if resp.usage else None,
        "messages": messages,
        "output": text,
    })
    return text


if __name__ == "__main__":
    print(chat("用一句话解释什么是语义层"))