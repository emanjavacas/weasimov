all:
	@if [ -a db_repository ]; then rm -r db_repository; fi;
	@if [ -a weasimov.db ]; then rm -r weasimov.db; fi;

	@python db_create.py;
	@python db_migrate.py;