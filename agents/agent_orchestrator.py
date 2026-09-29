from agents.deal_historian import DealHistorian
from agents.executive_briefer import ExecutiveBriefer
from agents.objection_coach import ObjectionCoach
from agents.pattern_miner import PatternMiner
from agents.risk_predictor import RiskPredictor


class AgentOrchestrator:
    def __init__(self):
        self.deal_historian = DealHistorian()
        self.executive_briefer = ExecutiveBriefer()
        self.objection_coach = ObjectionCoach()
        self.pattern_miner = PatternMiner()
        self.risk_predictor = RiskPredictor()

    async def handle_query(self, query, deal_id):
        text = (query or "").lower().strip()

        if "risk" in text:
            return await self.risk_predictor.run(deal_id)
        if "objection" in text:
            return await self.objection_coach.run(query)
        if "brief" in text:
            return await self.executive_briefer.generate_brief(deal_id)
        if "history" in text:
            return await self.deal_historian.retrieve_history(deal_id)
        return await self.pattern_miner.run()
