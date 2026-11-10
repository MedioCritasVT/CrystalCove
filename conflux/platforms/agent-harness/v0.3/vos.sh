#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
image=localhost/vos-harness:0.3
controller=vos_v03_coordinator
services=(message_board_rabbitmq ollama_node_1 ollama_node_2 ollama_node_3 ollama_node_4 open_webui_1 open_webui_2 open_webui_3 open_webui_4)
workers=(vos_v03_worker_1 vos_v03_worker_2 vos_v03_worker_3 vos_v03_worker_4)
for name in ollama open-webui; do
    if podman container exists "$name"; then services+=("$name"); fi
done
start_one() {
    if [[ $(podman inspect --format '{{.State.Running}}' "$1") != true ]]; then podman start "$1"; fi
}
stop_one() {
    if podman container exists "$1"; then
        if [[ $(podman inspect --format '{{.State.Running}}' "$1") == true ]]; then podman stop "$1"; fi
    fi
}
password() {
    if [[ -z ${VOS_RABBIT_PASSWORD:-} ]]; then
        read -r -s -p 'Existing vos_worker RabbitMQ password: ' VOS_RABBIT_PASSWORD
        printf '\n'
    fi
    [[ -n ${VOS_RABBIT_PASSWORD:-} ]] || { echo 'Password cannot be empty.' >&2; exit 1; }
    export VOS_RABBIT_PASSWORD
}
case "${1:-start}" in
    start)
        for name in "${services[@]}"; do
            podman container exists "$name" || { echo "Missing existing service: $name" >&2; exit 1; }
        done
        podman network exists ollama-net || { echo 'Missing ollama-net.' >&2; exit 1; }
        if ! podman image exists "$image"; then podman build -t "$image" -f Containerfile .; fi
        for name in "${workers[@]}" "$controller"; do
            if ! podman container exists "$name"; then password; break; fi
        done
        for name in "${services[@]}"; do start_one "$name"; done
        ready=false
        for attempt in {1..30}; do
            if podman exec message_board_rabbitmq rabbitmq-diagnostics -q check_running >/dev/null 2>&1; then ready=true; break; fi
            sleep 2
        done
        [[ $ready == true ]] || { echo 'RabbitMQ did not become ready.' >&2; exit 1; }
        for node in 1 2 3 4; do
            name="vos_v03_worker_$node"
            if podman container exists "$name"; then start_one "$name"; else
                podman run -d --name "$name" --network ollama-net \
                    -e VOS_RABBIT_PASSWORD -e VOS_MODEL="${VOS_MODEL:-qwen3.5:4b}" \
                    "$image" transport.py worker --node "$node"
            fi
            webui="open_webui_$node"
            if [[ $(podman inspect --format '{{if index .NetworkSettings.Networks "ollama-net"}}yes{{end}}' "$webui") != yes ]]; then
                podman network connect ollama-net "$webui"
            fi
        done
        if podman container exists "$controller"; then start_one "$controller"; else
            podman volume create vos_board_v03 >/dev/null
            podman run -d --name "$controller" --network ollama-net \
                -e VOS_RABBIT_PASSWORD -v vos_board_v03:/data \
                "$image" coordinator.py serve
        fi
        ready=false
        for attempt in {1..20}; do
            if podman exec "$controller" python coordinator.py health >/dev/null 2>&1; then ready=true; break; fi
            sleep 1
        done
        [[ $ready == true ]] || { podman logs --tail 20 "$controller"; echo 'Controller failed to become ready.' >&2; exit 1; }
        for name in "${workers[@]}"; do
            if [[ $(podman inspect --format '{{.State.Running}}' "$name") != true ]]; then
                podman logs --tail 20 "$name"; echo "Worker failed: $name" >&2; exit 1
            fi
        done
        echo 'v0.3 started. Next: replace the Open WebUI Function code using this folder’s openwebui_vos_pipe.py.'
        echo 'Older workers are retained; v0.3 uses separate queues. No model volumes were changed.'
        ;;
    pause)
        stop_one "$controller"
        for name in "${workers[@]}"; do stop_one "$name"; done
        echo 'Only v0.3 services stopped. Older harness and browser services retained.'
        ;;
    stop)
        stop_one "$controller"
        for name in "${workers[@]}" vos_worker_1 vos_harness_1 vos_harness_2 vos_harness_3 vos_harness_4 "${services[@]}"; do stop_one "$name"; done
        echo 'Services stopped. Model, chat, and board volumes retained.'
        ;;
    status)
        for name in "${services[@]}" "${workers[@]}" "$controller"; do
            if podman container exists "$name"; then podman inspect --format '{{.Name}}: {{.State.Status}}' "$name"; else echo "$name: missing"; fi
        done
        ;;
    logs)
        node=${2:-controller}
        if [[ $node == controller ]]; then name=$controller
        elif [[ $node =~ ^[1-4]$ ]]; then name="vos_v03_worker_$node"
        else echo 'Use logs controller or logs 1–4.' >&2; exit 1; fi
        podman logs --tail 60 "$name"
        ;;
    board|receipts)
        mode=notes; [[ $1 == receipts ]] && mode=events
        podman exec "$controller" python coordinator.py "$mode"
        ;;
    ask)
        node=${2:-1}; [[ $node =~ ^[1-4]$ ]] || { echo 'Choose node 1–4.' >&2; exit 1; }
        podman exec "$controller" python coordinator.py ask --node "$node" "${3:-Hello}"
        ;;
    *) echo 'Usage: bash vos.sh {start|stop|pause|status|logs [controller|1-4]|board|receipts|ask NODE "prompt"}' >&2; exit 1 ;;
esac
