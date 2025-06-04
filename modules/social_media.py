from datetime import datetime
from openai import OpenAI

def generate_social_media_post(einsatznummer, einsatzstichwort, einsatzmeldung, uhrzeit, datum, ort, einsatzbericht, fahrzeuge, weitere_kraefte, client, use_gpt):
    datum_obj = datetime.strptime(datum, '%Y-%m-%d')
    datum_format = datum_obj.strftime('%d.%m.%Y')
    
    if use_gpt:
        prompt = f"Erstelle einen kurzen Feuerwehr-Einsatzbericht basierend auf diesen Informationen:\n\nEinsatzstichwort: {einsatzstichwort}\nEinsatzmeldung: {einsatzmeldung}\nUhrzeit: {uhrzeit}\nDatum: {datum_format}\nOrt: {ort}\nEinsatzbericht: {einsatzbericht}\nEingesetzte Fahrzeuge: {fahrzeuge}\nWeitere Kräfte: {weitere_kraefte}. Die Eingesetzten Kräfte und Fahrzeuge müssen nicht aufgezählt werden. Keine überschrift, leicht leserlich für Social Media. Kein Bedanken am ende."
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates press releases."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.5,
        )  
        bericht = response.choices[0].message.content
    else:
        bericht = einsatzbericht
    
    post_template = f"""🚒 #Einsatz {einsatznummer}

📟 #{einsatzstichwort} / {einsatzmeldung}
⏰📅 {uhrzeit} Uhr / {datum_format}
📍 {ort}

{bericht}

Eingesetzte Fahrzeuge:
{fahrzeuge}

Weitere Kräfte:
{weitere_kraefte}"""

    return post_template
