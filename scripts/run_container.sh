sudo docker run \
	-p9000:9000 \
	-v"$(pwd)/notebooks:/notebooks" \
	-v"$(pwd):/app" \
	-e MLFINLAB_API_KEY="$MLFINLAB_API_KEY" \
	-it qml:latest

