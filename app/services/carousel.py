import random
import uuid
from pathlib import Path
from typing import List

from app.config import Settings
from app.models import GenerateRequest, GenerateResponse, GeneratedCard
from app.services.llm import LLMPlanner
from app.services.renderer import CardRenderer
from app.services.stable_diffusion import StableDiffusionClient


class CarouselGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.planner = LLMPlanner(settings)
        self.sd = StableDiffusionClient(settings)
        self.renderer = CardRenderer()

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        brand_name = request.brand_name or self.settings.default_brand_name
        job_id = uuid.uuid4().hex[:12]
        job_dir = Path(self.settings.output_dir) / job_id
        raw_dir = job_dir / "raw"
        final_dir = job_dir / "final"
        raw_dir.mkdir(parents=True, exist_ok=True)
        final_dir.mkdir(parents=True, exist_ok=True)

        plan = self.planner.build_plan(
            topic=request.topic,
            audience=request.audience,
            tone=request.tone,
            style_hint=request.style_hint,
            brand_name=brand_name,
        )

        cards: List[GeneratedCard] = []
        base_seed = random.randint(1, 2_000_000_000)

        for slide in plan.slides:
            prompt = self._compose_prompt(plan.visual_style, slide.image_prompt, plan.palette)
            raw_path = raw_dir / f"card_{slide.index:02d}_background.png"
            final_path = final_dir / f"card_{slide.index:02d}.png"

            self.sd.txt2img(prompt=prompt, output_path=raw_path, seed=base_seed + slide.index)
            self.renderer.render(
                background_path=raw_path,
                output_path=final_path,
                index=slide.index,
                total=5,
                title=plan.title,
                headline=slide.headline,
                body=slide.body,
                palette=plan.palette,
                brand_name=brand_name,
            )

            cards.append(
                GeneratedCard(
                    index=slide.index,
                    filename=final_path.name,
                    url=self._public_url(job_id, final_path.name),
                    headline=slide.headline,
                )
            )

        return GenerateResponse(job_id=job_id, title=plan.title, palette=plan.palette, cards=cards)

    def _compose_prompt(self, visual_style: str, slide_prompt: str, palette: List[str]) -> str:
        palette_text = ", ".join(palette[:5])
        return (
            f"{slide_prompt}, {visual_style}, cohesive instagram carousel background, "
            f"consistent color palette {palette_text}, no text, no letters, no logo, "
            f"vertical 4:5 composition, professional social media design background"
        )

    def _public_url(self, job_id: str, filename: str) -> str:
        base = self.settings.public_base_url.rstrip("/")
        path = f"/output/{job_id}/final/{filename}"
        return f"{base}{path}" if base else path
