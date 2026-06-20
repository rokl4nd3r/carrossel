from pydantic import BaseModel, Field
from typing import List


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Tema do carrossel")
    audience: str = Field(default="publico geral", description="Publico-alvo")
    tone: str = Field(default="direto, util e provocativo", description="Tom do texto")
    brand_name: str = Field(default="", description="Nome opcional da marca")
    style_hint: str = Field(default="", description="Direcao visual opcional")


class SlidePlan(BaseModel):
    index: int
    headline: str
    body: str
    image_prompt: str


class CarouselPlan(BaseModel):
    title: str
    subtitle: str
    palette: List[str]
    visual_style: str
    slides: List[SlidePlan]


class GeneratedCard(BaseModel):
    index: int
    filename: str
    url: str
    headline: str


class GenerateResponse(BaseModel):
    job_id: str
    title: str
    palette: List[str]
    cards: List[GeneratedCard]
