import requests
import json

# 1. 配置你的 API 信息
API_KEY = "你的小米MiMo_API_KEY"
URL = "https://api.mimo.xiaomi.com/v2.5/chat/completions"

# 2. 定义你的题库 (这里可以放你的 30 道题)
quiz_list = [
    {
        "id": 1,
        "title": "副驾驶归属权",
        "option_a": "必须是我的专属位置，别人坐我会炸毛",
        "option_b": "只是个座位，普通异性同事坐也无所谓"
    },
    {
        "id": 2,
        "title": "前任社交边界",
        "option_b": "完全断联，互删是基本尊重",
        "option_a": "偶尔点赞，只要不私聊就没问题"
    }
    # ... 继续添加你的 30 道题
]

def generate_xhs_batch():
    all_scripts = []
    
    for item in quiz_list:
        print(f"正在处理题目：{item['title']}...")
        
        # 3. 构造 Prompt，直接代入变量
        prompt = f"""
        你是一个拥有百万粉丝的小红书情感博主。
        我们要针对《镜像坦白局》这个测试做引流。
        
        题目：{item['title']}
        分歧点：一方认为“{item['option_a']}”，另一方认为“{item['option_b']}”。
        
        请生成一个短视频脚本：
        1. [标题] 要带“价值观碰撞”、“情侣必看”等关键词。
        2. [第一幕] 还原一个具体的吵架或尴尬场景。
        3. [第二幕] 用扎心的语言分析两人的底层逻辑差异。
        4. [结尾] 引导：‘想知道你们的镜像同步率吗？点击链接测一测’。
        """
        
        payload = {
            "model": "mimLM-v2.5-pro",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8  # 调高一点，让文案更有创意
        }
        
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        
        response = requests.post(URL, json=payload, headers=headers)
        script_content = response.json()['choices'][0]['message']['content']
        
        all_scripts.append({"id": item['id'], "script": script_content})

    # 4. 将所有生成的脚本保存为本地文件
    with open("xhs_scripts_batch.json", "w", encoding="utf-8") as f:
        json.dump(all_scripts, f, ensure_ascii=False, indent=4)
    
    print("✨ 30套爆款脚本生成完毕！请查看 xhs_scripts_batch.json")

if __name__ == "__main__":
    generate_xhs_batch()