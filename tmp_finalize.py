import json, os, hashlib
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
source_id = "AN013"
filepath = r"inbox\Alan Nicolas\PODCASTS\UGC Audiencia Fortnite AIOX e Games com IA [youtube_rRBDxe3dM_s].txt"

# MD5
with open(filepath, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()

# File registry
reg_path = r"system\REGISTRY\file-registry.json"
os.makedirs(os.path.dirname(reg_path), exist_ok=True)
if os.path.exists(reg_path):
    with open(reg_path, 'r', encoding='utf-8') as f:
        reg = json.load(f)
else:
    reg = {"files": []}

reg["files"] = [r for r in reg["files"] if r.get("source_id") != source_id]
reg["files"].append({
    "source_id": source_id,
    "path": filepath,
    "md5": md5,
    "youtube_id": "rRBDxe3dM_s",
    "person": "Alan Nicolas",
    "type": "PODCAST",
    "registered_at": datetime.now().isoformat(),
    "status": "PROCESSED"
})

with open(reg_path, 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False, indent=2)
print("File registry OK")

# INBOX-REGISTRY
inbox_reg_path = r"system\REGISTRY\INBOX-REGISTRY.md"
if os.path.exists(inbox_reg_path):
    with open(inbox_reg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if source_id not in content:
        entry = f"\n### {source_id}: UGC Audiencia Fortnite AIOX e Games com IA\n| Campo | Valor |\n|-------|-------|\n| **Path** | `{filepath}` |\n| **MD5** | `{md5}` |\n| **Status** | `COMPLETE` |\n| **Processado em** | {today} |\n| **Chunks** | 80 |\n| **Insights** | 10 (5 HIGH) |\n"
        with open(inbox_reg_path, 'a', encoding='utf-8') as f:
            f.write(entry)
        print("INBOX-REGISTRY atualizado")
    else:
        print("INBOX-REGISTRY ja tem entry")
else:
    print("INBOX-REGISTRY nao encontrado")

print(f"AN013 registrado com MD5: {md5}")
