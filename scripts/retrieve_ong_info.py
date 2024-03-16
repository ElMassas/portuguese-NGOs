# A segurança social mantém uma lista de todas as IPSS registadas em Portugal mas não parece ser regularmente disponibilizada. Único sito em que encontrei(fora das financças que têm menos informação)
# https://www.seg-social.pt/publicacoes?kw=Listagem+de+Institui%C3%A7%C3%B5es+Particulares+de+Solidariedade+Social+registadas
import json
import pdfplumber
from loguru import logger


# Open the PDF file
def retrieve_info():
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

                    district = row[3]
                    city = row[2]
                    name = row[0]
                    details = [row[4], row[1], row[5]]
                    details_list.append(details)

                    details_list = sorted(details_list, key=lambda x: x[0])

                    if district not in data:
                        data[district] = {}
                    if city not in data[district]:
                        data[district][city] = {}
                    for details in details_list:
                        data[district][city][name] = details

        logger.info(f"Extracted {len(data)} rows from the PDF")
        return data


if __name__ == "__main__":
    data = retrieve_info()
    with open("data/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info("Data saved to data/data.json")
