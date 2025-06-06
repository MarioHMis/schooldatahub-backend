from aiohttp import web
from .schools import get_schools, create_school, get_school_by_id

async def handle_ping(request):
    return web.json_response({"message": "pong"})

def setup_routes(app):
    app.router.add_get("/ping", handle_ping)
    app.router.add_get("/schools", get_schools)
    app.router.add_post("/schools", create_school)
    app.router.add_get("/schools/{id}", get_school_by_id)




