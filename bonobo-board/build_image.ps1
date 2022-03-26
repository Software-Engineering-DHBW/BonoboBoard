
param (
    [switch]$d = $false,
    [switch]$a = $false
)
$FAIL = 1
$SUCCESS = 0

if(($a -and $d) -or (!$a -and !$d)){
    Write-Error "Wrong usage of build_image.ps1"
    echo "Usage: .\build_image.ps1 [-a|-d]"
    echo "You have to use at least one flag."
    echo "  -a : build all images (recommended)"
    echo "  -d : only build django"
    echo ""
    exit $FAIL
}

function exit_on_error {
    if($lastExitCode -ne 0){
        Write-Error "An error appeared, aborting image creation"
        exit $FAIL
    }
}

if($a){
    docker build -t python_bonobo:latest -f Dockerfile.base --no-cache .
    exit_on_error
}
docker build -t bonobo_board:latest -f Dockerfile.django --no-cache .
exit_on_error

exit $SUCCESS