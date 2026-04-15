"""
Reading Guide Capability
========================

个性化带读计划生成: 根据学生年级/阅读速度/时间安排生成精读计划
"""

from __future__ import annotations

from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus


class ReadingGuideCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="reading_guide",
        description="Generate personalized reading plans with daily tasks, discussion prompts, and comprehension checks.",
        stages=[
            "assessing_reader",
            "generating_plan",
            "creating_daily_tasks",
            "building_discussion_prompts",
        ],
        tools_used=["rag"],
        cli_aliases=["guide"],
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        async with stream.stage("assessing_reader", source=self.manifest.name):
            reader_profile = await self._assess_reader(context)

        async with stream.stage("generating_plan", source=self.manifest.name):
            plan = await self._generate_plan(context, reader_profile)

        async with stream.stage("creating_daily_tasks", source=self.manifest.name):
            daily_tasks = await self._create_daily_tasks(context, plan)

        async with stream.stage("building_discussion_prompts", source=self.manifest.name):
            prompts = await self._build_discussion_prompts(context, plan)

    async def _assess_reader(self, context: UnifiedContext) -> dict:
        """Assess reader's grade level, reading speed, and availability."""
        return {}

    async def _generate_plan(self, context: UnifiedContext, reader_profile: dict) -> dict:
        """Generate a structured reading plan."""
        return {}

    async def _create_daily_tasks(self, context: UnifiedContext, plan: dict) -> dict:
        """Create daily reading tasks with focus areas."""
        return {}

    async def _build_discussion_prompts(self, context: UnifiedContext, plan: dict) -> dict:
        """Build Socratic discussion prompts for each day."""
        return {}
