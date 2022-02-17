# add BonoboBoard modules to python module search path

bonobo_module_path="/bonobo-board/modules"

if [ -z "${PYTHONPATH##*${bonobo_module_path}}" ] && [ -z "${PYTHONPATH##*${bonobo_module_path}:*}" ]; then
    export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${bonobo_module_path}"
fi
