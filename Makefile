.PHONY: test
test:
	@docker-compose down
	@docker-compose up -d database
	@docker-compose exec database bash -c "\
		sleep 2 && \
		psql --user=postgres -c \"create database tin;\" \
	"
	@docker-compose run app bash -c "\
		python -m tin -c /app/conf/config.json -i && \
		python -m tin -c /app/conf/config.json --add-superuser \
	"
	@docker-compose run -u root app bash -c "\
		set -x && \
		bash -c \"sleep 1; pytest; pkill coverage\" & \
		coverage run -m tin -c /app/conf/config.json --ssl --start\
	"
