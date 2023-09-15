from aiohttp.web import Request

from opsdroid.skill import Skill
from opsdroid.matchers import match_webhook
from opsdroid.events import Message

import logging
import pprint

_LOGGER = logging.getLogger(__name__)

class AlertManager(Skill):
    @match_webhook('webhook')
    async def alertmanager(self, event: Request):
        payload = await event.json()
        _LOGGER.debug('payload receiveddd by alertmanager: ' +
                      pprint.pformat(payload))

        for alert in payload["alerts"]:
            msg = ""
            if "message" in alert["annotations"]:
                msg = alert["annotations"]["message"]
            elif "description" in alert["annotations"]:
                msg = '''
                :fire: {status} :fire:
                **Started at:** {start}
                '''
                

            await self.opsdroid.send(Message(
                        target=payload["channel_name"],
                        text=str(msg.format(
                            status=alert["status"].upper(),
                            start=alert["startsAt"]))
                        )))
