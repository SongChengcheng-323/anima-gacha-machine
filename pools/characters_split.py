try:
    from pools.characters import CHARACTERS_SPLIT
except Exception:
    from characters import CHARACTERS_SPLIT

if __name__ == "__main__":
    print(f"characters_split 已改为转发；数据在 pools/characters.py，共 {len(CHARACTERS_SPLIT)} 个角色 ✓")
