import requests
import json
import base64
import os

# --- 全局配置 ---
# 严格从 GitHub Actions 的 Secrets 读取环境变量
MIMO_API_KEY = os.getenv("MIMO_API_KEY")
# 这里的 URL 使用你之前提供的地址
MIMO_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

def prepare_capcut_assets(theme):
    # 基础校验：确保 Key 存在
    if not MIMO_API_KEY:
        print("❌ 错误：未找到 MIMO_API_KEY，请在 GitHub Secrets 中配置。")
        return

    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. 调用 MiMo Pro 生成剧本
    script_payload = {
        "model": "mimo-v2.5-pro",
        "messages": [{
            "role": "user", 
            "content": f"写一个'{theme}'的短视频剧本。角色：小猫(橘色德文猫)、狗子(大金毛)。输出JSON格式，包含dialogue列表（含role和text字段）以及一段详细的视频描述词video_prompt。"
        }],
        "response_format": {"type": "json_object"}
    }
    
    print(f"🚀 正在生成剧本，主题: {theme}")
    res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=script_payload, headers=headers)
    
    if res.status_code != 200:
        print(f"❌ 剧本生成失败: {res.text}")
        return

    # 解析剧本内容并保存
    script_content_raw = res.json()['choices'][0]['message']['content']
    with open("script_and_prompt.json", "w", encoding="utf-8") as f:
        f.write(script_content_raw)
    
    data = json.loads(script_content_raw)
    print(f"✅ 剧本已保存至 script_and_prompt.json")
    print(f"🎬 视频提示词: {data.get('video_prompt', '')[:100]}...\n")

    # 2. 调用 MiMo TTS 生成配音
    if not os.path.exists("output_audio"):
        os.makedirs("output_audio")

    dialogues = data.get('dialogue', [])
    for i, item in enumerate(dialogues):
        role = item.get('role', 'unknown')
        text = item.get('text', '')
        
        # --- 音色映射（根据 API 报错提示的可用音色） ---
        # 小猫设定为 '茉莉' (女声)，狗子设定为 'Dean' (男声)
        if "猫" in role:
            voice = "茉莉"
        else:
            voice = "Dean"
        
        tts_payload = {
            "model": "mimo-v2.5-tts",
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": "mp3"},
            "messages": [{"role": "assistant", "content": text}]
        }
        
        print(f"🎙️ 正在为 [{role}] 生成配音，使用音色 [{voice}]...")
        tts_res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=tts_payload, headers=headers)
        
        if tts_res.status_code == 200:
            audio_b64 = tts_res.json()['choices'][0]['message']['audio']['data']
            # 文件名加入序号和角色，方便剪映排序
            filename = f"output_audio/{i+1}_{role}.mp3"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"✅ 已保存: {filename}")
        else:
            print(f"❌ 配音生成失败 [{role}]: {tts_res.text}")

if __name__ == "__main__":
    # 从 GitHub Actions 传入的输入中读取主题
    target_theme = os.getenv("VIDEO_THEME", "小猫和金毛讲笑话")
    prepare_capcut_assets(target_theme)
