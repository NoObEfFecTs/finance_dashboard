function do_build {
    docker build -t cost_ui .
}

function do_run {
    docker run --rm -it -p 8050:8050 --name=cost_ui cost_ui
}

task=$1
shift
do_$task $*