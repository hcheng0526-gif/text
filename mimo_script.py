import requests
import json
import base64
import os

# --- 1. 全局配置 ---
# 从 GitHub Actions 的 Secrets 中读取 Key
MIMO_API_KEY = os.getenv("MIMO_API_KEY")
# 使用你之前提供的 API 基础地址
MIMO_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

def prepare_capcut_assets(theme):
    if not MIMO_API_KEY:
        print("❌ 错误：环境变量 MIMO_API_KEY 未设置，请检查 GitHub Secrets。")
        return

    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # --- 2. 生成剧本逻辑 ---
    script_payload = {
        "model": "mimo-v2.5-pro",
        "messages": [{
            "role": "user", 
            "content": f"写一个'{theme}'的短视频剧本。角色：小猫(女)、狗子(男)。输出JSON格式，包含dialogue列表（含role和text字段）以及video_prompt。"
        }],
        "response_format": {"type": "json_object"}
    }
    
    print(f"🚀 正在生成剧本: {theme}")
    res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=script_payload, headers=headers)
    
    if res.status_code != 200:
        print(f"❌ 剧本生成失败: {res.text}")
        return

    script_data_raw = res.json()['choices'][0]['message']['content']
    with open("script_and_prompt.json", "w", encoding="utf-8") as f:
        f.write(script_data_raw)
    
    data = json.loads(script_data_raw)

    # --- 3. 生成配音逻辑 ---
    if not os.path.exists("output_audio"):
        os.makedirs("output_audio")

    for i, item in enumerate(data.get('dialogue', [])):
        role = item.get('role', 'unknown')
        text = item.get('text', '')
        
        # --- 核心修复：使用 API 支持的音色名称 ---
        # 小猫设定为 '茉莉' (可用列表中的女声)
        # 狗子设定为 'Dean' (可用列表中的男声)
        voice = "茉莉" if "猫" in role else "Dean"
        
        tts_payload = {
            "model": "mimo-v2.5-tts",
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": "mp3"},
            "messages": [{"role": "assistant", "content": text}]
        }
        
        print(f"🎙️ 正在为 {role} 生成配音 (使用音色: {voice})...")
        tts_res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=tts_payload, headers=headers)
        
        if tts_res.status_code == 200:
            audio_b64 = tts_res.json()['choices'][0]['message']['audio']['data']
            filename = f"output_audio/{i+1}_{role}.mp3"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"✅ 已保存: {filename}")
        else:
            print(f"❌ 配音接口报错: {tts_res.text}")

if __name__ == "__main__":
    # 获取 GitHub Actions 传入的主题
    target_theme = os.getenv("VIDEO_THEME", "猫咪吐槽金毛掉毛太多")
    prepare_capcut_assets(target_theme)
