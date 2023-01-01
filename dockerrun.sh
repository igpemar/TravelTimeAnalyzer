docker stop tta_db tta_app;
docker rm tta_db tta_app;
docker run --name tta_db -d -p 5433:5431 --network mynetwork -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=travelAnalyzer postgres -p 5431;
docker build -t tta_app ./;
docker run --name tta_app -d --network mynetwork tta_app;

#docker-compose -p tta up --build