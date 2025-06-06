from aiohttp import web
from .schools import get_schools, create_school, get_school_by_id, update_school, delete_school, enrich_school

async def handle_ping(request):
    return web.json_response({"message": "pong"})

def setup_routes(app):
    app.router.add_get("/ping", handle_ping)
    app.router.add_get("/schools", get_schools)
    app.router.add_post("/schools", create_school)
    app.router.add_get("/schools/{id}", get_school_by_id)
    app.router.add_put("/schools/{id}", update_school)
    app.router.add_delete("/schools/{id}", delete_school)
    app.router.add_post("/schools/{id}/enrich", enrich_school)

