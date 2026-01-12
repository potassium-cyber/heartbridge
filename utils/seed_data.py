import sqlite3
from datetime import datetime
import random

DB_FILE = 'heartbridge.db'

# 测试数据集：旨在覆盖极端情绪，验证 NLP 分析的敏感度
TEST_DATA = [
    # --- 负面/焦虑 (预期得分 < 0.2) ---
    {
        "role": "孩子", "nickname": "绝望的深渊", "title": "我真的坚持不下去了",
        "content": "每天只有做不完的作业和考不完的试。父母只会责骂我，从来不关心我累不累。我感觉窒息，活着没有任何意义，我想结束这一切。太痛苦了，真的太痛苦了。"
    },
    {
        "role": "孩子", "nickname": "哭泣的角落", "title": "为什么总是比较",
        "content": "我讨厌被拿来和别人家的孩子比。无论我多努力，在他们眼里永远是不够好的。这种压力让我整夜失眠，头发大把大把地掉，我快崩溃了。"
    },
    {
        "role": "家长", "nickname": "甚至想哭的父亲", "title": "对不起孩子",
        "content": "最近失业了，家里经济压力很大，脾气没控制住吼了孩子。看着他恐惧的眼神，我真的好恨自己无能。生活为什么这么难？我该怎么办？"
    },
    
    # --- 正面/温情 (预期得分 > 0.8) ---
    {
        "role": "孩子", "nickname": "追光的少年", "title": "今天妈妈拥抱了我",
        "content": "今天鼓起勇气和妈妈聊了心里话，没想到她没有骂我，而是紧紧抱住了我。那一刻我感觉所有的委屈都化解了。谢谢你妈妈，我爱你，我们一起加油！"
    },
    {
        "role": "家长", "nickname": "幸福的园丁", "title": "孩子长大了",
        "content": "看到孩子主动帮我洗碗，那一刻真的好感动。其实成绩不是最重要的，只要他健康快乐，我就心满意足了。生活充满了希望和阳光，感恩拥有这一切。"
    },
    {
        "role": "孩子", "nickname": "快乐小狗", "title": "超级开心的一天",
        "content": "被老师表扬了！而且周末爸爸答应带我去游乐园！太棒了太棒了！我觉得世界超级美好，充满力量！冲鸭！"
    },

    # --- 中性/平淡 (预期得分 0.4 - 0.6) ---
    {
        "role": "孩子", "nickname": "观察者", "title": "关于校服的建议",
        "content": "我们学校的校服面料需要改进一下，夏天有点不透气。希望学校能采纳这个建议。"
    },
    {
        "role": "家长", "nickname": "路人", "title": "今天的天气",
        "content": "今天下雨了，出门记得带伞。路况稍微有点堵，大家注意安全。"
    }
]

def seed_database():
    print("🚀 开始注入测试数据...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    for post in TEST_DATA:
        # 随机生成一些点赞数
        likes = random.randint(0, 50)
        c.execute('''
            INSERT INTO posts (role, nickname, title, content, is_hidden, created_at, likes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (post['role'], post['nickname'], post['title'], post['content'], False, datetime.now(), likes))
    
    conn.commit()
    conn.close()
    print(f"✅ 成功注入 {len(TEST_DATA)} 条具有鲜明情感特征的测试数据。")

if __name__ == "__main__":
    choice = input("⚠️ 这将向数据库写入测试数据，是否继续？(y/n): ")
    if choice.lower() == 'y':
        seed_database()
    else:
        print("操作已取消。")
