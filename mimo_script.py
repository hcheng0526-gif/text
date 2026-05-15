import requests
import json
import base64
import os

# --- 配置 ---
# 统一变量名，确保全局可访问
MIMO_API_KEY = os.getenv("MIMO_API_KEY") 
# 建议直接使用这个基础 URL
MIMO_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

def prepare_capcut_assets(theme):
    # 检查 Key 是否成功加载
    if not MIMO_API_KEY:
        print("❌ 错误: 未找到环境变量 MIMO_API_KEY，请检查 GitHub Secrets 配置")
        return

    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}", 
        "Content-Type": "application/json"
    }
    
    # 1. 让 MiMo 写剧本并明确画面描述
    script_payload = {
        "model": "mimo-v2.5-pro",
        "messages": [{
            "role": "user", 
            "content": f"写一个'{theme}'的短视频剧本。角色：小猫(女声,橘色德文猫)、狗子(男声,大金毛)。输出JSON格式，包含dialogue列表（内含role和text）和一段详细的视频描述词video_prompt。"
        }],
        "response_format": {"type": "json_object"}
    }
    
    print(f"正在为主题 '{theme}' 生成剧本...")
    # 注意这里使用 MIMO_BASE_URL
    res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=script_payload, headers=headers)
    
    # 增加异常处理防止 API 返回错误导致脚本崩溃
    if res.status_code != 200:
        print(f"❌ 剧本生成请求失败: {res.text}")
        return

    res_json = res.json()
    data = json.loads(res_json['choices'][0]['message']['content'])
    
    print(f"🎬 视频提示词：\n{data.get('video_prompt', '未生成提示词')}\n")

    # 2. 生成配音文件
    dialogues = data.get('dialogue', [])
    for i, item in enumerate(dialogues):
        # 根据角色分配音色
        voice = "mimo_female_cute" if "猫" in item.get('role', '') else "mimo_male_gentle"
        
        tts_payload = {
            "model": "mimo-v2.5-tts",
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": "mp3"},
            "messages": [{"role": "assistant", "content": item.get('text', '')}]
        }
        
        print(f"🔊 正在生成第 {i+1} 段配音...")
        tts_res = requests.post(f"{MIMO_BASE_URL}/chat/completions", json=tts_payload, headers=headers)
        
        if tts_res.status_code == 200:
            audio_b64 = tts_res.json()['choices'][0]['message']['audio']['data']
            audio_data = base64.b64decode(audio_b64)
            
            filename = f"{i+1}_{item.get('role', 'role')}.mp3"
            with open(filename, "wb") as f:
                f.write(audio_data)
            print(f"✅ 已保存：{filename}")
        else:
            print(f"❌ 配音生成失败: {tts_res.text}")

if __name__ == "__main__":
    # 优先从环境变量读取主题（Actions 传入），否则使用默认
    target_theme = os.getenv("VIDEO_THEME", "猫咪吐槽金毛掉毛太多")
    prepare_capcut_assets(target_theme)
