source "$HOME/.bashrc"
conda activate mlfinlab_env

export PYTHONPATH="/app"
# pytest
conda run --no-capture-output -n mlfinlab_env pytest -v --junitxml=test-results.xml
