docker stop tta_db;
docker rm tta_db
docker run --name tta_db -d -p 5431:5431 -e POSTGRES_PASSWORD=postgres -e POSTGRESS_NAME=travelanalyzer postgres;
docker stop tta_app;
docker rm tta_app
docker build -t tta_app ./;
docker run --name tta_app -d tta_app;