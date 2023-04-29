name="plotly_ui"

function do_build {
    docker build -t $name .
}

function do_run {
    docker run \
	-d \
	--restart:unless-stopped \
	-p 8050:8050 \
	--name=$name \
	-v $(pwd):/app \
	$name
}

task=$1
shift
do_$task $*