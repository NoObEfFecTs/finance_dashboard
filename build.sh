function do_build {
    docker build -t cost_ui .
}

function do_run {
    docker run \
	--rm -it \
	-d \
	 -p 8050:8050 \
	 --name=cost_ui \
	-v /home/pi/projects/finance_dashboard/conf.json:/app/conf.json \
	 cost_ui
}

task=$1
shift
do_$task $*
