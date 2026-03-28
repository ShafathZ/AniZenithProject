FROM python:3.12.3-slim

# Copy frontend files and folders
# echo -e "=== Copying frontend files to VM ==="
# "${SCP_BASE[@]}" -r static/ templates/ frontend_app.py requirements.txt \
#  "$FRONTEND_USER@$FRONTEND_HOST:~/$FRONTEND_ROOT_FOLDER/"

# TODO: add pemithus folder

# COPY src/frontend.py /app/src/
COPY frontend/ /anizenith_frontend/

WORKDIR /anizenith_frontend

RUN pip install -r frontend/requirements.txt

# TODO: add permethius

EXPOSE 7860
# EXPOSE 9090

ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

CMD ["python", "src/frontend.py"]
