from aiohttp import web
from .const import DOMAIN
from .helper import normalize_value

async def async_setup_api(hass):

    async def handle_post(request):
        data = await request.json()

        node = data.get("node")
        if not node:
            return web.json_response({"error": "missing node"}, status=400)

        store = hass.data[DOMAIN]["store"]

        # normalize values
        clean = {
            k: normalize_value(v)
            for k, v in data.items()
            if k not in ["node", "integration"]
        }

        store.update_node(node, clean)

        # trigger entity update
        if "update_entities" in hass.data[DOMAIN]:
            hass.data[DOMAIN]["update_entities"](node)

        return web.json_response({"ok": True})

    hass.http.register_view(
        web.View
    )

    hass.http.app.router.add_post("/api/extaas_template", handle_post)