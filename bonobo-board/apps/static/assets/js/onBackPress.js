function HandleBackFunctionality() {
    if (window.event) {
        if (event.currentTarget.performance.navigation.type == 2) {
            console.log("back pressed collected")
        }
    }
} 