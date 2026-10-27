import sys
sys.path.insert(0, "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES")
import importlib.util
import sys

# Load the CURRENT working-tree full_hexagram_shotgun.py by file path
spec = importlib.util.spec_from_file_location(
    "shotgun_current", "C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/full_hexagram_shotgun.py"
)
m = importlib.util.module_from_spec(spec)
sys.modules["shotgun_current"] = m
spec.loader.exec_module(m)

import emotional_engine as ee

p = m.shotgun_expand(request_text="shotgun blast", emotional_input=50)

print("audit dict:", ee.HAMILTONIAN_PAIRED_DIFFERENTIALS)
print("payload total_encodings:", p.get("total_encodings"))
print("payload total_resolved:", p.get("total_resolved"))
print("avg_hamiltonian_energy:", p.get("avg_hamiltonian_energy"))
print("identity preserved (is HEXAGRAM_BASE_TYPED is HEXAGRAM_BASE):",
      ee.HEXAGRAM_BASE_TYPED is ee.HEXAGRAM_BASE)
print("expanded[0] has expanded_vector:", bool(p["expanded"][0].get("expanded_vector")))
print("line_balance has old_yin_count:", p["expanded"][0].get("line_balance", {}).get("old_yin_count"))
print("resolved[0] qdot computed alive:", p["resolved"][0].get("qdot"))
print("sorted OK")
