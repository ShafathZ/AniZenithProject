docker build -t ebprihar/cookiemancer_backend:latest -f backend.dockerfile ../..
docker build -t ebprihar/cookiemancer_frontend:latest -f frontend.dockerfile ../..
docker push ebprihar/cookiemancer_backend:latest
docker push ebprihar/cookiemancer_frontend:latest