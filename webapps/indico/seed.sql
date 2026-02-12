CREATE EXTENSION IF NOT EXISTS pgcrypto;

--
-- Disable all triggers (including FKs) in 'public' schema
--

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema') 
    LOOP
        EXECUTE format('ALTER TABLE %I.%I DISABLE TRIGGER ALL;', r.schemaname, r.tablename);
    END LOOP;
END$$;

--
-- Data for Name: logs; Type: TABLE DATA; Schema: categories; Owner: -
--

INSERT INTO categories.logs VALUES (1, '2026-01-19 02:00:07.963028', 2, 'Content', 'simple', 'Event created: "Lecture 1"', '{"ID": 1, "Type": "Lecture"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (2, '2026-01-19 02:01:39.122341', 2, 'Content', 'simple', 'Event created: "Lecture 2 w/ Survey"', '{"ID": 2, "Type": "Lecture"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (3, '2026-01-19 02:14:49.40372', 2, 'Content', 'simple', 'Event created: "Conference 1"', '{"ID": 3, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (4, '2026-01-19 02:24:15.078037', 2, 'Content', 'simple', 'Event created: "Meeting 1"', '{"ID": 4, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (5, '2026-01-19 02:26:31.645973', 2, 'Content', 'simple', 'Event created: "Weekly Software Architecture Sync"', '{"ID": 5, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (6, '2026-01-19 02:29:53.865332', 2, 'Content', 'simple', 'Event created: "International Conference on AI Testing (IC-AIT 2026)"', '{"ID": 6, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (7, '2026-01-19 02:30:34.795225', 2, 'Content', 'simple', 'Event created: "PhD Research Group Monthly Meeting"', '{"ID": 7, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (8, '2026-01-19 02:31:06.357725', 2, 'Content', 'simple', 'Event created: "Web Automation & E2E Testing Summit"', '{"ID": 8, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (9, '2026-01-19 02:31:42.485004', 2, 'Content', 'simple', 'Event created: "Indico Platform Deployment Planning"', '{"ID": 9, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (10, '2026-01-19 02:32:59.450703', 2, 'Content', 'simple', 'Event created: "International Workshop on Formal Methods for UI Testing"', '{"ID": 10, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (11, '2026-01-19 02:33:44.41464', 2, 'Content', 'simple', 'Event created: "Program Committee Kickoff – IC-AIT 2026"', '{"ID": 11, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (12, '2026-01-19 02:34:25.326749', 2, 'Content', 'simple', 'Event created: "Frontend Testing Strategy Review"', '{"ID": 12, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (13, '2026-01-19 02:34:55.141786', 2, 'Content', 'simple', 'Event created: "Data-Driven Quality Engineering Conference"', '{"ID": 13, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (14, '2026-01-19 02:35:20.569989', 2, 'Content', 'simple', 'Event created: "Security & Privacy Review Board"', '{"ID": 14, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (15, '2026-01-19 02:35:48.127406', 2, 'Content', 'simple', 'Event created: "Workshop on LLMs for Software Testing"', '{"ID": 15, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (16, '2026-01-19 02:36:22.156543', 2, 'Content', 'simple', 'Event created: "Accessibility Testing Guidelines Alignment"', '{"ID": 16, "Type": "Meeting"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (17, '2026-01-19 02:36:45.195172', 2, 'Content', 'simple', 'Event created: "International Symposium on End-to-End System Validation"', '{"ID": 17, "Type": "Conference"}', '{}', 0, 2, 1);
INSERT INTO categories.logs VALUES (18, '2026-01-19 02:37:11.357703', 2, 'Content', 'simple', 'Event created: "Test Infrastructure Cost Optimization Meeting"', '{"ID": 18, "Type": "Meeting"}', '{}', 0, 2, 1);

--
-- Data for Name: form_field_data; Type: TABLE DATA; Schema: event_registration; Owner: -
--

INSERT INTO event_registration.form_field_data VALUES (1, 2, '{}');
INSERT INTO event_registration.form_field_data VALUES (2, 3, '{}');
INSERT INTO event_registration.form_field_data VALUES (3, 4, '{}');
INSERT INTO event_registration.form_field_data VALUES (4, 5, '{}');
INSERT INTO event_registration.form_field_data VALUES (5, 6, '{}');
INSERT INTO event_registration.form_field_data VALUES (6, 7, '{}');
INSERT INTO event_registration.form_field_data VALUES (7, 8, '{}');
INSERT INTO event_registration.form_field_data VALUES (8, 9, '{}');
INSERT INTO event_registration.form_field_data VALUES (9, 10, '{"choices": [{"id": "506fbe9e-316b-4f7e-b0b3-fad1c5f61d78", "price": 0, "is_enabled": true, "places_limit": 0, "max_extra_slots": 0}, {"id": "4c8a6a43-f923-4aa9-bcce-468fefcd1bab", "price": 0, "is_enabled": true, "places_limit": 0, "max_extra_slots": 0}, {"id": "1d17ec95-762d-4ad6-92b8-0c1b87dc9013", "price": 0, "is_enabled": true, "places_limit": 0, "max_extra_slots": 0}, {"id": "e7c5f855-953e-47ac-b996-ed0f68bf6f71", "price": 0, "is_enabled": true, "places_limit": 0, "max_extra_slots": 0}, {"id": "0334cbad-d310-4c40-bb24-21a61f12d2de", "price": 0, "is_enabled": true, "places_limit": 0, "max_extra_slots": 0}, {"id": "6069df2c-5068-4225-9846-97b282961457", "price": 0, "is_enabled": true, "places_limit": 0, "max_extra_slots": 0}]}');
INSERT INTO event_registration.form_field_data VALUES (10, 11, '{}');

--
-- Data for Name: form_items; Type: TABLE DATA; Schema: event_registration; Owner: -
--

INSERT INTO event_registration.form_items VALUES (1, 1, 4, NULL, NULL, 1, 'Personal Data', '', true, false, false, false, NULL, 'null', NULL, false, NULL);
INSERT INTO event_registration.form_items VALUES (2, 1, 5, 2, 1, 1, 'First Name', '', true, false, true, false, 'text', '{}', NULL, false, 1);
INSERT INTO event_registration.form_items VALUES (3, 1, 5, 3, 1, 2, 'Last Name', '', true, false, true, false, 'text', '{}', NULL, false, 2);
INSERT INTO event_registration.form_items VALUES (4, 1, 5, 1, 1, 3, 'Email Address', '', true, false, true, false, 'email', '{}', NULL, false, 3);
INSERT INTO event_registration.form_items VALUES (5, 1, 5, 4, 1, 4, 'Affiliation', '', true, false, false, false, 'text', '{}', NULL, false, 4);
INSERT INTO event_registration.form_items VALUES (6, 1, 5, 6, 1, 1000, 'Address', '', false, false, false, false, 'textarea', '{}', NULL, false, 5);
INSERT INTO event_registration.form_items VALUES (7, 1, 5, 8, 1, 1001, 'Country', '', false, false, false, false, 'country', '{}', NULL, false, 6);
INSERT INTO event_registration.form_items VALUES (8, 1, 5, 7, 1, 1002, 'Phone Number', '', false, false, false, false, 'phone', '{}', NULL, false, 7);
INSERT INTO event_registration.form_items VALUES (9, 1, 5, 9, 1, 1003, 'Position', '', false, false, false, false, 'text', '{}', NULL, false, 8);
INSERT INTO event_registration.form_items VALUES (10, 1, 5, 5, 1, 1004, 'Title', '', false, false, false, false, 'single_choice', '{"captions": {"0334cbad-d310-4c40-bb24-21a61f12d2de": "Prof.", "1d17ec95-762d-4ad6-92b8-0c1b87dc9013": "Mrs", "4c8a6a43-f923-4aa9-bcce-468fefcd1bab": "Ms", "506fbe9e-316b-4f7e-b0b3-fad1c5f61d78": "Mr", "6069df2c-5068-4225-9846-97b282961457": "Mx", "e7c5f855-953e-47ac-b996-ed0f68bf6f71": "Dr"}, "item_type": "dropdown", "default_item": null, "with_extra_slots": false}', NULL, false, 9);
INSERT INTO event_registration.form_items VALUES (11, 1, 5, 10, 1, 1005, 'Picture', '', false, false, false, false, 'picture', '{}', NULL, false, 10);

--
-- Data for Name: forms; Type: TABLE DATA; Schema: event_registration; Owner: -
--

INSERT INTO event_registration.forms VALUES (1, 3, 'Registration Form', false, '', '', '2026-01-19 02:16:32.556265', NULL, 3, NULL, false, false, false, true, NULL, 1, 2, NULL, false, false, false, false, 'e09cd74e-ad5f-408a-beac-e9a5cd35950d', 0.00, 'EUR', NULL, '', '', '', false, false, '{}', false, false, false, true, true, true, false, NULL, NULL, false, false);

--
-- Data for Name: items; Type: TABLE DATA; Schema: event_surveys; Owner: -
--

INSERT INTO event_surveys.items VALUES (2, 1, 1, 1, 1, 'Number Question', NULL, true, 'number', '{"max_value": 100, "min_value": 1}', 'Question description, answer in range 1-100');
INSERT INTO event_surveys.items VALUES (3, 1, 1, 2, 1, 'Multiple Choice Question', NULL, true, 'multiselect', '{"options": [{"id": "6e75574f-7030-4431-8ba1-a43e7bbd0c3c", "option": "Option 1"}, {"id": "ba6223eb-7273-49be-9dda-16d72b816a96", "option": "Option 2"}, {"id": "05f465b2-2583-4321-80a7-b664a0bcb28c", "option": "Option 3"}, {"id": "68431edb-2e6d-4868-a221-b5824b79308f", "option": "Option 4"}], "max_choices": 4, "min_choices": 1}', 'Select n of N');
INSERT INTO event_surveys.items VALUES (6, 1, 1, 5, 1, 'Yes/No Question', NULL, true, 'bool', '{}', 'Yes or No?');
INSERT INTO event_surveys.items VALUES (1, 1, NULL, 1, 2, '', false, NULL, NULL, '{}', '');
INSERT INTO event_surveys.items VALUES (8, 1, NULL, 3, 2, 'Section 1', true, NULL, NULL, '{}', 'Section description');
INSERT INTO event_surveys.items VALUES (9, 1, 8, 1, 1, 'Multiline Text Question', NULL, true, 'text', '{"max_words": 200, "multiline": true, "max_length": null}', 'Description (max. 200 words)');

--
-- Data for Name: surveys; Type: TABLE DATA; Schema: event_surveys; Owner: -
--

INSERT INTO event_surveys.surveys VALUES (1, 2, 'Lecture Survey', 'f0aebe9a-4a32-4467-bafe-7bc7b416e457', 'Curabitur sit amet tristique dolor. Maecenas aliquam felis arcu, a fringilla justo suscipit sed. Curabitur commodo nec sem id volutpat. Curabitur mattis lobortis bibendum. Aliquam erat volutpat. Etiam pretium non est a semper. Sed interdum nibh vitae pellentesque molestie. Suspendisse mi ipsum, ornare id tempus sit amet, posuere at nisi. Integer tristique iaculis odio, a fringilla mi. Suspendisse potenti. Fusce cursus vulputate neque, eu hendrerit orci rhoncus a. Phasellus placerat vehicula tincidunt. Quisque mauris lorem, condimentum at metus viverra, efficitur consequat ligula.', false, true, false, NULL, '2026-01-19 02:12:43.913642', NULL, false, false, false, false, '{}', '{}', false, 0);

--
-- Data for Name: breaks; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.breaks VALUES (1, 'Break', '00:20:00', '', '253f08', 'e3f2d3', true, NULL, NULL, '', '', '');
INSERT INTO events.breaks VALUES (2, 'Break', '00:20:00', '', '253f08', 'e3f2d3', true, NULL, NULL, '', '', '');
INSERT INTO events.breaks VALUES (3, 'Break', '00:20:00', '', '253f08', 'e3f2d3', true, NULL, NULL, '', '', '');

--
-- Data for Name: event_person_links; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.event_person_links VALUES (1, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0);
INSERT INTO events.event_person_links VALUES (2, 2, 2, NULL, NULL, 4, NULL, NULL, NULL, NULL, 0);

--
-- Data for Name: events; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.events VALUES (9, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:31:42.201527', '2025-02-11 03:00:00', '2025-02-11 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Indico Platform Deployment Planning', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (10, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:32:59.415297', '2025-02-15 03:00:00', '2025-02-16 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'International Workshop on Formal Methods for UI Testing', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (11, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:33:44.387377', '2025-01-05 03:00:00', '2025-01-05 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Program Committee Kickoff – IC-AIT 2026', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (4, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:24:15.046478', '2025-01-19 03:00:00', '2025-01-19 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Meeting 1', '<p>Vivamus quis risus quis enim lacinia pulvinar. Nulla accumsan urna et fringilla suscipit. Nullam porta tincidunt enim, sed ultricies urna maximus ac. Nam id elit quam. Nullam a sollicitudin turpis. Suspendisse venenatis velit nec libero congue, sed tempus erat consequat. Nulla nec tempor tellus. Fusce at ante justo. In hac habitasse platea dictumst. Nulla eleifend fermentum orci quis maximus.</p>', NULL, NULL, 'Meeting Venue', 'Meeting Room', '', 0, '', '');
INSERT INTO events.events VALUES (5, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:26:31.617888', '2025-01-01 03:00:00', '2025-01-01 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Weekly Software Architecture Sync', '', NULL, NULL, 'Conference Room B / Zoom', '', '', 0, '', '');
INSERT INTO events.events VALUES (1, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:00:07.885713', '2025-03-01 02:00:00', '2025-03-01 04:00:00', 'Europe/Zurich', 1, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Lecture 1', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean id nunc semper, tincidunt tellus et, pellentesque est. In tincidunt tincidunt turpis, eu dapibus diam malesuada ut. Donec turpis sapien, mattis eget urna id, auctor ultrices justo. Nunc laoreet, ex vel hendrerit viverra, mauris dolor tincidunt arcu, ac eleifend metus elit eget arcu. Integer venenatis fermentum dapibus. Praesent ultrices ut diam eget sagittis. Sed vitae diam nec nisi commodo viverra in volutpat erat. Ut rhoncus volutpat mi, eget pulvinar tortor gravida a.</p>', NULL, NULL, 'Lecture Venue', 'Lecture Room', '', 0, '', '');
INSERT INTO events.events VALUES (2, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:01:39.044024', '2025-03-02 03:00:00', '2025-03-02 05:00:00', 'Europe/Zurich', 1, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Lecture 2 w/ Survey', '', NULL, NULL, 'Lecture Venue', 'Lecture Room', '', 0, '', '');
INSERT INTO events.events VALUES (3, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:14:49.363683', '2025-03-01 03:00:00', '2025-03-05 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 3, 'Conference 1', '<p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nam porta nunc nec dui vulputate accumsan. Donec id augue lacus. Etiam massa risus, rhoncus a venenatis ut, molestie at augue. Ut quis dui et augue commodo tincidunt eget a sem. Cras nisi orci, iaculis vel dapibus a, laoreet quis justo. Aenean dictum diam eget metus mattis porta. Duis lorem leo, elementum id tortor a, rutrum tempor lacus. Morbi sit amet nunc id arcu hendrerit maximus.</p>', NULL, NULL, 'Conference Venue', 'Conference Room', '', 0, '', '');
INSERT INTO events.events VALUES (6, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:29:53.833393', '2025-02-01 03:00:00', '2025-02-03 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'International Conference on AI Testing (IC-AIT 2026)', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (7, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:30:34.731783', '2025-02-02 03:00:00', '2025-02-02 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'PhD Research Group Monthly Meeting', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (8, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:31:06.322254', '2025-02-07 03:00:00', '2025-02-12 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Web Automation & E2E Testing Summit', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (12, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:34:25.301885', '2025-01-11 03:00:00', '2025-01-11 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Frontend Testing Strategy Review', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (13, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:34:55.106263', '2025-01-12 03:00:00', '2025-01-14 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Data-Driven Quality Engineering Conference', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (14, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:35:20.543782', '2025-01-14 03:00:00', '2025-01-14 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Security & Privacy Review Board', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (15, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:35:48.087852', '2025-01-14 03:00:00', '2025-01-15 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Workshop on LLMs for Software Testing', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (16, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:36:22.117148', '2025-01-15 03:00:00', '2025-01-15 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Accessibility Testing Guidelines Alignment', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (17, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:36:45.15676', '2025-01-17 03:00:00', '2025-01-19 05:00:00', 'Europe/Zurich', 3, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'International Symposium on End-to-End System Validation', '', NULL, NULL, '', '', '', 1, '', '');
INSERT INTO events.events VALUES (18, false, false, 1, 0, NULL, NULL, NULL, '', '2026-01-19 02:37:11.332359', '2025-01-22 03:00:00', '2025-01-22 05:00:00', 'Europe/Zurich', 2, NULL, '{}', NULL, 'null', NULL, 'null', NULL, NULL, '', NULL, true, 0, 0, 0, 'Test Infrastructure Cost Optimization Meeting', '', NULL, NULL, '', '', '', 1, '', '');

--
-- Data for Name: logs; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.logs VALUES (1, '2026-01-19 02:00:07.943965', 2, 'Protection', 'simple', 'ACL entry added', '{"User": "Admin User", "Read Access": false, "Manager": false, "Permissions": "Submission"}', '{}', 1, 2, 1);
INSERT INTO events.logs VALUES (2, '2026-01-19 02:00:07.964933', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 1, 1, 1);
INSERT INTO events.logs VALUES (3, '2026-01-19 02:01:39.091126', 2, 'Protection', 'simple', 'ACL entry added', '{"Email": "first.last@university.com", "Read Access": false, "Manager": false, "Permissions": "Submission"}', '{}', 2, 2, 1);
INSERT INTO events.logs VALUES (4, '2026-01-19 02:01:39.123641', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 2, 1, 1);
INSERT INTO events.logs VALUES (5, '2026-01-19 02:14:49.405303', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 3, 1, 1);
INSERT INTO events.logs VALUES (6, '2026-01-19 02:15:10.726731', 3, 'Event', 'simple', 'Description updated', '{"Changes": {"_diff": true, "Description": ["", "<p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nam porta nunc nec dui vulputate accumsan. Donec id augue lacus. Etiam massa risus, rhoncus a venenatis ut, molestie at augue. Ut quis dui et augue commodo tincidunt eget a sem. Cras nisi orci, iaculis vel dapibus a, laoreet quis justo. Aenean dictum diam eget metus mattis porta. Duis lorem leo, elementum id tortor a, rutrum tempor lacus. Morbi sit amet nunc id arcu hendrerit maximus.</p>", "text"]}}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (7, '2026-01-19 02:16:11.432036', 2, 'Registration', 'simple', 'Registration form "Registration Form" has been created', '{"Visibility to participants": "Show all participants", "Visibility to everyone": "Show only consenting participants", "Visibility duration": "Indefinite", "Retention period": "Indefinite"}', '{"registration_form_id": 1}', 3, 2, 1);
INSERT INTO events.logs VALUES (8, '2026-01-19 02:16:32.566705', 3, 'Registration', 'simple', 'Registration form "Registration Form" was opened', '{}', '{"registration_form_id": 1}', 3, 1, 1);
INSERT INTO events.logs VALUES (9, '2026-01-19 02:16:56.8251', 2, 'Roles', 'simple', 'Added role: "Session Chair"', '{}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (10, '2026-01-19 02:18:27.030212', 2, 'Sessions', 'simple', 'Session "Session 1" has been created', '{}', '{"session_id": 1}', 3, 2, 1);
INSERT INTO events.logs VALUES (11, '2026-01-19 02:18:38.73554', 2, 'Sessions', 'simple', 'Session "Session 2" has been created', '{}', '{"session_id": 2}', 3, 2, 1);
INSERT INTO events.logs VALUES (12, '2026-01-19 02:18:47.902692', 2, 'Sessions', 'simple', 'Session "Session 3" has been created', '{}', '{"session_id": 3}', 3, 2, 1);
INSERT INTO events.logs VALUES (13, '2026-01-19 02:19:13.179394', 2, 'Sessions', 'simple', 'Session block "Paper 1.1" for session "Session 1" has been created', '{}', '{"session_block_id": 1}', 3, 2, 1);
INSERT INTO events.logs VALUES (14, '2026-01-19 02:19:13.185426', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 1.1'' created', '{"Time": "1 Jan 2025, 04:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (15, '2026-01-19 02:19:31.163511', 2, 'Sessions', 'simple', 'Session block "Paper 2.1" for session "Session 2" has been created', '{}', '{"session_block_id": 2}', 3, 2, 1);
INSERT INTO events.logs VALUES (16, '2026-01-19 02:19:31.169943', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 2.1'' created', '{"Time": "1 Jan 2025, 05:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (17, '2026-01-19 02:19:46.076351', 2, 'Sessions', 'simple', 'Session block "Paper 3.1" for session "Session 3" has been created', '{}', '{"session_block_id": 3}', 3, 2, 1);
INSERT INTO events.logs VALUES (18, '2026-01-19 02:19:46.081884', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 3.1'' created', '{"Time": "1 Jan 2025, 05:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (19, '2026-01-19 02:20:09.226543', 2, 'Timetable', 'simple', 'Entry for break ''Break'' created', '{"Time": "1 Jan 2025, 06:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (20, '2026-01-19 02:20:19.586875', 2, 'Sessions', 'simple', 'Session block "Paper 1.2" for session "Session 1" has been created', '{}', '{"session_block_id": 4}', 3, 2, 1);
INSERT INTO events.logs VALUES (21, '2026-01-19 02:20:19.592488', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 1.2'' created', '{"Time": "1 Jan 2025, 06:20"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (22, '2026-01-19 02:20:55.041851', 2, 'Sessions', 'simple', 'Session block "Paper 1.1" for session "Session 1" has been created', '{}', '{"session_block_id": 5}', 3, 2, 1);
INSERT INTO events.logs VALUES (23, '2026-01-19 02:20:55.052457', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 1.1'' created', '{"Time": "2 Jan 2025, 08:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (24, '2026-01-19 02:21:08.300508', 2, 'Sessions', 'simple', 'Session block "Paper 2.1" for session "Session 2" has been created', '{}', '{"session_block_id": 6}', 3, 2, 1);
INSERT INTO events.logs VALUES (25, '2026-01-19 02:21:08.307199', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 2.1'' created', '{"Time": "2 Jan 2025, 08:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (26, '2026-01-19 02:21:19.122927', 2, 'Sessions', 'simple', 'Session block "Paper 3.1" for session "Session 3" has been created', '{}', '{"session_block_id": 7}', 3, 2, 1);
INSERT INTO events.logs VALUES (27, '2026-01-19 02:21:19.129229', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 3.1'' created', '{"Time": "2 Jan 2025, 08:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (28, '2026-01-19 02:21:32.605736', 2, 'Sessions', 'simple', 'Session block "Paper 1.2" for session "Session 1" has been created', '{}', '{"session_block_id": 8}', 3, 2, 1);
INSERT INTO events.logs VALUES (29, '2026-01-19 02:21:32.612297', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 1.2'' created', '{"Time": "2 Jan 2025, 09:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (30, '2026-01-19 02:21:38.063216', 2, 'Timetable', 'simple', 'Entry for break ''Break'' created', '{"Time": "2 Jan 2025, 10:00"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (31, '2026-01-19 02:21:50.100626', 2, 'Sessions', 'simple', 'Session block "Paper 2.2" for session "Session 2" has been created', '{}', '{"session_block_id": 9}', 3, 2, 1);
INSERT INTO events.logs VALUES (32, '2026-01-19 02:21:50.106849', 2, 'Timetable', 'simple', 'Entry for session block ''Paper 2.2'' created', '{"Time": "2 Jan 2025, 10:20"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (33, '2026-01-19 02:22:03.206076', 2, 'Timetable', 'simple', 'Entry for break ''Break'' created', '{"Time": "2 Jan 2025, 11:20"}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (34, '2026-01-19 02:24:15.079291', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 4, 1, 1);
INSERT INTO events.logs VALUES (35, '2026-01-19 02:24:27.856521', 3, 'Event', 'simple', 'Description updated', '{"Changes": {"_diff": true, "Description": ["", "<p>Vivamus quis risus quis enim lacinia pulvinar. Nulla accumsan urna et fringilla suscipit. Nullam porta tincidunt enim, sed ultricies urna maximus ac. Nam id elit quam. Nullam a sollicitudin turpis. Suspendisse venenatis velit nec libero congue, sed tempus erat consequat. Nulla nec tempor tellus. Fusce at ante justo. In hac habitasse platea dictumst. Nulla eleifend fermentum orci quis maximus.</p>", "text"]}}', '{}', 4, 2, 1);
INSERT INTO events.logs VALUES (36, '2026-01-19 02:26:31.647441', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 5, 1, 1);
INSERT INTO events.logs VALUES (37, '2026-01-19 02:26:58.707122', 3, 'Event', 'simple', 'Dates updated', '{"Changes": {"_diff": true, "Start date": ["2024-01-01T03:00:00+00:00", "2025-01-01T03:00:00+00:00", "datetime"], "End date": ["2024-01-01T05:00:00+00:00", "2025-01-01T05:00:00+00:00", "datetime"]}}', '{}', 5, 2, 1);
INSERT INTO events.logs VALUES (38, '2026-01-19 02:27:20.965846', 3, 'Event', 'simple', 'Dates updated', '{"Changes": {"_diff": true, "Start date": ["2025-01-01T02:00:00+00:00", "2025-03-01T02:00:00+00:00", "datetime"], "End date": ["2025-01-01T04:00:00+00:00", "2025-03-01T04:00:00+00:00", "datetime"]}}', '{}', 1, 2, 1);
INSERT INTO events.logs VALUES (39, '2026-01-19 02:28:14.721015', 3, 'Event', 'simple', 'Dates updated', '{"Changes": {"_diff": true, "Start date": ["2025-01-02T03:00:00+00:00", "2025-03-02T03:00:00+00:00", "datetime"], "End date": ["2025-01-02T05:00:00+00:00", "2025-03-02T05:00:00+00:00", "datetime"]}}', '{}', 2, 2, 1);
INSERT INTO events.logs VALUES (40, '2026-01-19 02:28:42.58421', 3, 'Event', 'simple', 'Dates updated', '{"Changes": {"_diff": true, "Start date": ["2025-01-01T03:00:00+00:00", "2025-03-01T03:00:00+00:00", "datetime"], "End date": ["2025-01-05T05:00:00+00:00", "2025-03-05T05:00:00+00:00", "datetime"]}}', '{}', 3, 2, 1);
INSERT INTO events.logs VALUES (41, '2026-01-19 02:29:53.866467', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 6, 1, 1);
INSERT INTO events.logs VALUES (42, '2026-01-19 02:30:34.796785', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 7, 1, 1);
INSERT INTO events.logs VALUES (43, '2026-01-19 02:31:06.358874', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 8, 1, 1);
INSERT INTO events.logs VALUES (44, '2026-01-19 02:31:42.487658', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 9, 1, 1);
INSERT INTO events.logs VALUES (45, '2026-01-19 02:32:59.451927', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 10, 1, 1);
INSERT INTO events.logs VALUES (46, '2026-01-19 02:33:11.738765', 3, 'Event', 'simple', 'Dates updated', '{"Changes": {"_diff": true, "Start date": ["2026-02-15T03:00:00+00:00", "2025-02-15T03:00:00+00:00", "datetime"], "End date": ["2026-02-16T05:00:00+00:00", "2025-02-16T05:00:00+00:00", "datetime"]}}', '{}', 10, 2, 1);
INSERT INTO events.logs VALUES (47, '2026-01-19 02:33:44.415952', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 11, 1, 1);
INSERT INTO events.logs VALUES (48, '2026-01-19 02:34:25.327849', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 12, 1, 1);
INSERT INTO events.logs VALUES (49, '2026-01-19 02:34:55.143059', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 13, 1, 1);
INSERT INTO events.logs VALUES (50, '2026-01-19 02:35:20.571012', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 14, 1, 1);
INSERT INTO events.logs VALUES (51, '2026-01-19 02:35:48.128799', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 15, 1, 1);
INSERT INTO events.logs VALUES (52, '2026-01-19 02:36:22.157685', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 16, 1, 1);
INSERT INTO events.logs VALUES (53, '2026-01-19 02:36:45.196409', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 17, 1, 1);
INSERT INTO events.logs VALUES (54, '2026-01-19 02:37:11.358684', 2, 'Event', 'simple', 'Event created', '{"Category": "Home"}', '{}', 18, 1, 1);

--
-- Data for Name: persons; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.persons VALUES (1, 1, 1, 'Admin', 'User', 'admin@admin.com', 0, NULL, 'WebTestPilot', '', '', NULL, false);
INSERT INTO events.persons VALUES (2, 2, NULL, 'First', 'Last', 'first.last@university.com', 0, NULL, 'University', '', '', NULL, false);

--
-- Data for Name: principals; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.principals VALUES (false, true, '{submit}', 1, 1, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, false, '{submit}', 2, 2, 4, NULL, NULL, NULL, NULL, 'first.last@university.com', NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 3, 2, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 4, 3, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 5, 4, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 6, 5, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 7, 6, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 8, 7, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 9, 8, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 10, 9, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 11, 10, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 12, 11, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 13, 12, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 14, 13, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 15, 14, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 16, 15, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 17, 16, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 18, 17, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO events.principals VALUES (false, true, '{}', 19, 18, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

--
-- Data for Name: roles; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.roles VALUES (1, 3, 'Session Chair', 'SC', '6e5494');

--
-- Data for Name: session_blocks; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.session_blocks VALUES (1, 1, 'Paper 1.1', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (2, 2, 'Paper 2.1', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (3, 3, 'Paper 3.1', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (4, 1, 'Paper 1.2', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (5, 1, 'Paper 1.1', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (6, 2, 'Paper 2.1', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (7, 3, 'Paper 3.1', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (8, 1, 'Paper 1.2', '', '01:00:00', true, NULL, NULL, '', '', '');
INSERT INTO events.session_blocks VALUES (9, 2, 'Paper 2.2', '', '01:00:00', true, NULL, NULL, '', '', '');

--
-- Data for Name: sessions; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.sessions VALUES (1, 1, 3, NULL, 'Session 1', '', '00:20:00', false, '', 'eff5ff', '0d316f', 1, true, NULL, NULL, '', '', '');
INSERT INTO events.sessions VALUES (2, 2, 3, NULL, 'Session 2', '', '00:20:00', false, '', '1f1100', 'ecc495', 1, true, NULL, NULL, '', '', '');
INSERT INTO events.sessions VALUES (3, 3, 3, NULL, 'Session 3', '', '00:20:00', false, '', '202020', 'efebc2', 1, true, NULL, NULL, '', '', '');

--
-- Data for Name: settings; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.settings VALUES (1, 'layout', 'timetable_theme', '"lecture"', 1);
INSERT INTO events.settings VALUES (2, 'layout', 'timetable_theme', '"lecture"', 2);
INSERT INTO events.settings VALUES (3, 'contributions', 'published', 'false', 3);
INSERT INTO events.settings VALUES (4, 'layout', 'timetable_theme', '"standard"', 4);
INSERT INTO events.settings VALUES (5, 'layout', 'timetable_theme', '"standard"', 5);
INSERT INTO events.settings VALUES (6, 'core', 'start_dt_override', 'null', 3);
INSERT INTO events.settings VALUES (7, 'core', 'end_dt_override', 'null', 3);
INSERT INTO events.settings VALUES (8, 'contributions', 'published', 'false', 6);
INSERT INTO events.settings VALUES (9, 'layout', 'timetable_theme', '"standard"', 7);
INSERT INTO events.settings VALUES (10, 'contributions', 'published', 'false', 8);
INSERT INTO events.settings VALUES (11, 'layout', 'timetable_theme', '"standard"', 9);
INSERT INTO events.settings VALUES (12, 'contributions', 'published', 'false', 10);
INSERT INTO events.settings VALUES (13, 'core', 'start_dt_override', 'null', 10);
INSERT INTO events.settings VALUES (14, 'core', 'end_dt_override', 'null', 10);
INSERT INTO events.settings VALUES (15, 'layout', 'timetable_theme', '"standard"', 11);
INSERT INTO events.settings VALUES (16, 'layout', 'timetable_theme', '"standard"', 12);
INSERT INTO events.settings VALUES (17, 'contributions', 'published', 'false', 13);
INSERT INTO events.settings VALUES (18, 'layout', 'timetable_theme', '"standard"', 14);
INSERT INTO events.settings VALUES (19, 'contributions', 'published', 'false', 15);
INSERT INTO events.settings VALUES (20, 'layout', 'timetable_theme', '"standard"', 16);
INSERT INTO events.settings VALUES (21, 'contributions', 'published', 'false', 17);
INSERT INTO events.settings VALUES (22, 'layout', 'timetable_theme', '"standard"', 18);

--
-- Data for Name: timetable_entries; Type: TABLE DATA; Schema: events; Owner: -
--

INSERT INTO events.timetable_entries VALUES (1, 3, NULL, 1, NULL, NULL, 1, '2025-03-01 03:00:00');
INSERT INTO events.timetable_entries VALUES (2, 3, NULL, 2, NULL, NULL, 1, '2025-03-01 04:00:00');
INSERT INTO events.timetable_entries VALUES (3, 3, NULL, 3, NULL, NULL, 1, '2025-03-01 04:00:00');
INSERT INTO events.timetable_entries VALUES (4, 3, NULL, NULL, NULL, 1, 3, '2025-03-01 05:00:00');
INSERT INTO events.timetable_entries VALUES (5, 3, NULL, 4, NULL, NULL, 1, '2025-03-01 05:20:00');
INSERT INTO events.timetable_entries VALUES (6, 3, NULL, 5, NULL, NULL, 1, '2025-03-02 07:00:00');
INSERT INTO events.timetable_entries VALUES (7, 3, NULL, 6, NULL, NULL, 1, '2025-03-02 07:00:00');
INSERT INTO events.timetable_entries VALUES (8, 3, NULL, 7, NULL, NULL, 1, '2025-03-02 07:00:00');
INSERT INTO events.timetable_entries VALUES (9, 3, NULL, 8, NULL, NULL, 1, '2025-03-02 08:00:00');
INSERT INTO events.timetable_entries VALUES (10, 3, NULL, NULL, NULL, 2, 3, '2025-03-02 09:00:00');
INSERT INTO events.timetable_entries VALUES (11, 3, NULL, 9, NULL, NULL, 1, '2025-03-02 09:20:00');
INSERT INTO events.timetable_entries VALUES (12, 3, NULL, NULL, NULL, 3, 3, '2025-03-02 10:20:00');

--
-- Data for Name: settings; Type: TABLE DATA; Schema: indico; Owner: -
--

INSERT INTO indico.settings VALUES (3, 'upcoming_events', 'entries', '[]');
INSERT INTO indico.settings VALUES (4, 'upcoming_events', 'max_entries', '20');

--
-- Data for Name: location_principals; Type: TABLE DATA; Schema: roombooking; Owner: -
--

INSERT INTO roombooking.location_principals VALUES (false, true, '{}', 1, 1, 1, 1, NULL, NULL, NULL);


--
-- Data for Name: locations; Type: TABLE DATA; Schema: roombooking; Owner: -
--

INSERT INTO roombooking.locations VALUES (1, 'Location 1', '', '%1$s/%2$s-%3$s', false);

--
-- Data for Name: registrations; Type: TABLE DATA; Schema: event_registration; Owner: -
--

INSERT INTO event_registration.registrations VALUES
(1, gen_random_uuid(), 7, 3, 1, NULL, NULL, 1, 50.00, 0.00, 'EUR', '2026-01-19 12:20:00', 'emma.johnson@example.com', 'Emma', 'Johnson', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(2, gen_random_uuid(), 8, 3, 1, NULL, NULL, 1, 60.00, 5.00, 'EUR', '2026-01-19 12:22:00', 'liam.smith@example.com', 'Liam', 'Smith', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(3, gen_random_uuid(), 9, 3, 1, NULL, NULL, 2, 75.00, 0.00, 'EUR', '2026-01-19 12:24:00', 'olivia.brown@example.com', 'Olivia', 'Brown', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(4, gen_random_uuid(), 10, 3, 1, NULL, NULL, 1, 55.00, 0.00, 'EUR', '2026-01-19 12:26:00', 'noah.jones@example.com', 'Noah', 'Jones', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(5, gen_random_uuid(), 11, 3, 1, NULL, NULL, 1, 80.00, 10.00, 'EUR', '2026-01-19 12:28:00', 'ava.garcia@example.com', 'Ava', 'Garcia', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(6, gen_random_uuid(), 12, 3, 1, NULL, NULL, 2, 90.00, 0.00, 'EUR', '2026-01-19 12:30:00', 'ethan.martinez@example.com', 'Ethan', 'Martinez', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(7, gen_random_uuid(), 13, 3, 1, NULL, NULL, 1, 70.00, 0.00, 'EUR', '2026-01-19 12:32:00', 'mia.rodriguez@example.com', 'Mia', 'Rodriguez', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(8, gen_random_uuid(), 14, 3, 1, NULL, NULL, 1, 65.00, 5.00, 'EUR', '2026-01-19 12:34:00', 'jacob.lee@example.com', 'Jacob', 'Lee', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(9, gen_random_uuid(), 15, 3, 1, NULL, NULL, 2, 85.00, 0.00, 'EUR', '2026-01-19 12:36:00', 'sophia.walker@example.com', 'Sophia', 'Walker', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(10, gen_random_uuid(), 16, 3, 1, NULL, NULL, 1, 55.00, 0.00, 'EUR', '2026-01-19 12:38:00', 'mason.hall@example.com', 'Mason', 'Hall', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(11, gen_random_uuid(), 17, 3, 1, NULL, NULL, 1, 60.00, 0.00, 'EUR', '2026-01-19 12:40:00', 'isabella.allen@example.com', 'Isabella', 'Allen', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(12, gen_random_uuid(), 18, 3, 1, NULL, NULL, 2, 95.00, 0.00, 'EUR', '2026-01-19 12:42:00', 'logan.young@example.com', 'Logan', 'Young', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(13, gen_random_uuid(), 19, 3, 1, NULL, NULL, 1, 75.00, 5.00, 'EUR', '2026-01-19 12:44:00', 'charlotte.king@example.com', 'Charlotte', 'King', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(14, gen_random_uuid(), 20, 3, 1, NULL, NULL, 1, 80.00, 0.00, 'EUR', '2026-01-19 12:46:00', 'lucas.scott@example.com', 'Lucas', 'Scott', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(15, gen_random_uuid(), 21, 3, 1, NULL, NULL, 2, 65.00, 0.00, 'EUR', '2026-01-19 12:48:00', 'amelia.adams@example.com', 'Amelia', 'Adams', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(16, gen_random_uuid(), 22, 3, 1, NULL, NULL, 1, 70.00, 5.00, 'EUR', '2026-01-19 12:50:00', 'elijah.baker@example.com', 'Elijah', 'Baker', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(17, gen_random_uuid(), 23, 3, 1, NULL, NULL, 1, 90.00, 0.00, 'EUR', '2026-01-19 12:52:00', 'harper.gonzalez@example.com', 'Harper', 'Gonzalez', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(18, gen_random_uuid(), 24, 3, 1, NULL, NULL, 2, 85.00, 0.00, 'EUR', '2026-01-19 12:54:00', 'benjamin.nelson@example.com', 'Benjamin', 'Nelson', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(19, gen_random_uuid(), 25, 3, 1, NULL, NULL, 1, 60.00, 0.00, 'EUR', '2026-01-19 12:56:00', 'evelyn.carter@example.com', 'Evelyn', 'Carter', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, ''),
(20, gen_random_uuid(), 26, 3, 1, NULL, NULL, 1, 55.00, 5.00, 'EUR', '2026-01-19 12:58:00', 'alexander.mitchell@example.com', 'Alexander', 'Mitchell', false, gen_random_uuid(), false, NULL, '', 2, false, false, NULL, '');

--
-- Data for Name: registration_data; Type: TABLE DATA; Schema: event_registration; Owner: -
--

INSERT INTO event_registration.registration_data VALUES
(1, 1, '"Emma"', NULL, NULL, NULL, NULL, NULL, NULL),
(1, 2, '"Johnson"', NULL, NULL, NULL, NULL, NULL, NULL),
(1, 3, '"emma.johnson@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(1, 4, '"National University of Singapore"', NULL, NULL, NULL, NULL, NULL, NULL),

(2, 1, '"Liam"', NULL, NULL, NULL, NULL, NULL, NULL),
(2, 2, '"Smith"', NULL, NULL, NULL, NULL, NULL, NULL),
(2, 3, '"liam.smith@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(2, 4, '"University of Malaya"', NULL, NULL, NULL, NULL, NULL, NULL),

(3, 1, '"Olivia"', NULL, NULL, NULL, NULL, NULL, NULL),
(3, 2, '"Brown"', NULL, NULL, NULL, NULL, NULL, NULL),
(3, 3, '"olivia.brown@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(3, 4, '"Nanyang Technological University"', NULL, NULL, NULL, NULL, NULL, NULL),

(4, 1, '"Noah"', NULL, NULL, NULL, NULL, NULL, NULL),
(4, 2, '"Jones"', NULL, NULL, NULL, NULL, NULL, NULL),
(4, 3, '"noah.jones@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(4, 4, '"Singapore University of Technology"', NULL, NULL, NULL, NULL, NULL, NULL),

(5, 1, '"Ava"', NULL, NULL, NULL, NULL, NULL, NULL),
(5, 2, '"Garcia"', NULL, NULL, NULL, NULL, NULL, NULL),
(5, 3, '"ava.garcia@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(5, 4, '"Shanghai Jiao Tong University"', NULL, NULL, NULL, NULL, NULL, NULL),

(6, 1, '"Ethan"', NULL, NULL, NULL, NULL, NULL, NULL),
(6, 2, '"Martinez"', NULL, NULL, NULL, NULL, NULL, NULL),
(6, 3, '"ethan.martinez@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(6, 4, '"University of Hong Kong"', NULL, NULL, NULL, NULL, NULL, NULL),

(7, 1, '"Mia"', NULL, NULL, NULL, NULL, NULL, NULL),
(7, 2, '"Rodriguez"', NULL, NULL, NULL, NULL, NULL, NULL),
(7, 3, '"mia.rodriguez@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(7, 4, '"Singapore Management University"', NULL, NULL, NULL, NULL, NULL, NULL),

(8, 1, '"Jacob"', NULL, NULL, NULL, NULL, NULL, NULL),
(8, 2, '"Lee"', NULL, NULL, NULL, NULL, NULL, NULL),
(8, 3, '"jacob.lee@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(8, 4, '"University of Malaya"', NULL, NULL, NULL, NULL, NULL, NULL),

(9, 1, '"Sophia"', NULL, NULL, NULL, NULL, NULL, NULL),
(9, 2, '"Walker"', NULL, NULL, NULL, NULL, NULL, NULL),
(9, 3, '"sophia.walker@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(9, 4, '"National University of Singapore"', NULL, NULL, NULL, NULL, NULL, NULL),

(10, 1, '"Mason"', NULL, NULL, NULL, NULL, NULL, NULL),
(10, 2, '"Hall"', NULL, NULL, NULL, NULL, NULL, NULL),
(10, 3, '"mason.hall@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(10, 4, '"Nanyang Technological University"', NULL, NULL, NULL, NULL, NULL, NULL),

(11, 1, '"Isabella"', NULL, NULL, NULL, NULL, NULL, NULL),
(11, 2, '"Allen"', NULL, NULL, NULL, NULL, NULL, NULL),
(11, 3, '"isabella.allen@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(11, 4, '"University of Hong Kong"', NULL, NULL, NULL, NULL, NULL, NULL),

(12, 1, '"Logan"', NULL, NULL, NULL, NULL, NULL, NULL),
(12, 2, '"Young"', NULL, NULL, NULL, NULL, NULL, NULL),
(12, 3, '"logan.young@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(12, 4, '"Singapore University of Technology"', NULL, NULL, NULL, NULL, NULL, NULL),

(13, 1, '"Charlotte"', NULL, NULL, NULL, NULL, NULL, NULL),
(13, 2, '"King"', NULL, NULL, NULL, NULL, NULL, NULL),
(13, 3, '"charlotte.king@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(13, 4, '"Shanghai Jiao Tong University"', NULL, NULL, NULL, NULL, NULL, NULL),

(14, 1, '"Lucas"', NULL, NULL, NULL, NULL, NULL, NULL),
(14, 2, '"Scott"', NULL, NULL, NULL, NULL, NULL, NULL),
(14, 3, '"lucas.scott@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(14, 4, '"National University of Singapore"', NULL, NULL, NULL, NULL, NULL, NULL),

(15, 1, '"Amelia"', NULL, NULL, NULL, NULL, NULL, NULL),
(15, 2, '"Adams"', NULL, NULL, NULL, NULL, NULL, NULL),
(15, 3, '"amelia.adams@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(15, 4, '"Nanyang Technological University"', NULL, NULL, NULL, NULL, NULL, NULL),

(16, 1, '"Elijah"', NULL, NULL, NULL, NULL, NULL, NULL),
(16, 2, '"Baker"', NULL, NULL, NULL, NULL, NULL, NULL),
(16, 3, '"elijah.baker@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(16, 4, '"University of Malaya"', NULL, NULL, NULL, NULL, NULL, NULL),

(17, 1, '"Harper"', NULL, NULL, NULL, NULL, NULL, NULL),
(17, 2, '"Gonzalez"', NULL, NULL, NULL, NULL, NULL, NULL),
(17, 3, '"harper.gonzalez@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(17, 4, '"Singapore Management University"', NULL, NULL, NULL, NULL, NULL, NULL),

(18, 1, '"Benjamin"', NULL, NULL, NULL, NULL, NULL, NULL),
(18, 2, '"Nelson"', NULL, NULL, NULL, NULL, NULL, NULL),
(18, 3, '"benjamin.nelson@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(18, 4, '"University of Hong Kong"', NULL, NULL, NULL, NULL, NULL, NULL),

(19, 1, '"Evelyn"', NULL, NULL, NULL, NULL, NULL, NULL),
(19, 2, '"Carter"', NULL, NULL, NULL, NULL, NULL, NULL),
(19, 3, '"evelyn.carter@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(19, 4, '"National University of Singapore"', NULL, NULL, NULL, NULL, NULL, NULL),

(20, 1, '"Alexander"', NULL, NULL, NULL, NULL, NULL, NULL),
(20, 2, '"Mitchell"', NULL, NULL, NULL, NULL, NULL, NULL),
(20, 3, '"alexander.mitchell@example.com"', NULL, NULL, NULL, NULL, NULL, NULL),
(20, 4, '"Nanyang Technological University"', NULL, NULL, NULL, NULL, NULL, NULL);

SELECT pg_catalog.setval('categories.logs_id_seq', 18, true);
SELECT pg_catalog.setval('event_registration.form_field_data_id_seq', 10, true);
SELECT pg_catalog.setval('event_registration.form_items_id_seq', 11, true);
SELECT pg_catalog.setval('event_registration.forms_id_seq', 1, true);
SELECT pg_catalog.setval('event_surveys.items_id_seq', 9, true);
SELECT pg_catalog.setval('event_surveys.surveys_id_seq', 1, true);
SELECT pg_catalog.setval('events.breaks_id_seq', 3, true);
SELECT pg_catalog.setval('events.event_person_links_id_seq', 2, true);
SELECT pg_catalog.setval('events.events_id_seq', 18, true);
SELECT pg_catalog.setval('events.logs_id_seq', 54, true);
SELECT pg_catalog.setval('events.persons_id_seq', 2, true);
SELECT pg_catalog.setval('events.principals_id_seq', 19, true);
SELECT pg_catalog.setval('events.roles_id_seq', 1, true);
SELECT pg_catalog.setval('events.session_blocks_id_seq', 9, true);
SELECT pg_catalog.setval('events.sessions_id_seq', 3, true);
SELECT pg_catalog.setval('events.settings_id_seq', 22, true);
SELECT pg_catalog.setval('events.timetable_entries_id_seq', 12, true);
SELECT pg_catalog.setval('indico.settings_id_seq', 4, true);
SELECT pg_catalog.setval('roombooking.location_principals_id_seq', 1, true);
SELECT pg_catalog.setval('roombooking.locations_id_seq', 1, true);
SELECT pg_catalog.setval('event_registration.registrations_id_seq', 20, true);

-- ============================================
-- 4️⃣ Re-enable all triggers
-- ============================================
DO $$
DECLARE
    r RECORD;
BEGIN
    -- Re-enable triggers on all user-defined tables
    FOR r IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema') 
    LOOP
        EXECUTE format('ALTER TABLE %I.%I ENABLE TRIGGER ALL;', r.schemaname, r.tablename);
    END LOOP;
END$$;