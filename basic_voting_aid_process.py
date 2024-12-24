import basic_gpt
import query_data
import util


def main():
    parties = ["afd", "bsw", "fdp", "gruene", "linke", "spd", "union"]
    max_answer_length = 100
    political_position = input("Please explain you're political positions:\n")
    if not political_position:
        political_position = "Für mich ist der Zugang zu einem starken Gesundheitssystem ein Grundpfeiler einer gerechten Gesellschaft. Jeder Mensch sollte unabhängig von Einkommen oder Wohnort eine qualitativ hochwertige medizinische Versorgung erhalten. Daher halte ich es für notwendig, dass die Politik stärker in öffentliche Gesundheitsstrukturen investiert und den Zugang zu Präventionsmaßnahmen wie Impfungen oder regelmäßigen Untersuchungen erleichtert. Besonders wichtig ist mir hierbei auch die mentale Gesundheit, die oft vernachlässigt wird und dringend mehr Aufmerksamkeit erfordert. Bildung ist für mich das wichtigste Mittel, um Chancengleichheit zu schaffen. Ein freier und gleicher Zugang zu Bildung sollte für alle Menschen selbstverständlich sein, angefangen bei der frühkindlichen Förderung bis hin zu lebenslangem Lernen. Ich glaube, dass wir dringend mehr in Schulen, Lehrpersonal und digitale Infrastruktur investieren müssen, um sicherzustellen, dass Kinder und Jugendliche die bestmögliche Ausbildung erhalten, unabhängig von ihrem sozialen Hintergrund. Ein weiteres Thema, das mir wichtig ist, ist der öffentliche Verkehr. Ich bin der Überzeugung, dass eine bessere Infrastruktur im Nah- und Fernverkehr nicht nur unsere Lebensqualität verbessert, sondern auch die Umwelt schützt. Der Ausbau von Schienenverkehr und emissionsfreien Verkehrsmitteln sollte daher im Mittelpunkt einer nachhaltigen Verkehrspolitik stehen. Gleichzeitig müssen Tickets erschwinglicher werden, um den öffentlichen Verkehr für alle attraktiv zu machen."

    role = ("Erstelle eine Liste der zentralen Themengebiete, die in diesen politischen Positionen behandelt werden. "
            "Die Themengebiete sollten abstrakt und allgemein gehalten sein, ohne in spezifische Unterpunkte zu "
            "zerfallen. Berücksichtige alle Hauptthemen, die im Text angesprochen werden. "
            "Jedes Thema soll gleich wichtig sein, und es soll keine Überschneidungen geben. "
            "Hier sind Beispiele, wie die Themengebiete aussehen könnten:"
            "\nBeispiel 1: Klimaschutz, Soziale Gerechtigkeit, Digitalisierung"
            "\nBeispiel 2: Bildungspolitik, Wirtschaftspolitik, Gesundheitssystem"
            "Die Themen sollten durch Kommas getrennt werden."
            "Nutze diese Struktur, um die Themen im folgenden Text zu identifizieren.")
    topics_text = basic_gpt.ask_gpt(political_position, role)
    # Split the topics_text into individual topics
    topics = topics_text.split(", ")

    role = ("Fasse die politischen Positionen zu dem Thema zusammen. "
            "Gliedere die Meinungen in Stichpunkten. Beziehe dich ausschließlich auf die politischen Positionen. "
            "Achte darauf, dass es sich nicht mit den anderen Themen überschneidet (angegeben als andere Themen). "
            "Gebe Stichpunkte direkt untereinander an ohne leere Zeilen. "
            "Interpretiere die politischen Positionen nicht, sondern fasse sie nur zusammen. "
            "Sollte es keine Meinung zu dem Thema geben oder wenn es nicht klar ist, was das Thema bedeutet, "
            "dann antworte ausschließlich mit 'None'. "
            )




    position_texts = []
    for topic in topics:
        prompt = ("Thema: " + topic + "\n Politische Position" + political_position +
                  "\nAndere Themen: " + ", ".join([t for t in topics if t != topic]))
        position_text = basic_gpt.ask_gpt(prompt, role)
        position_text = "Thema: " + topic + "\n Politische Position" + position_text
        position_texts.append(position_text)

    # User evaluation of party positions

    final_score = {}
    for position_text in position_texts:
        prompt_template = \
        """ Hier ist eine politische Position zu einem Thema: {question}
        ---
        Wie eng entspricht die Meinung der Partei im Kontext? Bewerte von 0-5!
        {context}
        """

        role= (f"Wie eng entspricht die Meinung dem Kontext? Antworte in {max_answer_length} Zeichen oder weniger "
               f"und bewerte von 0-5. 0 bedeutet keine Übereinstimmung. 5 bedeutet volle Übereinstimmung. "
               f"Antworte bitte im folgenden Format:\n"
               f"Antwort: <detaillierte Antwort>\n"
               f"Bewertung: <Zahl>\n"
               f"Sollte der Context keine Antwort auf die Frage bereitstellen, dann antworte ausschließlich mit: 'None'.")

        for party in parties:
            chroma_dir = f"data/{party}/chroma"

            response, context = query_data.query_rag(position_text, chroma_dir, role, prompt_template)

            if response == "None":
                print(f"Die {party} hat keine Meinung zu dem Thema {topic}.")
                if party not in final_score:
                    final_score[party] = 0
                continue

            detailed_answer, rating = split_response(response)

            print(f"Die {party} ist in dem Thema {topic}, {rating}/5 an deiner Meinung."
                  f"\nDetaillierte Antwort:"
                  f"\n{detailed_answer}\n\n")
            if party not in final_score:
                final_score[party] = 0
            final_score[party] += int(rating)

    print("\n\nDie Parteien haben folgende Bewertungen zu deinen politischen Positionen:")
    for party, score in final_score.items():
        print(f"{party}: {score / len(topics)}")

def split_response(response):
    # Split the response into detailed answer and rating
    parts = response.split("\nBewertung: ")
    detailed_answer = parts[0].replace("Antwort: ", "").strip()
    rating = parts[1].strip() if len(parts) > 1 else None
    return detailed_answer, rating

if __name__ == "__main__":
    main()