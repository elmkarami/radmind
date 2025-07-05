
up:
	docker-compose up -d

down:
	docker-compose down

shell:
	docker-compose run --rm api bash

ssh:
	docker exec -it $$(docker-compose ps -q api) /bin/bash

logs:
	docker-compose logs -f

restart:
	docker-compose restart

