# Team-locations-map frontend application [![CircleCI](https://circleci.com/gh/lazy-ants/team-locations-map.svg?style=svg)](https://circleci.com/gh/lazy-ants/team-locations-map)

Onepager map showing location of the team members

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
docker exec -ti angular-universal_nodejs bash -c 'npm install'
docker exec -ti angular-universal_nodejs bash -c 'npm start'
```

- in prod mode (bash deploy.sh as quick solution)

```
docker-compose up -d --build
docker exec -ti angular-universal_nodejs bash -c 'npm install'
docker exec -ti angular-universal_nodejs bash -c 'npm run build:ssr'
docker exec -ti angular-universal_nodejs bash -c 'npm run serve:ssr'
```
