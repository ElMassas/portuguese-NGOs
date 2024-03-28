# A segurança social mantém uma lista de todas as IPSS registadas em Portugal mas não parece ser regularmente disponibilizada. Único sito em que encontrei(fora das financças que têm menos informação)
# https://www.seg-social.pt/publicacoes?kw=Listagem+de+Institui%C3%A7%C3%B5es+Particulares+de+Solidariedade+Social+registadas
import json
import pdfplumber
from loguru import logger
from time import perf_counter
from typing import Dict, List


# Open the PDF file
def retrieve_info() -> Dict[str, Dict[str, Dict[str, List[str]]]]:
    data = {}
    with pdfplumber.open("data/IPSS.pdf") as pdf:
        for page in pdf.pages:
            # Extract the text from the page
            tables = page.extract_tables()

            for table in tables:
                details_list = []
                for index, row in enumerate(table):
                    if index == 0:
                        continue

                    district = row[3].replace("\n", "") if row[3] is not None else ""
                    city = row[2].replace("\n", "") if row[2] is not None else ""
                    name = row[0].replace("\n", "") if row[0] is not None else ""
                    details = [
                        row[4].replace("\n", "") if row[4] is not None else "",
                        row[1].replace("\n", "") if row[1] is not None else "",
                        row[5].replace("\n", "") if row[5] is not None else "",
                    ]
                    details_list.append(details)

                    details_list = sorted(details_list, key=lambda x: x[0])

                    if district not in data:
                        data[district] = {}
                    if city not in data[district]:
                        data[district][city] = {}
                    for details in details_list:
                        data[district][city][name] = details

        logger.info("Extracted data from the PDF")
        return data


def update_readme(data: Dict[str, Dict[str, Dict[str, List[str]]]]) -> None:
    # Read the existing README file
    with open("RAW_ONGS.md", "r") as f:
        readme = f.read()

    # Prepare the new data
    new_data = ""
    for district, cities in data.items():
        new_data += f"## {district}\n"
        new_data += (
            "| Associação | Concelho | Localização Sede | Tipo  | Ano criação |\n\n"
        )
        new_data += "|---|---|---|---|---|\n\n"

        for city, associations in cities.items():
            for name, details in associations.items():
                new_data += f"| **{name}** | {city} | {details[1]} | {details[0]} | {details[2]} |\n\n"

        new_data += "\n\nDe volta ao [topo](#distritos)\n\n---\n\n"

    # Check if the comments are present in the README
    if "<!--START_SECTION:data-->" in readme and "<!--END_SECTION:data-->" in readme:
        # Replace the data between the comments
        readme = (
            readme.split("<!--START_SECTION:data-->")[0]
            + "<!--START_SECTION:data-->\n"
            + new_data
            + "<!--END_SECTION:data-->"
            + readme.split("<!--END_SECTION:data-->")[1]
        )
    else:
        logger.error("The README file does not contain the required comments.")

    # Write the updated README back to the file
    with open("RAW_ONGS.md", "w") as f:
        f.write(readme)

    logger.info("Updated the README with the extracted data")


if __name__ == "__main__":
    data = retrieve_info()
    with open("data/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info("Data saved to data/data.json")
    # I want to save the data in a file instead of using it just from memory so that it can be used in the future without having to extract it again
    update_readme(data)
