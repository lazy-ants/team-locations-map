# Team-locations-map frontend application
Based on [Angular Universal: server-side rendering](https://github.com/lazy-ants/angular-universal/) - commit [55fc1e4f140fabff2bb8256fa5936ec77e26803d](https://github.com/lazy-ants/angular-universal/commit/55fc1e4f140fabff2bb8256fa5936ec77e26803d)

## CLONE REPO

```
git clone git@github.com:lazy-ants/team-locations-map.git
cd team-locations-map
```

## CREATE APP CONFIG FILES

```
cp docker/nginx/nginx.conf.dist docker/nginx/nginx.conf
cp docker-compose.override.yml.dist docker-compose.override.yml
cp project/api/app.config.json.dist project/api/app.config.json
cp project/api/db.config.json.dist project/api/db.config.json
```

## BUILD APPLICATION

- in dev mode

```
docker-compose up -d --build
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm install'
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm start'
```

- in prod mode (bash deploy.sh as quick solution)

```
docker-compose up -d --build
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm install'
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm run build:ssr'
docker exec -ti angular-universal_nodejs bash -c 'cd application && npm run serve:ssr'
```
