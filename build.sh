name="plotly_ui"

function do_build {
    docker build -t $name .
}

function do_run {
    docker run \
	-d \
	-p 8050:8050 \
	--name=$name \
	--restart=unless-stopped \
	-v $(pwd):/app \
	$name
}

task=$1
shift
do_$task $*
