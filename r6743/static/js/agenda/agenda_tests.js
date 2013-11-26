// globals needed for tests cases.
var agenda_globals;
function reset_globals() {
    // hack to reach in and manipulate global specifically.
    window.agenda_globals = new AgendaGlobals();
}

test( "hello test", function() {
  ok( 1 == "1", "Passed!" );
});

test( "TimeSlot Create test", function() {
    reset_globals();
    var nts = make_timeslot({"timeslot_id":"123",
                             "room"       :"Regency A",
                             "time"       :"0900",
                             "date"       :"2013-11-04",
                             "domid"      :"regencya_2013-11-04_0900"});
    equal(nts.slot_title(), "id#123 dom:regencya_2013-11-04_0900", "slot_title correct");
});

asyncTest("Load Timeslots", function() {
    reset_globals();
    expect( 1 );     // expect one assertion.

    var ts_promise = load_timeslots("/meeting/83/timeslots.json");
    ts_promise.done(function() {
        equal(Object.keys(agenda_globals.timeslot_byid).length, 179, "179 timeslots loaded");
        start();
    });
});

asyncTest("Load Sessions", function() {
    reset_globals();
    expect( 1 );     // expect one assertion.

    var session_promise = load_sessions("/meeting/83/sessions.json");
    session_promise.done(function() {
        equal(Object.keys(agenda_globals.meeting_objs).length, 145, "145 sessions loaded");
        start();
    });
});

function full_83_setup() {
    reset_globals();
    var ts_promise      = load_timeslots("/meeting/83/timeslots.json");
    var session_promise = load_sessions("/meeting/83/sessions.json");
    var ss_promise      = load_scheduledsessions(ts_promise, session_promise, "/meeting/83/schedule/mtg_83/sessions.json")
    return ss_promise;
}

asyncTest("Load ScheduledSlot", function() {
    expect( 1 );     // expect one assertion.

    var ss_promise = full_83_setup();
    ss_promise.done(function() {
        equal(Object.keys(agenda_globals.slot_objs).length, 150, "150 scheduled sessions loaded");
        start();
    });
});

