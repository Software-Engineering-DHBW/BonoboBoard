//for firefox we need to catch back click events in order to logout/redirect to login page and kill the session
//if we listen to the event, firefox is prevented from it's own logic.
function HandleBackFunctionality() {
    if (window.event) {
        if (event.currentTarget.performance.navigation.type == 2) {
            console.log("back pressed collected")
        }
    }
} 