from neo4j import GraphDatabase
import json
import os

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12341234"

driver = None
last_movies = []
selected_movie = None

def connect_db():
    global driver
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        with driver.session() as session:
            session.run("RETURN 1")
        return True
    except:
        return False


def film_ara():
    global last_movies
    keyword = input("Aranacak film adı: ").strip()

    if keyword == "":
        print("⚠ Boş arama yapılamaz.")
        return

    query = """
    MATCH (m:Movie)
    WHERE m.title CONTAINS $key
    RETURN m.title AS title, m.released AS year
    """

    with driver.session() as session:
        result = session.run(query, key=keyword)
        last_movies = list(result)

    if not last_movies:
        print("❌ Sonuç bulunamadı.")
        return

    for i, movie in enumerate(last_movies, start=1):
        print(f"{i}) {movie['title']} ({movie['year']})")


def film_detay():
    global selected_movie

    if not last_movies:
        print("⚠ Önce film arayın.")
        return

    try:
        secim = int(input("Film numarası: "))
        if secim < 1 or secim > len(last_movies):
            print("⚠ Geçersiz seçim.")
            return
    except:
        print("⚠ Sayı giriniz.")
        return

    selected_movie = last_movies[secim - 1]["title"]

    query = """
    MATCH (m:Movie {title:$title})
    OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
    OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
    RETURN m.title AS title,
           m.released AS year,
           m.tagline AS tagline,
           collect(DISTINCT d.name) AS directors,
           collect(DISTINCT a.name)[0..5] AS actors
    """

    with driver.session() as session:
        record = session.run(query, title=selected_movie).single()

    print("\n🎬 Film Detayı")
    print("Ad:", record["title"])
    print("Yıl:", record["year"])
    print("Tagline:", record["tagline"] if record["tagline"] else "Yok")

    print("\n🎥 Yönetmen(ler):")
    for d in record["directors"]:
        print("-", d)

    print("\n🎭 Oyuncular:")
    for a in record["actors"]:
        print("-", a)


def graph_json_olustur():
    if not selected_movie:
        print("⚠ Önce film seçmelisiniz.")
        return

    query = """
    MATCH (m:Movie {title:$title})
    OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
    OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
    RETURN m, d, a
    """

    nodes = []
    links = []
    node_ids = {}

    def add_node(name, label):
        if name not in node_ids:
            node_ids[name] = len(node_ids)
            nodes.append({"id": name, "label": label})

    with driver.session() as session:
        results = session.run(query, title=selected_movie)
        for r in results:
            m = r["m"]
            d = r["d"]
            a = r["a"]

            add_node(m["title"], "Movie")

            if d:
                add_node(d["name"], "Person")
                links.append({"source": d["name"], "target": m["title"], "type": "DIRECTED"})

            if a:
                add_node(a["name"], "Person")
                links.append({"source": a["name"], "target": m["title"], "type": "ACTED_IN"})

    os.makedirs("exports", exist_ok=True)
    with open("exports/graph.json", "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "links": links}, f, indent=2, ensure_ascii=False)

    print("✅ graph.json oluşturuldu: exports/graph.json")


def menu():
    print("""
=== MovieGraphPy ===
1) Film Ara
2) Film Detayı Göster
3) Seçili Film için graph.json Oluştur
4) Çıkış
""")


if not connect_db():
    print("❌ Neo4j bağlantısı kurulamadı.")
    exit()

while True:
    menu()
    secim = input("Seçim: ")

    if secim == "1":
        film_ara()
    elif secim == "2":
        film_detay()
    elif secim == "3":
        graph_json_olustur()
    elif secim == "4":
        print("👋 Çıkılıyor...")
        break
    else:
        print("⚠ Geçersiz seçim.")
