import json
import re
from typing import Any, Dict

import requests

from app.config import Settings
from app.models import CarouselPlan, SlidePlan


SYSTEM_PROMPT = """
Voce e um estrategista de conteudo para carrosseis de Instagram.
Responda sempre em JSON valido, sem markdown e sem comentarios.
Crie um carrossel de exatamente 5 cards.
O conteudo precisa ser curto, forte, legivel em tela de celular e com promessa clara.
A imagem de fundo sera gerada por Stable Diffusion, entao os prompts visuais devem descrever cena, objetos, luz, ambiente e composicao, mas nunca pedir texto dentro da imagem.
""".strip()


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _fallback_plan(topic: str, audience: str, tone: str, style_hint: str, brand_name: str) -> CarouselPlan:
    base_visual = style_hint or "fundo fotografico realista relacionado ao tema, luz cinematica, composicao limpa"
    return CarouselPlan(
        title=topic[:70],
        subtitle="Um guia rapido em 5 pontos",
        palette=["#111827", "#F97316", "#F9FAFB", "#0F766E", "#FDE68A"],
        visual_style=f"{base_visual}, editorial premium, alto contraste, sem texto na imagem",
        slides=[
            SlidePlan(
                index=1,
                headline=topic[:58],
                body="O erro quase nunca esta no detalhe obvio. Esta no processo.",
                image_prompt=f"{base_visual}, abertura impactante, objeto principal em destaque, cinematic light",
            ),
            SlidePlan(
                index=2,
                headline="1. Comecar sem contexto",
                body="Antes de agir, entenda o cenario. Sem contexto, voce resolve o problema errado.",
                image_prompt=f"{base_visual}, pessoa analisando uma situacao, mesa organizada, luz lateral",
            ),
            SlidePlan(
                index=3,
                headline="2. Ignorar o padrao",
                body="Um caso isolado engana. O padrao mostra onde esta a causa real.",
                image_prompt=f"{base_visual}, padroes visuais, repeticao organizada, perspectiva limpa",
            ),
            SlidePlan(
                index=4,
                headline="3. Querer atalhos demais",
                body="Atalho bom reduz trabalho. Atalho ruim cria retrabalho e dor de cabeca.",
                image_prompt=f"{base_visual}, caminho dividido, contraste entre ordem e caos, profundidade de campo",
            ),
            SlidePlan(
                index=5,
                headline="Salve isso antes de esquecer",
                body=f"Use como checklist na proxima vez. {brand_name}".strip(),
                image_prompt=f"{base_visual}, fechamento memoravel, ambiente premium, luz quente, composicao minimalista",
            ),
        ],
    )


class LLMPlanner:
    def __init__(self, settings: Settings):
        self.settings = settings

    def build_plan(self, topic: str, audience: str, tone: str, style_hint: str = "", brand_name: str = "") -> CarouselPlan:
        provider = self.settings.llm_provider.lower().strip()
        if provider == "ollama":
            try:
                return self._from_ollama(topic, audience, tone, style_hint, brand_name)
            except Exception:
                return _fallback_plan(topic, audience, tone, style_hint, brand_name)
        if provider == "openai_compatible":
            try:
                return self._from_openai_compatible(topic, audience, tone, style_hint, brand_name)
            except Exception:
                return _fallback_plan(topic, audience, tone, style_hint, brand_name)
        return _fallback_plan(topic, audience, tone, style_hint, brand_name)

    def _user_prompt(self, topic: str, audience: str, tone: str, style_hint: str, brand_name: str) -> str:
        return f"""
Tema: {topic}
Publico: {audience}
Tom: {tone}
Marca: {brand_name or self.settings.default_brand_name}
Direcao visual extra: {style_hint or self.settings.default_style}

Gere JSON neste formato exato:
{{
  "title": "titulo geral",
  "subtitle": "subtitulo curto",
  "palette": ["#111827", "#F97316", "#F9FAFB", "#0F766E", "#FDE68A"],
  "visual_style": "descricao visual consistente para todos os cards, sem texto na imagem",
  "slides": [
    {{"index": 1, "headline": "max 58 caracteres", "body": "max 130 caracteres", "image_prompt": "prompt visual sem texto"}},
    {{"index": 2, "headline": "max 58 caracteres", "body": "max 130 caracteres", "image_prompt": "prompt visual sem texto"}},
    {{"index": 3, "headline": "max 58 caracteres", "body": "max 130 caracteres", "image_prompt": "prompt visual sem texto"}},
    {{"index": 4, "headline": "max 58 caracteres", "body": "max 130 caracteres", "image_prompt": "prompt visual sem texto"}},
    {{"index": 5, "headline": "max 58 caracteres", "body": "max 130 caracteres", "image_prompt": "prompt visual sem texto"}}
  ]
}}
""".strip()

    def _validate(self, payload: Dict[str, Any], topic: str, audience: str, tone: str, style_hint: str, brand_name: str) -> CarouselPlan:
        plan = CarouselPlan.model_validate(payload)
        if len(plan.slides) != 5:
            return _fallback_plan(topic, audience, tone, style_hint, brand_name)
        return plan

    def _from_ollama(self, topic: str, audience: str, tone: str, style_hint: str, brand_name: str) -> CarouselPlan:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        response = requests.post(
            url,
            json={
                "model": self.settings.ollama_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self._user_prompt(topic, audience, tone, style_hint, brand_name)},
                ],
                "options": {"temperature": 0.45, "top_p": 0.9},
            },
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return self._validate(_extract_json(content), topic, audience, tone, style_hint, brand_name)

    def _from_openai_compatible(self, topic: str, audience: str, tone: str, style_hint: str, brand_name: str) -> CarouselPlan:
        url = f"{self.settings.openai_compatible_base_url.rstrip('/')}/chat/completions"
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.settings.openai_compatible_api_key}"},
            json={
                "model": self.settings.openai_compatible_model,
                "temperature": 0.45,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self._user_prompt(topic, audience, tone, style_hint, brand_name)},
                ],
            },
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._validate(_extract_json(content), topic, audience, tone, style_hint, brand_name)
