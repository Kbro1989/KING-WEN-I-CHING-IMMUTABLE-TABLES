import ast, json, re
# ============================================================
# STATIC KING WEN REGISTRY — Verified, Immutable
# ============================================================

HEXAGRAMS = [
    {"id": 1, "name": "The Creative", "chinese": "乾", "pinyin": "qián", "binary": "111111", "unicode": "\u4dc0", "upper_trigram": "Qian", "lower_trigram": "Qian", "category": "sovereign", "action": "ASSERT"},
    {"id": 2, "name": "The Receptive", "chinese": "坤", "pinyin": "kūn", "binary": "000000", "unicode": "\u4dc1", "upper_trigram": "Kun", "lower_trigram": "Kun", "category": "transformer", "action": "YIELD"},
    {"id": 3, "name": "Difficulty at the Beginning", "chinese": "屯", "pinyin": "zhūn", "binary": "010001", "unicode": "\u4dc2", "upper_trigram": "Zhen", "lower_trigram": "Kan", "category": "dissipator", "action": "ADAPT"},
    {"id": 4, "name": "Youthful Folly", "chinese": "蒙", "pinyin": "méng", "binary": "100010", "unicode": "\u4dc3", "upper_trigram": "Kan", "lower_trigram": "Gen", "category": "transformer", "action": "WAIT"},
    {"id": 5, "name": "Waiting", "chinese": "需", "pinyin": "xū", "binary": "010111", "unicode": "\u4dc4", "upper_trigram": "Qian", "lower_trigram": "Kan", "category": "dissipator", "action": "WAIT"},
    {"id": 6, "name": "Conflict", "chinese": "訟", "pinyin": "sòng", "binary": "111010", "unicode": "\u4dc5", "upper_trigram": "Kan", "lower_trigram": "Qian", "category": "transformer", "action": "ASSERT"},
    {"id": 7, "name": "The Army", "chinese": "師", "pinyin": "shī", "binary": "000010", "unicode": "\u4dc6", "upper_trigram": "Kan", "lower_trigram": "Kun", "category": "sovereign", "action": "ASSERT"},
    {"id": 8, "name": "Holding Together", "chinese": "比", "pinyin": "bǐ", "binary": "010000", "unicode": "\u4dc7", "upper_trigram": "Kun", "lower_trigram": "Kan", "category": "transformer", "action": "YIELD"},
    {"id": 9, "name": "Taming Power of the Small", "chinese": "小畜", "pinyin": "xiǎo chù", "binary": "110111", "unicode": "\u4dc8", "upper_trigram": "Qian", "lower_trigram": "Xun", "category": "dissipator", "action": "ADAPT"},
    {"id": 10, "name": "Treading", "chinese": "履", "pinyin": "lǚ", "binary": "111011", "unicode": "\u4dc9", "upper_trigram": "Dui", "lower_trigram": "Qian", "category": "sovereign", "action": "ADAPT"},
    {"id": 11, "name": "Peace", "chinese": "泰", "pinyin": "tài", "binary": "000111", "unicode": "\u4dca", "upper_trigram": "Qian", "lower_trigram": "Kun", "category": "transformer", "action": "YIELD"},
    {"id": 12, "name": "Standstill", "chinese": "否", "pinyin": "pǐ", "binary": "111000", "unicode": "\u4dcb", "upper_trigram": "Kun", "lower_trigram": "Qian", "category": "boundary", "action": "WAIT"},
    {"id": 13, "name": "Fellowship with Men", "chinese": "同人", "pinyin": "tóng rén", "binary": "101111", "unicode": "\u4dcc", "upper_trigram": "Qian", "lower_trigram": "Li", "category": "transformer", "action": "ASSERT"},
    {"id": 14, "name": "Possession in Great Measure", "chinese": "大有", "pinyin": "dà yǒu", "binary": "111101", "unicode": "\u4dcd", "upper_trigram": "Li", "lower_trigram": "Qian", "category": "sovereign", "action": "ASSERT"},
    {"id": 15, "name": "Modesty", "chinese": "謙", "pinyin": "qiān", "binary": "001000", "unicode": "\u4dce", "upper_trigram": "Kun", "lower_trigram": "Gen", "category": "transformer", "action": "YIELD"},
    {"id": 16, "name": "Enthusiasm", "chinese": "豫", "pinyin": "yù", "binary": "000100", "unicode": "\u4dcf", "upper_trigram": "Zhen", "lower_trigram": "Kun", "category": "dissipator", "action": "ADAPT"},
    {"id": 17, "name": "Following", "chinese": "隨", "pinyin": "suí", "binary": "100110", "unicode": "\u4dd0", "upper_trigram": "Zhen", "lower_trigram": "Dui", "category": "transformer", "action": "YIELD"},
    {"id": 18, "name": "Work on Decayed", "chinese": "蠱", "pinyin": "gǔ", "binary": "011001", "unicode": "\u4dd1", "upper_trigram": "Xun", "lower_trigram": "Gen", "category": "dissipator", "action": "ADAPT"},
    {"id": 19, "name": "Approach", "chinese": "臨", "pinyin": "lín", "binary": "110000", "unicode": "\u4dd2", "upper_trigram": "Kun", "lower_trigram": "Dui", "category": "transformer", "action": "YIELD"},
    {"id": 20, "name": "Contemplation", "chinese": "觀", "pinyin": "guān", "binary": "000011", "unicode": "\u4dd3", "upper_trigram": "Xun", "lower_trigram": "Kun", "category": "boundary", "action": "WAIT"},
    {"id": 21, "name": "Biting Through", "chinese": "噬嗑", "pinyin": "shì kè", "binary": "100101", "unicode": "\u4dd4", "upper_trigram": "Zhen", "lower_trigram": "Li", "category": "transformer", "action": "ASSERT"},
    {"id": 22, "name": "Grace", "chinese": "賁", "pinyin": "bì", "binary": "101001", "unicode": "\u4dd5", "upper_trigram": "Li", "lower_trigram": "Gen", "category": "boundary", "action": "WAIT"},
    {"id": 23, "name": "Splitting Apart", "chinese": "剝", "pinyin": "bō", "binary": "000001", "unicode": "\u4dd6", "upper_trigram": "Kun", "lower_trigram": "Gen", "category": "dissipator", "action": "WAIT"},
    {"id": 24, "name": "Return", "chinese": "復", "pinyin": "fù", "binary": "100000", "unicode": "\u4dd7", "upper_trigram": "Zhen", "lower_trigram": "Kun", "category": "transformer", "action": "YIELD"},
    {"id": 25, "name": "Innocence", "chinese": "无妄", "pinyin": "wú wàng", "binary": "100111", "unicode": "\u4dd8", "upper_trigram": "Zhen", "lower_trigram": "Qian", "category": "sovereign", "action": "ASSERT"},
    {"id": 26, "name": "Taming Power of the Great", "chinese": "大畜", "pinyin": "dà chù", "binary": "111001", "unicode": "\u4dd9", "upper_trigram": "Qian", "lower_trigram": "Gen", "category": "boundary", "action": "ADAPT"},
    {"id": 27, "name": "Corners of the Mouth", "chinese": "頤", "pinyin": "yí", "binary": "100001", "unicode": "\u4dda", "upper_trigram": "Zhen", "lower_trigram": "Gen", "category": "transformer", "action": "YIELD"},
    {"id": 28, "name": "Preponderance of the Great", "chinese": "大過", "pinyin": "dà guò", "binary": "011110", "unicode": "\u4ddb", "upper_trigram": "Xun", "lower_trigram": "Dui", "category": "dissipator", "action": "ADAPT"},
    {"id": 29, "name": "The Abysmal", "chinese": "坎", "pinyin": "kǎn", "binary": "010010", "unicode": "\u4ddc", "upper_trigram": "Kan", "lower_trigram": "Kan", "category": "dissipator", "action": "WAIT"},
    {"id": 30, "name": "The Clinging", "chinese": "離", "pinyin": "lí", "binary": "101101", "unicode": "\u4ddd", "upper_trigram": "Li", "lower_trigram": "Li", "category": "boundary", "action": "ADAPT"},
    {"id": 31, "name": "Influence", "chinese": "咸", "pinyin": "xián", "binary": "001110", "unicode": "\u4dde", "upper_trigram": "Gen", "lower_trigram": "Dui", "category": "transformer", "action": "YIELD"},
    {"id": 32, "name": "Duration", "chinese": "恆", "pinyin": "héng", "binary": "011100", "unicode": "\u4ddf", "upper_trigram": "Xun", "lower_trigram": "Zhen", "category": "boundary", "action": "WAIT"},
    {"id": 33, "name": "Retreat", "chinese": "遯", "pinyin": "dùn", "binary": "001111", "unicode": "\u4de0", "upper_trigram": "Gen", "lower_trigram": "Qian", "category": "boundary", "action": "YIELD"},
    {"id": 34, "name": "Power of the Great", "chinese": "大壯", "pinyin": "dà zhuàng", "binary": "111100", "unicode": "\u4de1", "upper_trigram": "Qian", "lower_trigram": "Zhen", "category": "sovereign", "action": "ASSERT"},
    {"id": 35, "name": "Progress", "chinese": "晉", "pinyin": "jìn", "binary": "000101", "unicode": "\u4de2", "upper_trigram": "Kun", "lower_trigram": "Li", "category": "transformer", "action": "ADAPT"},
    {"id": 36, "name": "Darkening of the Light", "chinese": "明夷", "pinyin": "míng yí", "binary": "101000", "unicode": "\u4de3", "upper_trigram": "Li", "lower_trigram": "Kun", "category": "dissipator", "action": "WAIT"},
    {"id": 37, "name": "The Family", "chinese": "家人", "pinyin": "jiā rén", "binary": "101011", "unicode": "\u4de4", "upper_trigram": "Li", "lower_trigram": "Xun", "category": "transformer", "action": "YIELD"},
    {"id": 38, "name": "Opposition", "chinese": "睽", "pinyin": "kuí", "binary": "110101", "unicode": "\u4de5", "upper_trigram": "Dui", "lower_trigram": "Li", "category": "dissipator", "action": "ADAPT"},
    {"id": 39, "name": "Obstruction", "chinese": "蹇", "pinyin": "jiǎn", "binary": "010100", "unicode": "\u4de6", "upper_trigram": "Gen", "lower_trigram": "Kan", "category": "dissipator", "action": "WAIT"},
    {"id": 40, "name": "Deliverance", "chinese": "解", "pinyin": "xiè", "binary": "001010", "unicode": "\u4de7", "upper_trigram": "Kan", "lower_trigram": "Zhen", "category": "transformer", "action": "ADAPT"},
    {"id": 41, "name": "Decrease", "chinese": "損", "pinyin": "sǔn", "binary": "100011", "unicode": "\u4de8", "upper_trigram": "Dui", "lower_trigram": "Gen", "category": "transformer", "action": "YIELD"},
    {"id": 42, "name": "Increase", "chinese": "益", "pinyin": "yì", "binary": "110001", "unicode": "\u4de9", "upper_trigram": "Zhen", "lower_trigram": "Xun", "category": "transformer", "action": "ASSERT"},
    {"id": 43, "name": "Breakthrough", "chinese": "夬", "pinyin": "guài", "binary": "111110", "unicode": "\u4dea", "upper_trigram": "Qian", "lower_trigram": "Dui", "category": "sovereign", "action": "ASSERT"},
    {"id": 44, "name": "Coming to Meet", "chinese": "姤", "pinyin": "gòu", "binary": "011111", "unicode": "\u4deb", "upper_trigram": "Xun", "lower_trigram": "Qian", "category": "boundary", "action": "WAIT"},
    {"id": 45, "name": "Gathering Together", "chinese": "萃", "pinyin": "cuì", "binary": "000110", "unicode": "\u4dec", "upper_trigram": "Kun", "lower_trigram": "Dui", "category": "transformer", "action": "YIELD"},
    {"id": 46, "name": "Pushing Upward", "chinese": "升", "pinyin": "shēng", "binary": "011000", "unicode": "\u4ded", "upper_trigram": "Xun", "lower_trigram": "Kun", "category": "transformer", "action": "ADAPT"},
    {"id": 47, "name": "Oppression", "chinese": "困", "pinyin": "kùn", "binary": "010110", "unicode": "\u4dee", "upper_trigram": "Kan", "lower_trigram": "Dui", "category": "dissipator", "action": "WAIT"},
    {"id": 48, "name": "The Well", "chinese": "井", "pinyin": "jǐng", "binary": "011010", "unicode": "\u4def", "upper_trigram": "Xun", "lower_trigram": "Kan", "category": "boundary", "action": "YIELD"},
    {"id": 49, "name": "Revolution", "chinese": "革", "pinyin": "gé", "binary": "101110", "unicode": "\u4df0", "upper_trigram": "Li", "lower_trigram": "Dui", "category": "transformer", "action": "ASSERT"},
    {"id": 50, "name": "The Cauldron", "chinese": "鼎", "pinyin": "dǐng", "binary": "011101", "unicode": "\u4df1", "upper_trigram": "Xun", "lower_trigram": "Li", "category": "sovereign", "action": "ASSERT"},
    {"id": 51, "name": "The Arousing", "chinese": "震", "pinyin": "zhèn", "binary": "100100", "unicode": "\u4df2", "upper_trigram": "Zhen", "lower_trigram": "Zhen", "category": "sovereign", "action": "ASSERT"},
    {"id": 52, "name": "Keeping Still", "chinese": "艮", "pinyin": "gèn", "binary": "001001", "unicode": "\u4df3", "upper_trigram": "Gen", "lower_trigram": "Gen", "category": "boundary", "action": "WAIT"},
    {"id": 53, "name": "Development", "chinese": "漸", "pinyin": "jiàn", "binary": "001011", "unicode": "\u4df4", "upper_trigram": "Gen", "lower_trigram": "Xun", "category": "transformer", "action": "ADAPT"},
    {"id": 54, "name": "The Marrying Maiden", "chinese": "歸妹", "pinyin": "guī mèi", "binary": "110100", "unicode": "\u4df5", "upper_trigram": "Dui", "lower_trigram": "Zhen", "category": "dissipator", "action": "YIELD"},
    {"id": 55, "name": "Abundance", "chinese": "豐", "pinyin": "fēng", "binary": "001101", "unicode": "\u4df6", "upper_trigram": "Li", "lower_trigram": "Zhen", "category": "sovereign", "action": "ASSERT"},
    {"id": 56, "name": "The Wanderer", "chinese": "旅", "pinyin": "lǚ", "binary": "101100", "unicode": "\u4df7", "upper_trigram": "Gen", "lower_trigram": "Li", "category": "dissipator", "action": "ADAPT"},
    {"id": 57, "name": "The Gentle", "chinese": "巽", "pinyin": "xùn", "binary": "011011", "unicode": "\u4df8", "upper_trigram": "Xun", "lower_trigram": "Xun", "category": "boundary", "action": "YIELD"},
    {"id": 58, "name": "The Joyous", "chinese": "兌", "pinyin": "duì", "binary": "110110", "unicode": "\u4df9", "upper_trigram": "Dui", "lower_trigram": "Dui", "category": "transformer", "action": "YIELD"},
    {"id": 59, "name": "Dispersion", "chinese": "渙", "pinyin": "huàn", "binary": "010011", "unicode": "\u4dfa", "upper_trigram": "Kan", "lower_trigram": "Xun", "category": "dissipator", "action": "ADAPT"},
    {"id": 60, "name": "Limitation", "chinese": "節", "pinyin": "jié", "binary": "110010", "unicode": "\u4dfb", "upper_trigram": "Dui", "lower_trigram": "Kan", "category": "boundary", "action": "WAIT"},
    {"id": 61, "name": "Inner Truth", "chinese": "中孚", "pinyin": "zhōng fú", "binary": "110011", "unicode": "\u4dfc", "upper_trigram": "Dui", "lower_trigram": "Xun", "category": "transformer", "action": "YIELD"},
    {"id": 62, "name": "Preponderance of the Small", "chinese": "小過", "pinyin": "xiǎo guò", "binary": "001100", "unicode": "\u4dfd", "upper_trigram": "Zhen", "lower_trigram": "Gen", "category": "dissipator", "action": "WAIT"},
    {"id": 63, "name": "After Completion", "chinese": "既濟", "pinyin": "jì jì", "binary": "101010", "unicode": "\u4dfe", "upper_trigram": "Li", "lower_trigram": "Kan", "category": "boundary", "action": "WAIT"},
    {"id": 64, "name": "Before Completion", "chinese": "未濟", "pinyin": "wèi jì", "binary": "010101", "unicode": "\u4dff", "upper_trigram": "Kan", "lower_trigram": "Li", "category": "transformer", "action": "ADAPT"},
]

