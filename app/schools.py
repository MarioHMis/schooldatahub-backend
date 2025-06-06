from aiohttp import web
import json
import os

# === Utilidades de persistencia ===

def load_schools_from_file():
    try:
        if not os.path.exists("schools.json"):
            return []
        with open("schools.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading schools.json:", e)
        return []

def save_schools_to_file():
    try:
        with open("schools.json", "w", encoding="utf-8") as f:
            json.dump(schools_db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving schools.json:", e)

# === Datos en memoria cargados desde archivo ===

schools_db = load_schools_from_file()
next_id = max([s["id"] for s in schools_db], default=0) + 1

# === Validación ===

def validate_school_data(data, partial=False):
    if not isinstance(data, dict):
        return False, "Invalid JSON format"

    allowed_keys = {"name", "city"}
    unexpected = set(data.keys()) - allowed_keys
    if unexpected:
        return False, f"Unexpected fields: {', '.join(unexpected)}"

    if not partial:
        if "name" not in data or "city" not in data:
            return False, "Missing 'name' or 'city'"

    for field in ("name", "city"):
        if field in data and not isinstance(data[field], str):
            return False, f"'{field}' must be a string"

    return True, ""

# === Endpoints ===

async def get_schools(request):
    return web.json_response(schools_db)

async def get_school_by_id(request):
    school_id = request.match_info.get("id")

    if not school_id.isdigit():
        return web.json_response({"error": "Invalid ID"}, status=400)

    school_id = int(school_id)
    for school in schools_db:
        if school["id"] == school_id:
            return web.json_response(school)

    return web.json_response({"error": "School not found"}, status=404)

async def create_school(request):
    global next_id
    try:
        data = await request.json()
        is_valid, error = validate_school_data(data)
        if not is_valid:
            return web.json_response({"error": error}, status=400)

        new_school = {
            "id": next_id,
            "name": data["name"],
            "city": data["city"]
        }

        schools_db.append(new_school)
        next_id += 1
        save_schools_to_file()

        return web.json_response(new_school, status=201)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def update_school(request):
    school_id = request.match_info.get("id")

    if not school_id.isdigit():
        return web.json_response({"error": "Invalid ID"}, status=400)

    school_id = int(school_id)

    for school in schools_db:
        if school["id"] == school_id:
            try:
                data = await request.json()
                is_valid, error = validate_school_data(data, partial=True)
                if not is_valid:
                    return web.json_response({"error": error}, status=400)

                name = data.get("name")
                city = data.get("city")

                if name:
                    school["name"] = name
                if city:
                    school["city"] = city

                save_schools_to_file()
                return web.json_response(school)

            except Exception as e:
                return web.json_response({"error": str(e)}, status=500)

    return web.json_response({"error": "School not found"}, status=404)

async def delete_school(request):
    school_id = request.match_info.get("id")

    if not school_id.isdigit():
        return web.json_response({"error": "Invalid ID"}, status=400)

    school_id = int(school_id)

    for index, school in enumerate(schools_db):
        if school["id"] == school_id:
            deleted = schools_db.pop(index)
            save_schools_to_file()
            return web.json_response({"message": "School deleted", "school": deleted})

    return web.json_response({"error": "School not found"}, status=404)


async def enrich_school(request):
    school_id = request.match_info.get("id")

    if not school_id.isdigit():
        return web.json_response({"error": "Invalid ID"}, status=400)

    school_id = int(school_id)

    for school in schools_db:
        if school["id"] == school_id:
            # Normalizar nombre
            school["name"] = school["name"].title()

            # Asignar región educativa basada en ciudad
            city = school["city"].lower()
            region = "Norte" if "monterrey" in city else "Centro" if "cdmx" in city else "Sur"
            school["region"] = region

            save_schools_to_file()
            return web.json_response({"message": "Escuela enriquecida", "school": school})

    return web.json_response({"error": "School not found"}, status=404)
