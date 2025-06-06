from aiohttp import web
import traceback

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        # Errores tipo 404, 400, etc.
        return web.json_response({"error": ex.reason}, status=ex.status)
    except Exception as ex:
        # Errores no controlados
        traceback.print_exc()
        return web.json_response({"error": "Internal Server Error"}, status=500)
