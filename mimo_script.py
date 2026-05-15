import requests
import json
import base64
import os

# --- 配置 ---
MIMO_API_KEY = "你的_MIMO_API_KEY"
MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"

def prepare_capcut_assets(theme):
    headers = {"Authorization": f"Bearer {MIMO_API_KEY}", "Content-Type": "application/json"}
    
    # 1. 让 MiMo 写剧本并明确画面描述
    script_payload = {
        "model": "mimo-v2.5-pro",
        "messages": [{
            "role": "user", 
            "content": f"写一个'{theme}'的短视频剧本。角色：小猫(女声,橘色德文猫)、狗子(男声,大金毛)。输出JSON，包含对话列表和一段详细的视频描述词。"
        }],
        "response_format": {"type": "json_object"}
    }
    
    res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=script_payload, headers=headers)
    data = json.loads(res.json()['choices'][0]['message']['content'])
    
    print(f"🎬 视频提示词（去即梦生成这个）：\n{data['video_prompt']}\n")

    # 2. 生成配音文件，方便在剪映里排列
    for i, item in enumerate(data['dialogue']):
        # 根据角色分配 MiMo-TTS 音色
        voice = "mimo_female_cute" if "猫" in item['role'] else "mimo_male_gentle"
        
        tts_payload = {
            "model": "mimo-v2.5-tts",
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": "mp3"},
            "messages": [{"role": "assistant", "content": item['text']}]
        }
        
        tts_res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=tts_payload, headers=headers)
        audio_data = base64.b64decode(tts_res.json()['choices'][0]['message']['audio']['data'])
        
        # 文件命名加上序号，方便在剪映里按顺序排列
        filename = f"{i+1}_{item['role']}.mp3"
        with open(filename, "wb") as f:
            f.write(audio_data)
        print(f"🔊 已生成配音：{filename}")

if __name__ == "__main__":
    prepare_capcut_assets("猫咪吐槽金毛掉毛太多")
