from services.deal_memory import recall_memory, retain_memory


class PatternMiner:
    """Lightweight pattern discovery from stored deal outcomes."""

    def __init__(self):
        self.agent_name = "Pattern Miner"

    async def analyze_won_deals(self):
        return await recall_memory("won deal success", top_k=20)

    async def analyze_lost_deals(self):
        return await recall_memory("lost deal failure", top_k=20)

    async def discover_patterns(self):
        won = await self.analyze_won_deals()
        lost = await self.analyze_lost_deals()
        return {
            "won_deals": won,
            "lost_deals": lost,
            "patterns": self._extract_patterns(won, lost),
        }

    @staticmethod
    def _extract_patterns(won, lost):
        def tokens(items):
            text = " ".join(str(x.get("content", x)) for x in items).lower()
            return {w for w in text.split() if len(w) >= 5}

        w, l = tokens(won), tokens(lost)
        return sorted(w & l)[:20]

    async def generate_insights(self):
        result = await self.discover_patterns()
        return {
            "patterns": result["patterns"],
            "insight": (
                "Patterns are based on terms shared by recorded won/lost memories; "
                "treat this as exploratory evidence, not a statistical win-rate estimate."
            ),
        }

    async def update_playbook(self):
        insights = await self.generate_insights()
        await retain_memory(
            f"Generated playbook insights: {insights}",
            metadata={"type": "playbook"},
        )
        return insights

    async def run(self):
        return await self.generate_insights()
