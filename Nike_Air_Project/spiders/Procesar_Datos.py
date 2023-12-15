import subprocess

comandos = [
    # "scrapy crawl vans -o Vans.json -t json",
    # "scrapy crawl Adidas -o Adidas_dataset.json -t json",
    # "scrapy crawl Zapatillas_Nike_Air -o Nike_dataset.json -t json",
    # "scrapy crawl Zapatillas_Puma -o Puma_dataset.json -t json",
    "scrapy crawl Zapatillas_Reebok -o Reebok_dataset.json -t json",
    "scrapy crawl Under_Armour -o Under_Armour_dataset.json -t json"
]

for comando in comandos:
    subprocess.run(comando, shell=True)