FROM python:3.12-slim

# Set up a new user named "user" with user ID 1000
# Hugging Face Spaces require running as a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory to the user's home directory
WORKDIR /home/user/app

# Copy the requirements file and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the application files (model, api, dashboard)
COPY --chown=user . .

# Expose port 7860 (Hugging Face Spaces default port)
EXPOSE 7860
EXPOSE 8000

# Run our unified launcher script
CMD ["python", "run.py"]
