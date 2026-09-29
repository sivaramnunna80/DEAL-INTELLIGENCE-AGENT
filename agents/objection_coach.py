from services.deal_memory import recall_memory, retain_memory


class ObjectionCoach:
    """Finds historical responses and produces a practical response template."""

    def __init__(self):
        self.agent_name = "Objection Coach"

    async def analyze_objection(self, objection):
        matches = await self.find_similar_cases(objection)
        return {"objection": objection, "similar_cases": matches}

    async def find_similar_cases(self, objection):
        return await recall_memory(f"objection {objection}", top_k=5)

    async def recommend_response(self, objection):
        cases = await self.find_similar_cases(objection)
        if cases:
            evidence = cases[0].get("content", str(cases[0]))
            response = (
                "Acknowledge the concern, clarify the underlying requirement, "
                f"and use this historical context: {evidence}"
            )
        else:
            response = (
                "Acknowledge the concern, ask one clarifying question, "
                "quantify the business impact, and propose a low-risk next step."
            )
        return {"objection": objection, "response": response, "evidence": cases}

    async def learn_outcome(self, outcome):
        return await retain_memory(
            f"Objection outcome: {outcome}",
            metadata={"type": "objection_outcome"},
        )

    async def run(self, objection="general objection"):
        return await self.recommend_response(objection)
