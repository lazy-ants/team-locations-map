docker-compose up -d --build
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm install'
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm run build:ssr'
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm run serve:ssr'
