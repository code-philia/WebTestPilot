INSERT INTO categories.logs VALUES (1, '2025-10-09 16:14:05.905215', 2, 'Content', 'simple', 'Event created: "Lecture"', '{"ID": 1, "Type": "Lecture"}', '{}', 0, 2, 1);

INSERT INTO categories.logs VALUES (2, '2025-10-09 16:14:07.522528', 2, 'Content', 'simple', 'Event created: "Meeting"', '{"ID": 2, "Type": "Meeting"}', '{}', 0, 2, 1);

INSERT INTO categories.logs VALUES (3, '2025-10-09 16:14:09.164951', 2, 'Content', 'simple', 'Event created: "Conference"', '{"ID": 3, "Type": "Conference"}', '{}', 0, 2, 1);

INSERT INTO events.events VALUES (1, false, false, 1, 0, NULL, NULL, NULL, '', '2025-10-09 16:14:05.861732', '2025-10-10 07:00:00', '2025-10-10 09:00:00', 'Europe/Zurich', 1, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Lecture', '', NULL, NULL, 'Venue', 'Room', '', 0, '', '');

INSERT INTO events.events VALUES (2, false, false, 1, 0, NULL, NULL, NULL, '', '2025-10-09 16:14:07.483091', '2025-10-10 07:00:00', '2040-10-10 11:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Meeting', '', NULL, NULL, 'Venue', 'Room', '', 0, '', '');

INSERT INTO events.events VALUES (3, false, false, 1, 0, NULL, NULL, NULL, '', '2025-10-09 16:14:09.150056', '2025-10-10 07:00:00', '2040-10-10 11:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Conference', '', NULL, NULL, 'Venue', 'Room', '', 0, '', '');

INSERT INTO events.logs VALUES (1, '2025-10-09 16:14:05.906477', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 1, 1, 1);

INSERT INTO events.logs VALUES (2, '2025-10-09 16:14:07.523574', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 2, 1, 1);

INSERT INTO events.logs VALUES (3, '2025-10-09 16:14:09.165356', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 3, 1, 1);

INSERT INTO events.principals VALUES (false, true, '{}', 1, 1, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO events.principals VALUES (false, true, '{}', 2, 2, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO events.principals VALUES (false, true, '{}', 3, 3, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO events.settings VALUES (1, 'layout', 'timetable_theme', '"lecture"', 1);

INSERT INTO events.settings VALUES (2, 'layout', 'timetable_theme', '"standard"', 2);

INSERT INTO events.settings VALUES (3, 'contributions', 'published', 'false', 3);

SELECT pg_catalog.setval('categories.logs_id_seq', 3, true);

SELECT pg_catalog.setval('events.events_id_seq', 3, true);

SELECT pg_catalog.setval('events.logs_id_seq', 3, true);

SELECT pg_catalog.setval('events.principals_id_seq', 3, true);

SELECT pg_catalog.setval('events.settings_id_seq', 3, true);

