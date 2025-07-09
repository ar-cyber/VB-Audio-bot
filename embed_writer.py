import json

filename = "licensehelp"

jsons = {
    "embed": {
        "title": "License support",
        "description": """We do not handle any support/questions about licenses being malformed or any enquires about licenses. Please contact us by the webshop contact form if you wish to enquire about a license: https://shop.vb-audio.com/en/contact-us. """,
    }
}

with open(f'cogs/embed/{filename}.json', 'w') as fp:
    json.dump(jsons, fp)