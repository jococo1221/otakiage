from tag_store import TagStore
from rfid_tags import rfid_tags

store = TagStore("rfid_tags.db")

def is_all_zero(uid_list):
    return all(int(x) == 0 for x in uid_list)

skipped = 0
inserted = 0

for key, data in rfid_tags.items():
    uid_list = data["uid"]
    if is_all_zero(uid_list):
        skipped += 1
        continue  # skip placeholders that all share the same zero UID

    uid_bytes = bytes(int(x) for x in uid_list)
    msg = data.get("message", "")
    func = data.get("function", "none")
    store.upsert(int(key), uid_bytes, msg, func)
    inserted += 1

print(f"Migration complete. Inserted: {inserted}, Skipped zero-UID placeholders: {skipped}")
