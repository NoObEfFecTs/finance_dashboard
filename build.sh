function do_build {
    docker build -t cost_ui .
}

function do_run {
    docker run \
	--rm -it \
	-d \
	-p 8050:8050 \
	--name=cost_ui \
	-v $(pwd):/app \
	cost_ui
}

task=$1
shift
do_$task $*