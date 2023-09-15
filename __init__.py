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
            msg = ""
            if "message" in alert["annotations"]:
                msg = alert["annotations"]["message"]
            elif "description" in alert["annotations"]:
                status=alert["status"].upper()
                start=alert["startsAt"]
                msg = (f":fire: {status} :fire:\n"
                       f"**Started at:** {start}\n")
            render_payload = {}
            render_payload.update(alert)
            rendered_alert = J2_TEMPLATE_ENGINE.render(render_payload)
            
            await self.opsdroid.send(Message(
                        target=payload["channel_name"],
                        text=J2_TEMPLATE_ENGINE.render(rendered_alert),
                        connector="mattermost")
            )
            msg = (f"&#128293; {status} &#128293;\n"
                       f"**Started at:** {start}\n")
            await self.opsdroid.send(Message(str(
                "{status} {name} ({severity}): {message}".
                format(
                    status=alert["status"].upper(),
                    name=alert["labels"]["alertname"],
                    severity=alert["labels"]["severity"].upper(),
                    message=msg)),
                connector="matrix"))
