# Hugging Face Docker Space - Todo Backend API
# Based on Hugging Face Docker Space guidelines
# Reference: https://huggingface.co/docs/hub/spaces-sdks-docker

FROM python:3.9

# Create non-root user for security (required by Hugging Face)
RUN useradd -m -u 1000 user
USER user

# Set PATH to include pip installations
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements file
COPY --chown=user requirements.txt requirements.txt

# Install dependencies (no cache to reduce image size)
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY --chown=user . /app

# Expose port 7860 (Hugging Face Docker Space standard port)
EXPOSE 7860

# Start FastAPI application
# Must listen on 0.0.0.0:7860 as required by Hugging Face Docker Spaces
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "7860"]
