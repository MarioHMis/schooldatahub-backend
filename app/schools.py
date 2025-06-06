from aiohttp import web

# Simulamos una "base de datos" en memoria
schools_db = [
    {"id": 1, "name": "Escuela Nacional", "city": "CDMX"},
    {"id": 2, "name": "Instituto del Sureste", "city": "Villahermosa"},
    {"id": 3, "name": "Colegio Libre", "city": "Monterrey"}
]

next_id = 4  # ID siguiente a asignar


async def get_schools(request):
    return web.json_response(schools_db)

async def create_school(request):
    global next_id
    try:
        data = await request.json()
        name = data.get("name")
        city = data.get("city")

        if not name or not city:
            return web.json_response(
                {"error": "Missing 'name' or 'city'"}, status=400
            )

        new_school = {
            "id": next_id,
            "name": name,
            "city": city
        }

        schools_db.append(new_school)
        next_id += 1

        return web.json_response(new_school, status=201)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def get_school_by_id(request):
    school_id = request.match_info.get("id")

    if not school_id.isdigit():
        return web.json_response({"error": "Invalid ID"}, status=400)

    school_id = int(school_id)
    for school in schools_db:
        if school["id"] == school_id:
            return web.json_response(school)

    return web.json_response({"error": "School not found"}, status=404)
