from aiohttp.web import Request

from opsdroid.skill import Skill
from opsdroid.matchers import match_webhook
from opsdroid.events import Message

import logging
import pprint
import os

from .j2_template_engine import load_j2_template_engine

_LOGGER = logging.getLogger(__name__)

class AlertManager(Skill):
    @match_webhook('webhook')
    async def alertmanager(self, event: Request):
        payload = await event.json()
        _LOGGER.debug('payload receiveddd by alertmanager: ' +
                      pprint.pformat(payload))
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        J2_TEMPLATE_ENGINE = load_j2_template_engine(dir_path + '/mattermost.j2')
        
        for alert in payload["alerts"]:
            origin = event.rel_url.query['origin']
            render_payload = {
                'origin': origin
            }
            render_payload.update(alert)
            rendered_alert = J2_TEMPLATE_ENGINE.render(render_payload)
            
            await self.opsdroid.send(Message(
                        target=event.rel_url.query['channel_name'],
                        text=rendered_alert,
                        connector="mattermost")
            )
            matrix = self.opsdroid.get_connector("matrix")
            if matrix:
                await self.opsdroid.send(Message(
                            text=rendered_alert,
                            connector="matrix")
