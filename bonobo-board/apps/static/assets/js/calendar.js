dayNames = getDayNames()
monday = getMonday()
sunday = getSunday()

currentDate = new Date();



function getDayNames() {
    return ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa']
}

function getMonday() {
    return 0
}

function getSunday() {
    return 6
}

function getWeekday(ts) {
    var a = new Date(ts);
    return a.getDay() - 1;
}

function getHour(ts) {
    var a = new Date(ts);
    return a.getHours() - 1;
}

function getMinute(ts) {
    var a = new Date(ts);
    return a.getMinutes();
}

function empty_lut(dimensions) {
    var array = [];

    for (var i = 0; i < dimensions[0]; ++i) {
        array.push(dimensions.length == 1 ? 0 : empty_lut(dimensions.slice(1)));
    }
    return array;
}

function dates(current) {
    var week = new Array();
    // Starting Week on Monday not on Sunday
    if (current.getDay() != 0) {
        current.setDate((current.getDate() - current.getDay() + 1));
    }
    else {
        current.setDate((current.getDate() - 6));
    }
    for (var i = 0; i < 7; i++) {
        week.push(
            new Date(current)
        );
        current.setDate(current.getDate() + 1);
    }
    return week;
}

function getWeekNumber() {
    currentDate.setDate(currentDate.getDate() - 1);
    var oneJan = new Date(currentDate.getFullYear(), 0, 1);
    var numberOfDays = Math.floor((currentDate - oneJan) / (24 * 60 * 60 * 1000));
    return Math.ceil((currentDate.getDay() + 1 + numberOfDays) / 7);
}

function isValidTime(start) {
    timeslot_start = getTimeSlot(start)
    return timeslot_start >= 0 && timeslot_start < 64 && weekday >= monday && weekday < sunday
}

function getDuration(start, end) {
    return getTimeSlot(end) - getTimeSlot(start)
}

function getTimeSlot(time) {
    return (getHour(time) - 7) * 4 + Math.floor(getMinute(time) / 15)
}

function changeMinutePresentation(time) {
    return getMinute(time) >= 10 ? getMinute(time) : ('0' + getMinute(time))
}
//comment
function createLut(lectureData) {
    let lut = empty_lut([64, 6])

    for (let lecture in lectureData) {
        start = lectureData[lecture].start
        end = lectureData[lecture].end

        duration = getDuration(start, end)

        timeslot_start = getTimeSlot(start)

        weekday = getWeekday(start)

        //just for UI --> 10:0 will shown as 10:00
        start_min = changeMinutePresentation(start)
        end_min = changeMinutePresentation(end)

        if (isValidTime(start)) {
            lut[timeslot_start][weekday] = new Lecture(lectureData[lecture].lecture, lectureData[lecture].location, (getHour(start) + ':' + start_min), (getHour(end) + ':' + end_min), duration)
        }
    }
    return lut
}

function isToday(day) {
    return new Date().getDay() == day + 1
}

function createHeader(content) {
    for (let day = monday; day < sunday; day++) {
        content += '<th' + (isToday(day) ? ' class="today"' : '') + '>' + dayNames[day] + ', ' + dates(new Date())[day].getDate() + '.' + (dates(new Date())[day].getMonth() + 1) + '</th>'
    }
    return content
}

function createCalendarBody(content) {
    for (let day = monday; day < sunday; day++) {
        content += '<td></td>'
    }
    let index = 0
    //create and fill calendar with lectures
    for (let time = 7; time < 22; time = time + 0.25) {
        let hour_label = time % 1 == 0 ? (time + ':00') : ''
        content += '<tr><td class="headcol">' + hour_label + '</td>'
        for (let day = monday; day < sunday; day++) {
            if (lut[index][day] != 0) {
                courseName = lut[index][day].name.replaceAll(" ","_")
                courseName = courseName.replaceAll("/", "!%&")
                //every single event is populated here
                content += '<td><div class="event" hx-get="/vorlesungsplan/edit_link/' + courseName + '" hx-target="#dialog" style="height:'
                    + (lut[index][day].duration * 100) + '%;"></label>'
                    + lut[index][day].start + '-'
                    + lut[index][day].end + '<br>'
                    + lut[index][day].name + '<br>'
                    + '<b>' + lut[index][day].room + '</b></div></td>'
            }
            else {
                content += '<td></td>'
            }
        }
        content += '</tr>'
        index++
    }
    return content
}

function getTodaysClass(lectureData, content) {
    let currentDay = getWeekday(currentDate)
    //create look up table for lecture data
    let lut = createLut(lectureData)

    console.log(currentDate)

    for (let timeslot in lut) {
        if (lut[timeslot][currentDay] != 0) {
            content += '<tr><td>' + lut[timeslot][currentDay].name + '</td>'
            content += '<td>' + lut[timeslot][currentDay].start + ' - ' + lut[timeslot][currentDay].end + '</td>'

            if (lut[timeslot][currentDay].room == "") {
                content += '<td> - </td></tr>'
            }
            else {
                content += '<td>' + lut[timeslot][currentDay].room + '</td></tr>'
            }

        }
    }
    return content
}