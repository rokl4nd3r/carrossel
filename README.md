# Carrossel MVP

Gerador local de carrossel para Instagram usando IA para estruturar o conteudo e Stable Diffusion local para gerar os fundos.

Este MVP gera 5 imagens em formato 1080x1350, mantendo uma paleta visual e um padrao de layout entre os cards.

## O que tem agora

- Interface web simples para usar pelo navegador ou celular na rede local.
- Backend em FastAPI.
- Integracao com Stable Diffusion Automatic1111 via API `/sdapi/v1/txt2img`.
- Integracao com IA via endpoint OpenAI-compatible ou Ollama.
- Fallback local simples caso a IA nao esteja configurada.
- Renderizacao final com Pillow: fundo gerado + camada escura + texto + numeracao.
- Saida em `output/<job_id>/card_01.png` ate `card_05.png`.

## Requisitos

- Python 3.11+
- Stable Diffusion Automatic1111 rodando com API habilitada.
- Opcional: uma IA OpenAI-compatible, OpenRouter, LM Studio, Ollama ou outro endpoint compativel.

## Como subir o Stable Diffusion com API

No Automatic1111, inicie com:

```bash
webui-user.bat --api --listen
```

Normalmente a API fica em:

```text
http://127.0.0.1:7860
```

Se o backend rodar em outro computador, use o IP do Windows onde esta o SD, por exemplo:

```text
http://192.168.240.20:7860
```

## Instalacao

```bash
git clone https://github.com/rokl4nd3r/carrossel.git
cd carrossel
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

No Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Configuracao

Edite o `.env`:

```env
SD_BASE_URL=http://127.0.0.1:7860
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3.5:9b
```

Para OpenAI-compatible, OpenRouter, LM Studio ou Fireworks:

```env
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_COMPATIBLE_API_KEY=lm-studio
OPENAI_COMPATIBLE_MODEL=qwen/qwen3.5-9b
```

## Rodar

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Abra:

```text
http://localhost:8080
```

No celular, estando na mesma rede:

```text
http://IP_DO_PC:8080
```

## Uso

Digite um tema, por exemplo:

```text
5 erros que pessoas cometem ao limpar teclado mecanico
```

O sistema vai:

1. pedir para a IA criar o roteiro dos 5 cards;
2. manter uma paleta de cor unica;
3. gerar um prompt visual para o Stable Diffusion;
4. gerar 5 fundos;
5. aplicar texto por cima;
6. devolver os links das imagens.

## Roadmap curto

- Escolha de templates visuais.
- Exportar ZIP.
- Historico de carrosseis.
- Upload direto para Instagram quando a etapa de autenticacao estiver definida.
- Scraper/analise de perfis depois do MVP estar validado.