# Verify uniqueness
binaries = [h["binary"] for h in HEXAGRAMS]
assert len(binaries) == len(set(binaries)), f"Duplicate binaries found: {[b for b in binaries if binaries.count(b) > 1]}"

# Inversion pairs (reversed binary)
inversion_pairs = [(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16),(17,18),(19,20),(21,22),(23,24),(25,26),(31,32),(33,34),(35,36),(37,38),(39,40),(41,42),(43,44),(45,46),(47,48),(49,50),(51,52),(53,54),(55,56),(57,58),(59,60),(63,64)]
for a, b in inversion_pairs:
    ba = HEXAGRAMS[a-1]["binary"]
    bb = HEXAGRAMS[b-1]["binary"]
    assert ba[::-1] == bb, f"Inversion pair {a}-{b} failed: {ba} vs {bb}"

# Complementary pairs (bit-flipped)
complementary_pairs = [(1,2),(11,12),(17,18),(27,28),(29,30),(61,62)]
for a, b in complementary_pairs:
    ba = HEXAGRAMS[a-1]["binary"]
    bb = HEXAGRAMS[b-1]["binary"]
    comp = "".join("1" if c == "0" else "0" for c in ba)
    assert comp == bb, f"Complementary pair {a}-{b} failed: {ba} complement={comp} vs {bb}"

print("✅ All 64 hexagrams verified:")
print(f"   - All binaries unique: {len(set(binaries))} / 64")
print(f"   - All {len(inversion_pairs)} inversion pairs verified")
print(f"   - All {len(complementary_pairs)} complementary pairs verified")
print(f"   - Unicode range: U+4DC0 to U+4DFF")
