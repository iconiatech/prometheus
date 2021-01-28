document.addEventListener("DOMContentLoaded", function() {

    /* initialize the external events
    -----------------------------------------------------------------*/

    var containerEl = document.getElementById("external-events");
    new FullCalendar.Draggable(containerEl, {
      itemSelector: ".external-event",
      eventData: function(eventEl) {
        return {
          title: eventEl.innerText.trim()
        }
      }
    });

    var calendarEl = document.getElementById("calendar");

    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
        },
        initialDate: "2020-06-12",
        editable: true,
        droppable: true,
        selectable: true,
        businessHours: true,
        dayMaxEvents: true, // allow "more" link when too many events
        drop: function(arg) {
            // is the "remove after drop" checkbox checked?
            if (document.getElementById("drop-remove").checked) {
              // if so, remove the element from the "Draggable Events" list
              arg.draggedEl.parentNode.removeChild(arg.draggedEl);
            }
        },
        select: function(arg) {
            // var title = prompt("Event Title:");
            // if (title) {
            //   calendar.addEvent({
            //     title: title,
            //     start: arg.start,
            //     end: arg.end,
            //     allDay: arg.allDay
            //   })
            // }
            $("#event-modal").modal("show");
            calendar.unselect()
        },
        eventClick: function(info) {
            alert("Event: " + info.event.title);
        },
        events: [
            {
                title: "All Day Event",
                start: "2020-06-01"
            },
            {
                title: "Long Event",
                start: "2020-06-07",
                end: "2020-06-10",
                display: "background",
                className: "bg-warning"
            },
            {
                groupId: 999,
                title: "Repeating Event",
                start: "2020-06-09T16:00:00"
            },
            {
                groupId: 999,
                title: "Repeating Event",
                start: "2020-06-16T16:00:00"
            },
            {
                title: "Conference",
                start: "2020-06-11",
                end: "2020-06-13",
                className: "bg-success"
            },
            {
                title: "Meeting",
                start: "2020-06-12T10:30:00",
                end: "2020-06-12T12:30:00"
            },
            {
                title: "Lunch",
                start: "2020-06-12T12:00:00"
            },
            {
                title: "Meeting",
                start: "2020-06-12T14:30:00"
            },
            {
                title: "Happy Hour",
                start: "2020-06-12T17:30:00"
            },
            {
                title: "Dinner",
                start: "2020-06-12T20:00:00"
            },
            {
                title: "Birthday Party",
                start: "2020-06-13T07:00:00"
            },
            {
                title: "Click for Google",
                url: "http://google.com/",
                start: "2020-06-28",
                className: "bg-danger"
            }
        ]
    });

    calendar.render();
  });