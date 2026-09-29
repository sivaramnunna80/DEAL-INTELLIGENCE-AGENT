from agents.deal_historian import DealHistorian
from agents.executive_briefer import ExecutiveBriefer

import asyncio


async def main():

    historian = DealHistorian()

    await historian.store_memory(
        """
        Acme Health uses Salesforce.

        Budget approved in Q4.

        HubSpot is primary competitor.

        Sarah Johnson is champion.
        """
    )

    briefer = ExecutiveBriefer()

    result = await briefer.generate_brief(
        "DL001"
    )

    print(result)


asyncio.run(main())
