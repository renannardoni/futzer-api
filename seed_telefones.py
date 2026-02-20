import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://renannardoni:Parma197$@cluster0.qiakegl.mongodb.net/?appName=Cluster0"

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["futzer_db"]
    col = db["quadras"]

    ops = [
        ("Arena RNMG",             "(11) 98765-4321"),
        ("Quadra Teste via Script", "(11) 91234-5678"),
        ("Arena Test",             "(11) 93456-7890"),
    ]

    for nome, tel in ops:
        r = await col.update_many({"nome": nome}, {"$set": {"telefone": tel}})
        print(f"{nome}: {r.modified_count} doc(s) atualizados com telefone {tel}")

    client.close()
    print("Concluido.")

asyncio.run(main())
