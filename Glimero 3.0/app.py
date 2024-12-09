from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import unicodedata

app = Flask(__name__)

# cale catre folderul assets
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)

# cale catre folderul style
@app.route('/style/<path:filename>')
def serve_style(filename):
    return send_from_directory('style', filename)

# cale catre folderul jsFile
@app.route('/jsFile/<path:filename>')
def jsFile(filename):
    return send_from_directory('jsFile', filename)

# extragerea datelor din fisierul json 
with open("sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)


counties = [
    "Alba", "Arad", "Argeș", "Bacău", "Bihor", "Bistrița-Năsăud", "Botoșani", "Brașov", 
    "Brăila", "Buzău", "Caraș-Severin", "Călărași", "Cluj", "Constanța", "Covasna", "Dâmbovița", 
    "Dolj", "Galați", "Giurgiu", "Gorj", "Harghita", "Hunedoara", "Ialomița", "Iași", "Ilfov", 
    "Maramureș", "Mehedinți", "Mureș", "Neamț", "Olt", "Prahova", "Sălaj", "Satu Mare", 
    "Sibiu", "Suceava", "Teleorman", "Timiș", "Tulcea", "Vaslui", "Vâlcea", "Vrancea", "București"
]

# Extract unique categories from JSON
categories = sorted({
    entry["Text"].split("<br>")[2].split(": ")[1].strip() for entry in data
})

# normalizarea textului, ignorare litere mici, mari sau diacritice
def normalize_text(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8').lower()

# Helper function to flatten nested JSON
def flatten_json(entry):
    flat_data = {}
    for key, value in entry.items():
        if isinstance(value, dict):  # Handle nested dictionaries
            for sub_key, sub_value in value.items():
                flat_data[sub_key] = sub_value
        else:
            flat_data[key] = value
    return flat_data



# functie filtrare pentru index.html
def filter_results(name="", county="", category="", min_capacity=None, max_capacity=None):
    results = []
    for entry in data:
        text = entry["Text"]
        
        details = text.split("<br>") 

        try:
            unit_name = text.split("<br>")[1].split(": ")[1]  # numele
            unit_county = text.split("<br>")[9].split(": ")[1]  # judet
            unit_category = text.split("<br>")[2].split(": ")[1]  # categorie
            capacity = int(text.split("<br>")[4].split(": ")[1])  # capacitate
        except (ValueError, IndexError):
            continue

        # aici aplicam filtrele
        if (
            (name.lower() in unit_name.lower() if name else True)
            and (normalize_text(unit_county) == normalize_text(county) if county else True)
            and (unit_category.strip() == category.strip() if category else True)
            and (capacity >= int(min_capacity) if min_capacity else True) 
            and (capacity <= int(max_capacity) if max_capacity else True)
        ):
            
            results.append({
                "name": unit_name,
                "county": unit_county,
                "category": unit_category,
                "capacity": capacity if capacity is not None else "N/A",
                "address": text.split("<br>")[8].split(": ")[1] + ", " + text.split("<br>")[5].split(": ")[1],
                "details": [detail.strip() for detail in details if detail.strip()],
            })
        

    return results



# functie pentru filtrare in map.html 
@app.route("/map_data", methods=["POST"])
def map_data():
    name = request.form.get("name", "")
    county = request.form.get("county", "")
    category = request.form.get("category", "")
    min_capacity = request.form.get("min_capacity", "")
    max_capacity = request.form.get("max_capacity", "")

    filtered_results = []
    for entry in data:
        text = entry["Text"]
        lat, lng = entry.get("Lat"), entry.get("Lng")

        if lat and lng:
            unit_name = text.split("<br>")[1].split(": ")[1]
            unit_county = text.split("<br>")[9].split(": ")[1]
            unit_category = text.split("<br>")[2].split(": ")[1]
            try:
                capacity = int(text.split("<br>")[4].split(": ")[1])
            except (ValueError, IndexError):
                capacity = None

            if (
                (name.lower() in unit_name.lower() if name else True)
                and (normalize_text(unit_county) == normalize_text(county) if county else True)
                and (unit_category.strip() == category.strip() if category else True)
                and (capacity >= int(min_capacity) if min_capacity else True)
                and (capacity <= int(max_capacity) if max_capacity else True)
            ):
                filtered_results.append({
                    "name": unit_name,
                    "county": unit_county,
                    "category": unit_category,
                    "latitude": lat,
                    "longitude": lng
                })

    return jsonify({"results": filtered_results})


# functie pentru autocomplete in bara de cautare
@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("q", "").lower()
    suggestions = []

    # sugestii pe baza introducetii de litere (mai mult de 3) 
    if query and len(query) >= 3:
        suggestions = [
            entry["Text"].split("<br>")[1].split(": ")[1]
            for entry in data
            if query in entry["Text"].split("<br>")[1].split(": ")[1].lower()
        ]

    # returneaza o lista cu sugestii unice
    return jsonify(list(set(suggestions)))






# Index route
@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    filters = {
        "name": "",
        "county": "",
        "category": "",
        "min_capacity": "",
        "max_capacity": ""
    }
    result_count = 0 

    if request.method == "POST":
        filters["name"] = request.form.get("name", "")
        filters["county"] = request.form.get("county", "")
        filters["category"] = request.form.get("category", "")
        filters["min_capacity"] = request.form.get("min_capacity", "")
        filters["max_capacity"] = request.form.get("max_capacity", "")
        
        # aplicare filtre
        results = filter_results(
            name=filters["name"],
            county=filters["county"],
            category=filters["category"],
            min_capacity=filters["min_capacity"],
            max_capacity=filters["max_capacity"]
        )
        result_count = len(results)  # numaram rezultatele gasite
    
    return render_template(
        "index.html", 
        results=results, 
        result_count=result_count, 
        counties=counties, 
        categories=categories, 
        filters=filters
    )



# Map route
@app.route("/map", methods=["GET", "POST"])
def map():
    results = []
    filters = {
        "name": "",
        "county": "",
        "category": "",
        "min_capacity": "",
        "max_capacity": ""
    }
    result_count = 0 

    if request.method == "POST":
        filters["name"] = request.form.get("name", "")
        filters["county"] = request.form.get("county", "")
        filters["category"] = request.form.get("category", "")
        filters["min_capacity"] = request.form.get("min_capacity", "")
        filters["max_capacity"] = request.form.get("max_capacity", "")
        
        results = filter_results(
            name=filters["name"],
            county=filters["county"],
            category=filters["category"],
            min_capacity=filters["min_capacity"],
            max_capacity=filters["max_capacity"]
        )
        result_count = len(results)  # numaram rezultatele
    
    return render_template(
        "map.html", 
        results=results, 
        result_count=result_count, 
        counties=counties, 
        categories=categories, 
        filters=filters
    )

if __name__ == "__main__":
    app.run(debug=True)