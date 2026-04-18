"""
Content Analyzer Capability
===========================

任意内容结构化拆解: 自动识别内容类型，选择对应拆解策略。
支持文学名著、数学教材、科学教材、语言教材、社科教材、自定义内容。
"""

from __future__ import annotations

from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus

CONTENT_TYPES = {
    "literature": "文学名著/语文",
    "math": "数学教材",
    "science": "科学教材(物理/化学/生物)",
    "language": "语言教材(英语等)",
    "social": "社科教材(历史/地理/政治)",
    "custom": "自定义内容",
}

ANALYSIS_TEMPLATES = {
    "literature": [
        "extract_chapters",
        "build_characters",
        "extract_themes",
        "identify_writing_techniques",
        "mark_exam_points",
    ],
    "math": [
        "extract_concepts",
        "extract_formulas",
        "analyze_examples",
        "identify_prerequisite_chain",
        "mark_exam_points",
    ],
    "science": [
        "extract_concepts",
        "identify_experiments",
        "extract_formulas",
        "build_application_map",
        "mark_exam_points",
    ],
    "language": [
        "extract_vocabulary",
        "extract_grammar",
        "analyze_texts",
        "identify_listening_points",
        "mark_exam_points",
    ],
    "social": [
        "extract_timeline",
        "extract_key_events",
        "extract_figures",
        "analyze_causality",
        "mark_exam_points",
    ],
    "custom": [
        "detect_content_type",
        "auto_extract_structure",
        "extract_key_points",
        "build_knowledge_graph",
    ],
}


class ContentAnalyzerCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="content_analyzer",
        description="Analyze any content into structured components with type-aware strategy.",
        stages=[
            "detecting_type",
            "extracting_structure",
            "building_knowledge_graph",
            "marking_exam_points",
            "generating_summary",
        ],
        tools_used=["rag"],
        cli_aliases=["analyze"],
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        async with stream.stage("detecting_type", source=self.manifest.name):
            content_type = await self._detect_content_type(context)

        async with stream.stage("extracting_structure", source=self.manifest.name):
            template = ANALYSIS_TEMPLATES.get(content_type, ANALYSIS_TEMPLATES["custom"])
            structure = await self._run_template(context, content_type, template)

        async with stream.stage("building_knowledge_graph", source=self.manifest.name):
            graph = await self._build_knowledge_graph(context, content_type, structure)

        async with stream.stage("marking_exam_points", source=self.manifest.name):
            exam_points = await self._mark_exam_points(context, content_type, structure)

        async with stream.stage("generating_summary", source=self.manifest.name):
            summary = await self._generate_summary(
                context, content_type, structure, graph, exam_points
            )

    async def _detect_content_type(self, context: UnifiedContext) -> str:
        """Use LLM to detect content type from uploaded material."""
        # TODO: prompt-based classification
        return "custom"

    async def _run_template(self, context: UnifiedContext, content_type: str, template: list) -> dict:
        """Run the appropriate analysis template for the content type."""
        results = {}
        for step in template:
            results[step] = {}
        return results

    async def _build_knowledge_graph(self, context: UnifiedContext, content_type: str, structure: dict) -> dict:
        """Build type-appropriate knowledge graph."""
        return {}

    async def _mark_exam_points(self, context: UnifiedContext, content_type: str, structure: dict) -> dict:
        """Mark exam focus areas based on content type."""
        return {}

    async def _generate_summary(self, context: UnifiedContext, **kwargs) -> dict:
        """Generate analysis summary for the user."""
        return {}
