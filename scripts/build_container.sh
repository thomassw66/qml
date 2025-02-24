sudo docker build \
	--build-arg MLFINLAB_API_KEY="$MLFINLAB_API_KEY" \
	--build-arg REPOSITORY_HANDLER_URL="$REPOSITORY_HANDLER_URL" \
	-t qml:latest \
	.

