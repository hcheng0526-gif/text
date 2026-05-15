import requests
import json
import base64
import os

# --- 1. 统一全局变量名 ---
# 必须确保这里 os.getenv 里的名字和 GitHub Secrets 里的名字完全一致
MIMO_API_KEY = os.getenv("MIMO_API_KEY") 
MIMO_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

def prepare_capcut_assets(theme):
    # 检查 Key 是否存在，避免 Authorization 字段出现 "Bearer None"
    if not MIMO_API_KEY:
        print("❌ 错误：环境变量 MIMO_API_KEY 为空。请检查 GitHub 仓库的 Secrets 配置。")
        return

    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}", 
        "Content-Type": "application/json"
    }
    
    # 1. 调用 MiMo 写剧本
    script_payload = {
        "model": "mimo-v2.5-pro",
        "messages": [{
            "role": "user", 
            "content": f"写一个'{theme}'的短视频剧本。角色：小猫(女声,橘色德文猫)、狗子(男声,大金毛)。输出JSON格式，包含dialogue列表和一段详细的视频描述词video_prompt。"
        }],
        "response_format": {"type": "json_object"}
    }
    
    print(f"🚀 正在为主题 '{theme}' 生成剧本...")
    res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=script_payload, headers=headers)
    
    if res.status_code != 200:
        print(f"❌ 剧本接口报错: {res.text}")
        return

    data = json.loads(res.json()['choices'][0]['message']['content'])
    print(f"🎬 画面提示词：{data.get('video_prompt', '无')}\n")

    # 2. 生成配音文件
    if not os.path.exists("output_audio"):
        os.makedirs("output_audio")

    for i, item in enumerate(data.get('dialogue', [])):
        # 分角色音色
        voice = "mimo_female_cute" if "猫" in item.get('role', '') else "mimo_male_gentle"
        
        tts_payload = {
            "model": "mimo-v2.5-tts",
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": "mp3"},
            "messages": [{"role": "assistant", "content": item.get('text', '')}]
        }
        
        print(f"🔊 正在生成第 {i+1} 段配音 ({item.get('role')})...")
        tts_res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=tts_payload, headers=headers)
        
        if tts_res.status_code == 200:
            audio_b64 = tts_res.json()['choices'][0]['message']['audio']['data']
            filename = f"output_audio/{i+1}_{item.get('role')}.mp3"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"✅ 已保存: {filename}")
        else:
            print(f"❌ 配音接口报错: {tts_res.text}")

if __name__ == "__main__":
    # 优先读取 Actions 传入的主题环境变量，没有则用默认值
    video_theme = os.getenv("VIDEO_THEME", "猫咪吐槽金毛掉毛太多")
    prepare_capcut_assets(video_theme)
