from services.deal_memory import recall_memory


class RiskPredictor:
    """Rule-based risk detector backed by deal memory."""

    def __init__(self):
        self.agent_name = "Risk Predictor"

    async def identify_risks(self, deal_id):
        memories = await recall_memory(f"Deal ID {deal_id}", top_k=20)
        text = " ".join(str(item.get("content", item)) for item in memories).lower()

        rules = [
            ("No executive sponsor mentioned", ["executive sponsor", "cfo", "ceo", "vp"]),
            ("Budget uncertainty", ["budget not approved", "budget pending", "no budget"]),
            ("Strong competition", ["competitor", "competition", "competing"]),
            ("Security review pending", ["security pending", "security review pending"]),
            ("Timeline risk", ["delayed", "delay", "timeline risk", "deadline at risk"]),
        ]
        risks = []
        for label, keywords in rules:
            if label == "No executive sponsor mentioned":
                present = any(k in text for k in keywords)
                if not present:
                    risks.append({"risk": label, "severity": "medium"})
            elif any(k in text for k in keywords):
                risks.append({"risk": label, "severity": "medium"})
        return {"deal_id": deal_id, "risks": risks, "risk_count": len(risks)}

    async def calculate_risk(self, deal_id):
        result = await self.identify_risks(deal_id)
        count = result["risk_count"]
        score = min(100, count * 20)
        level = "low" if score < 30 else "medium" if score < 60 else "high"
        return {**result, "risk_score": score, "risk_level": level}

    async def run(self, deal_id="unknown"):
        return await self.calculate_risk(deal_id)
