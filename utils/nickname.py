import random

# 词库定义
# 结构：{'role': {'adjectives': [...], 'nouns': [...]}}

NICKNAME_DATA = {
    "家长": {
        "adjectives": [
            "焦虑的", "守望的", "唠叨的", "辛勤的", "默默的", 
            "严厉的", "操心的", "温暖的", "迷茫的", "坚强的"
        ],
        "nouns": [
            "猫头鹰", "长颈鹿", "老黄牛", "大树", "避风港", 
            "园丁", "向日葵", "守护者", "大狮子", "啄木鸟"
        ]
    },
    "孩子": {
        "adjectives": [
            "想要自由的", "还没睡醒的", "迷茫的", "愤怒的", "追梦的", 
            "压力山大的", "不想说话的", "敏感的", "甚至想哭的", "奥特曼打不过的"
        ],
        "nouns": [
            "风", "考拉", "刺猬", "独角兽", "小怪兽", 
            "宇航员", "流浪猫", "仙人掌", "蒲公英", "哈士奇"
        ]
    }
}

def generate_nickname(role):
    """
    根据角色生成随机昵称。
    
    Args:
        role (str): '家长' 或 '孩子'
        
    Returns:
        str: 组合后的昵称，例如 "焦虑的猫头鹰"
    """
    if role not in NICKNAME_DATA:
        return "神秘的路人甲"
    
    adj = random.choice(NICKNAME_DATA[role]["adjectives"])
    noun = random.choice(NICKNAME_DATA[role]["nouns"])
    
    return f"{adj}{noun}"

if __name__ == "__main__":
    # 测试代码
    print(f"家长示例: {generate_nickname('家长')}")
    print(f"孩子示例: {generate_nickname('孩子')}")
