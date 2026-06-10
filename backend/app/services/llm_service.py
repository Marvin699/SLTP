"""大模型调用服务 — OpenAI 兼容接口（DeepSeek / 通义千问 / 智谱等）"""
import os
from openai import OpenAI
from app.core.config import settings

# Agent 和 LLM 配置文件目录
AGENT_DIR_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Agent"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "LLM"),
    os.path.join(os.getcwd(), "Agent"),
    os.path.join(os.getcwd(), "LLM"),
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Agent")),
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "LLM")),
]

def _find_agent_dir():
    for d in AGENT_DIR_CANDIDATES:
        if os.path.isdir(d):
            return d
    return AGENT_DIR_CANDIDATES[0]

AGENT_DIR = _find_agent_dir()
CONFIG_DIR = AGENT_DIR if AGENT_DIR.endswith("LLM") else AGENT_DIR_CANDIDATES[1]


def get_client():
    """获取 OpenAI 兼容客户端"""
    if not settings.LLM_API_KEY:
        return None
    return OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        timeout=180.0,
    )


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """
    调用大模型对话

    返回模型回复文本，若未配置 API Key 则返回 None
    """
    client = get_client()
    if not client:
        return None

    try:
        print(f"[LLM] 开始调用 {settings.LLM_MODEL}...")
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=4096,
        )
        msg = response.choices[0].message
        content = msg.content
        print(f"[LLM] 调用完成, finish_reason={response.choices[0].finish_reason}")

        # 推理模型（如 glm-4.7-flash）会把思考过程放在 reasoning_content
        # 如果 content 为空但 reasoning_content 有内容，使用 reasoning_content
        if not content and hasattr(msg, 'reasoning_content') and msg.reasoning_content:
            print(f"[LLM] content 为空，使用 reasoning_content")
            content = msg.reasoning_content

        print(f"[LLM] 返回内容: {repr(content)[:300]}")
        if not content:
            print(f"[LLM] 返回为空! 完整响应: {response}")
        return content
    except Exception as e:
        print(f"[LLM] 调用异常: {type(e).__name__}: {e}")
        raise RuntimeError(f"大模型调用失败: {str(e)}")


def load_agent_prompt(agent_filename: str) -> str:
    """
    从 Agent/ 目录加载 agent 系统提示词

    参数:
        agent_filename: agent 文件名，如 "uavSEA.md"

    若文件不存在则返回兜底 prompt, 避免 AI 选型直接崩。
    """
    for d in AGENT_DIR_CANDIDATES:
        filepath = os.path.join(d, agent_filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    fallback = (
        "你是智慧低空应急运输教学平台的无人机选型智能体。\n"
        "用户将给出应急物资需求、起飞点、配送点等信息，请你推荐合适的无人机型号、数量与趟次方案。\n"
        "输出 JSON，字段参考平台接口约定: {\"uav_model\":\"...\",\"count\":N,\"per_payload\":N,\"reason\":\"...\"}。"
    )
    print(f"[LLM] Agent 文件 {agent_filename} 未找到 (已搜索 {AGENT_DIR_CANDIDATES})，使用兜底 prompt")
    return fallback


def load_config_content(config_filename: str = "任务配置信息.md") -> str:
    """
    从 LLM/ 目录加载配置信息文件内容

    参数:
        config_filename: 配置文件名，默认 "任务配置信息.md"
    """
    filepath = os.path.join(CONFIG_DIR, config_filename)
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def is_configured() -> bool:
    """检查是否已配置 LLM"""
    return bool(settings.LLM_API_KEY)
