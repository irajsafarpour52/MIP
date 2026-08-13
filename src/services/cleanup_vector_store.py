import chromadb


DB_PATH = r"D:\MIP\data\chroma"


client = chromadb.PersistentClient(
    path=DB_PATH
)


collection = client.get_collection(
    name="mip_meetings"
)

test_ids = [
    "meeting_20260809_document_01",
    "meeting_20260809_summary_02",
    "meeting_20260809_decision_03",
    "meeting_20260809_decision_04",
    "meeting_20260809_task_06",
]


print("Cleaning test data...")


collection.delete(
    ids=test_ids
)


print("Test data deleted successfully.")


print("\n===== REMAINING IDS =====")

result = collection.get(
    include=["documents", "metadatas"]
)

for chunk_id in result["ids"]:
    print(chunk_id)