import base64
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

from app.config import Settings


class StableDiffusionClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def healthcheck(self) -> bool:
        try:
            response = requests.get(f"{self.settings.sd_base_url.rstrip('/')}/sdapi/v1/options", timeout=5)
            return response.ok
        except requests.RequestException:
            return False

    def txt2img(self, prompt: str, output_path: Path, seed: Optional[int] = None) -> Path:
        payload = {
            "prompt": prompt,
            "negative_prompt": self.settings.sd_negative_prompt,
            "steps": self.settings.sd_steps,
            "cfg_scale": self.settings.sd_cfg_scale,
            "width": self.settings.sd_width,
            "height": self.settings.sd_height,
            "sampler_name": self.settings.sd_sampler,
            "batch_size": 1,
            "n_iter": 1,
            "restore_faces": False,
            "tiling": False,
            "enable_hr": False,
        }
        if seed is not None:
            payload["seed"] = seed

        url = f"{self.settings.sd_base_url.rstrip('/')}/sdapi/v1/txt2img"
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()

        data = response.json()
        if not data.get("images"):
            raise RuntimeError("Stable Diffusion nao retornou imagens")

        image_data = data["images"][0]
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        return output_path
