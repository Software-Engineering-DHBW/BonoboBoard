/**
 * Every event in vorlesungsplan is represented by a Lecture
 * @param  {String} name  Name of the event.
 * @param  {String} room   Room number of event.
 * @param  {String} start Start time.
 * @param  {String} end  End time.
 * @param  {String} duration  duration of event.
 * @param  {String} link  Link to join event online.
 */
class Lecture {
    constructor(name, room, start, end, duration, link) {
        this.name = name;
        this.room = room;
        this.start = start
        this.end = end
        this.duration = duration
        this.link = link
    }
}