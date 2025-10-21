IMAGE_NAME = cartichrono 
CONTAINER_NAME = cartichrono 
PORT = 8889
VERSION = "latest"

activate:
	@echo "Run: source venv/bin/activate"
	@echo "Virtual environment must be activated in your current shell"

install:
	source venv/bin/activate && pip install -r requirements.txt

init:
	python3 -m venv venv

setup: init install
	direnv allow

run:
	python master.py

debug:
	python master.py 2> log.txt

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the container
run-docker:
	docker run -it --rm \
  		--env-file .env \
  		--network host \
  		--dns 8.8.8.8 --dns 8.8.4.4 \
		--name $(CONTAINER_NAME) $(IMAGE_NAME)

# Rebuild (force rebuild without cache)
rebuild:
	docker build --no-cache -t $(IMAGE_NAME) .