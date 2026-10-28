FROM python:3.12-slim
WORKDIR /repo
COPY services/api /repo/services/api
RUN pip install --no-cache-dir -r /repo/services/api/requirements.lock && pip install --no-cache-dir --no-deps /repo/services/api
COPY data/manifests /repo/data/manifests
COPY data/fixtures /repo/data/fixtures
COPY pipelines /repo/pipelines
COPY scripts /repo/scripts
WORKDIR /repo/services/api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
