# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Патчи безопасности ОС поверх базового образа: Trivy нашёл в python:3.12-slim
# HIGH CVE в zlib, которые уже исправлены в Debian, но ещё не попали в тег.
RUN apt-get -o APT::Update::Error-Mode=any update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# Непривилегированный пользователь без shell и домашнего каталога.
RUN addgroup --system app && adduser --system --ingroup app --no-create-home app

# Только runtime-зависимости: pytest и прочий dev-инструментарий в образ не попадает.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код принадлежит root и read-only для пользователя app: RCE не сможет его переписать.
COPY app ./app

USER app

EXPOSE 8000

# Healthcheck без curl/wget в образе — меньше утилит для атакующего.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
