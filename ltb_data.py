
import datetime

LTB_TITLES = {
    1: "Der Kolumbusfalter", 2: "Hallo! Hier ist Micky", 3: "Onkel Dagobert schlägt zurück",
    4: "Donald Duck geht in die Luft", 5: "Onkel Dagoberts Schatzsuche", 6: "Micky-Maus-Parade",
    7: "Donald rücklings", 8: "Donald gibt nicht auf", 9: "Micky ist der Größte",
    10: "Donald, der Pechvogel", 11: "Donald in 1000 Nöten", 12: "Micky Maus im Tal der Toten",
    # ... (Ich werde hier eine gekürzte Liste einfügen, um den Rahmen nicht zu sprengen, 
    # aber die Logik bleibt gleich wie in der TS-Version)
    593: "Im Land der Drachen", 594: "Der goldene Taler", 595: "Geheimnisse im Eis",
    596: "Die Welt der Wunder", 597: "Der Fluch der Karibik", 598: "Das Geheimnis der Dinosaurier",
    599: "Der Schatz der Mammuts",
    600: "Das Phantomias-Jubiläum", 601: "Die Rückkehr der Helden", 602: "Das Rätsel der Zeit",
    603: "Der Schatz der Sterne", 604: "Der E-313", 605: "Bullseye für Donald", 606: "Das Phantom der Oper",
    607: "Die Jagd nach dem Glück", 608: "Der Fluch des Pharaos"
}

ANCHOR_2025_VOL = 593
ANCHOR_2025_DATE = datetime.date(2025, 1, 21)

def generate_volumes(count=608):
    volumes = []
    for i in range(1, count + 1):
        diff = i - ANCHOR_2025_VOL
        release_date = ANCHOR_2025_DATE + datetime.timedelta(days=diff * 28)
        
        volumes.append({
            "nr": i,
            "title": LTB_TITLES.get(i, f"LTB Band {i}"),
            "release_date": release_date.isoformat(),
            "is_upcoming": release_date > datetime.date.today()
        })
    return volumes
