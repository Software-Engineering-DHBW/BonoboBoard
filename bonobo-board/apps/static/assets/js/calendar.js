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

//gets weekday of a date from timestamp - -1 to start from monday as 0
function getWeekday(ts) {
    var a = new Date(ts);
    return a.getDay() - 1;
}

//get hour from timestamp - Needs to be UTC because of data format
function getHour(ts) {
    var a = new Date(ts);
    return a.getUTCHours();
}

function getMinute(ts) {
    var a = new Date(ts);
    return a.getMinutes();
}

//creates empty lut to be filled with lecture data (2D Array - dimensions are passed)
function createEmptyLut(dimensions) {
    var array = [];

    //Uses recursive call to create 2D - fill with 0
    for (var i = 0; i < dimensions[0]; ++i) {
        array.push(dimensions.length == 1 ? 0 : createEmptyLut(dimensions.slice(1)));
    }

    return array;
}

//return an array of dates for the current week starting on monday
function getDatesOfCurrentWeek(date) {
    var week = new Array();
    // Starting week on monday not on sunday
    if (date.getDay() != 0) {
        date.setDate((date.getDate() - date.getDay() + 1));
    }
    else {
        date.setDate((date.getDate() - 6));
    }
    for (var i = monday; i <= sunday; i++) {
        week.push(
            new Date(date)
        );
        date.setDate(date.getDate() + 1);
    }
    return week;
}

//copied from https://www.delftstack.com/de/howto/javascript/javascript-get-week-number/
function getWeekNumber(headDate) {
    date = new Date(headDate)
    date.setDate(date.getDate() - 1);
    var oneJan = new Date(date.getFullYear(), 0, 1);
    var numberOfDays = Math.floor((date - oneJan) / (24 * 60 * 60 * 1000));
    var weekNum = Math.ceil((date.getDay() + 1 + numberOfDays) / 7) ;
    return weekNum
}

//checks if time is between 7am and 9:45pm and between monday and saturday
function isValidTime(start) {
    timeslot_start = getTimeSlot(start)
    return timeslot_start >= 0 && timeslot_start < 64 && weekday >= monday && weekday < sunday
}

//get duration in timeslots between start and end
function getDuration(start, end) {
    return getTimeSlot(end) - getTimeSlot(start)
}

//get timeslot in lecture table (one slot is one quarter of an hour between 7am and 9:45pm)
function getTimeSlot(time) {
    //-7 --> start at 7am / *4 --> 4 quarters in one hour / minute//15 --> get slot within hour
    return (getHour(time) - 7) * 4 + Math.floor(getMinute(time) / 15)
}

//just for UI --> 10:0 will be shown as 10:00
function changeMinutePresentation(time) {
    return getMinute(time) >= 10 ? getMinute(time) : ('0' + getMinute(time))
}

//creates empty lut and fills it with lecture data (one field for every quarter of an hour between 7am and 9:45pm - 6 days a week)
function createLut(lectureData) {
    let lut = createEmptyLut([64, 6])

    for (let lecture in lectureData) {
        eventName = lectureData[lecture].lecture

        //get start and end timestamp
        start = lectureData[lecture].start
        end = lectureData[lecture].end

        //get duration in quarter hours (for display size)
        duration = getDuration(start, end)

        //get timeslot of event start - events are saved in lut by there start timeslot in the final table
        timeslot_start = getTimeSlot(start)

        weekday = getWeekday(start)

        //just for UI --> 10:0 will be shown as 10:00
        start_min = changeMinutePresentation(start)
        end_min = changeMinutePresentation(end)

        let link = ""
        for (let i = 0; i < lectureLinks.length; i++) {
            if (lectureLinks[i]["lecture"] == eventName) {
                link = lectureLinks[i]["link"]
            }
        }

        //if time is valid, create lecture object and insert into lut
        if (isValidTime(start)) {
            lecture_object = new Lecture(eventName, lectureData[lecture].location, (getHour(start) + ':' + start_min), (getHour(end) + ':' + end_min), duration, link)
            lut[timeslot_start][weekday] = lecture_object
        }
    }
    return lut
}

//add one to start on monday
function isToday(day) {
    return new Date().getDay() == day + 1
}

//function to fill in the correct dates in schedule header. Marks current day as well.
function createHeaderContent(date) {
    let content = ''
    datesOfCurrentWeek = getDatesOfCurrentWeek(date)
    for (let day = monday; day < sunday; day++) {
        content += '<th' + (isToday(day) ? ' class="today"' : '')
            + '>' + dayNames[day] + ', '  //Mo, Di, Mi etc
            + datesOfCurrentWeek[day].getDate() + '.'
            + (datesOfCurrentWeek[day].getMonth() + 1) + '</th>' //plus one --> Jan = 0 in js
    }
    return content
}

function createCalendarBody() {
    //create look up table for lecture data
    let lut = createLut(lectureData)

    let content = ''
    //creates extra row above for cosmetic reason
    for (let day = monday; day < sunday; day++) {
        content += '<td></td>'
    }

    let index = 0
    //create and fill calendar with lectures (from 7am to 9:45pm in quarter hour steps)
    for (let time = 7; time < 22; time = time + 0.25) {
        //fill hour label with :00 if full hour else use minutes instead
        let hour_label = time % 1 == 0 ? (time + ':00') : ''
        content += '<tr><td class="headcol">' + hour_label + '</td>'
        for (let day = monday; day < sunday; day++) {
            if (lut[index][day] != 0) {
                //refactor courseName for correct URL handling
                courseName = lut[index][day].name.replaceAll(" ", "_")
                courseName = courseName.replaceAll("/", "!&!")

                //every single event is populated here
                content += '<td><div class="event" hx-get="/vorlesungsplan/edit_link/' + courseName
                //if link is known, add addidional parameter to link
                let currentLink = lut[index][day].link
                if (currentLink != "") {
                    let tempLink = lut[index][day].link
                    //replace html tokens with custom ones for making them processable
                    tempLink = tempLink.replaceAll("/", "!&!")
                    tempLink = tempLink.replaceAll("?", "!&&!")
                    tempLink = tempLink.replaceAll("#", "!&&&!")
                    tempLink = tempLink.replaceAll("%", "!&&&&!")
                    content += "/" + tempLink
                }

                content += '" hx-target="#dialog" style="height:'
                    + (lut[index][day].duration * 100) + '%;"></label>' //size of event box
                    + lut[index][day].start + '-'
                    + lut[index][day].end + '<br>'
                    + '<b>' + lut[index][day].name + '</b><br>'
                if (lut[index][day].room != "") {
                    content += lut[index][day].room + '<br>'
                }
                if (currentLink != "") {
                    content += '<a id="alink" onclick="event.stopPropagation()" href="https://' + currentLink + '" target="_blank" rel="noopener noreferrer">Zum Kursraum</a>'
                }
                content += '</div></td>'
            }
            else {
                //empty cell if no event at that timeslot
                content += '<td></td>'
            }
        }
        content += '</tr>'
        index++
    }
    return content
}



//creates table of lectures for current day
function getTodaysLectures(lectureData) {
    let currentDay = getWeekday(currentDate)
    //create look up table for lecture data
    let lut = createLut(lectureData)

    let content = ''

    for (let timeslot in lut) {
        if (currentDay == sunday){
            break;
        }

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