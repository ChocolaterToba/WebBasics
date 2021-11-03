export PROMETHEUS_MULTIPROC_DIR=metrics_dir
rm -rf metrics_dir
mkdir metrics_dir
gunicorn AskAglicheev.wsgi --daemon &