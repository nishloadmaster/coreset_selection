FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY backend/ .
# Install zcore_score requirements
COPY zcore_score/requirements.txt ./zcore_requirements.txt
RUN pip install -r zcore_requirements.txt
EXPOSE 8050
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]