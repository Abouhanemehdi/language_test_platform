--
-- PostgreSQL database dump
--

-- Dumped from database version 15.10 (Homebrew)
-- Dumped by pg_dump version 15.12 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: answers; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.answers (
    id integer NOT NULL,
    question_id integer NOT NULL,
    answer_text text NOT NULL,
    is_correct boolean
);


ALTER TABLE public.answers OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: answers_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.answers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.answers_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.answers_id_seq OWNED BY public.answers.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.questions (
    id integer NOT NULL,
    test_id integer NOT NULL,
    question_text text NOT NULL,
    question_type character varying(50) NOT NULL,
    points integer
);


ALTER TABLE public.questions OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questions_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.questions_id_seq OWNED BY public.questions.id;


--
-- Name: scheduled_tests; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.scheduled_tests (
    id integer NOT NULL,
    user_id integer NOT NULL,
    test_id integer NOT NULL,
    scheduled_for timestamp without time zone NOT NULL,
    completed boolean
);


ALTER TABLE public.scheduled_tests OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: scheduled_tests_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.scheduled_tests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scheduled_tests_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: scheduled_tests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.scheduled_tests_id_seq OWNED BY public.scheduled_tests.id;


--
-- Name: test_results; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.test_results (
    id integer NOT NULL,
    user_id integer NOT NULL,
    test_id integer NOT NULL,
    score double precision NOT NULL,
    level_achieved character varying(10),
    completed_at timestamp without time zone,
    validated boolean
);


ALTER TABLE public.test_results OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: test_results_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.test_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.test_results_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: test_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.test_results_id_seq OWNED BY public.test_results.id;


--
-- Name: test_sessions; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.test_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    test_id integer NOT NULL,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    status character varying(20)
);


ALTER TABLE public.test_sessions OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: test_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.test_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.test_sessions_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: test_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.test_sessions_id_seq OWNED BY public.test_sessions.id;


--
-- Name: tests; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.tests (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    level character varying(10) NOT NULL,
    description text,
    duration integer,
    created_at timestamp without time zone,
    is_active boolean,
    user_role character varying(20) NOT NULL
);


ALTER TABLE public.tests OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: tests_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.tests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tests_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: tests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.tests_id_seq OWNED BY public.tests.id;


--
-- Name: user_answers; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.user_answers (
    id integer NOT NULL,
    test_result_id integer NOT NULL,
    question_id integer NOT NULL,
    answer_id integer,
    text_answer text,
    is_correct boolean
);


ALTER TABLE public.user_answers OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: user_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.user_answers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_answers_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: user_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.user_answers_id_seq OWNED BY public.user_answers.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256) NOT NULL,
    role character varying(20) NOT NULL,
    created_at timestamp without time zone,
    username character varying(64),
    last_login timestamp without time zone,
    active boolean
);


ALTER TABLE public.users OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: sjrbpfay_abouhanemehd
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO sjrbpfay_abouhanemehd;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: answers id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.answers ALTER COLUMN id SET DEFAULT nextval('public.answers_id_seq'::regclass);


--
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.questions ALTER COLUMN id SET DEFAULT nextval('public.questions_id_seq'::regclass);


--
-- Name: scheduled_tests id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.scheduled_tests ALTER COLUMN id SET DEFAULT nextval('public.scheduled_tests_id_seq'::regclass);


--
-- Name: test_results id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_results ALTER COLUMN id SET DEFAULT nextval('public.test_results_id_seq'::regclass);


--
-- Name: test_sessions id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_sessions ALTER COLUMN id SET DEFAULT nextval('public.test_sessions_id_seq'::regclass);


--
-- Name: tests id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.tests ALTER COLUMN id SET DEFAULT nextval('public.tests_id_seq'::regclass);


--
-- Name: user_answers id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.user_answers ALTER COLUMN id SET DEFAULT nextval('public.user_answers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.alembic_version (version_num) FROM stdin;
22a30a24d708
\.


--
-- Data for Name: answers; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.answers (id, question_id, answer_text, is_correct) FROM stdin;
1	1	A) go 	f
4	1	D) gone	f
5	2	 A) am 	f
6	2	B) was 	f
9	3	 A) don’t 	t
10	3	B) like 	f
11	3	C) playing 	f
12	3	D) football	f
7	2	C) were 	f
8	2	D) will be	t
3	1	C) going 	f
2	1	B) goes 	t
13	4	rep1	t
14	4	rep2	f
15	4	rep3	f
16	4	rep4	f
17	5	rep1	f
18	5	rep2	t
19	5	rep3	f
20	5	rep4	f
21	6	rep1	f
22	6	rep2	f
23	6	rep3	t
24	6	rep4	f
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.questions (id, test_id, question_text, question_type, points) FROM stdin;
1	1	Question : Complétez la phrase :\r\n"She ______ to the park every morning."	qcm	1
2	1	Question : Choisissez la bonne réponse :\r\n"If I ______ rich, I would travel the world."	qcm	1
3	1	Question : Identifiez l'erreur :\r\n"He don’t like playing football."	qcm	1
4	2	test1	qcm	1
5	2	test2	qcm	1
6	2	test3	qcm	1
\.


--
-- Data for Name: scheduled_tests; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.scheduled_tests (id, user_id, test_id, scheduled_for, completed) FROM stdin;
\.


--
-- Data for Name: test_results; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.test_results (id, user_id, test_id, score, level_achieved, completed_at, validated) FROM stdin;
1	2	1	66.66666666666666	A1	2024-12-20 16:32:51.611136	t
3	5	1	33.33333333333333	A1	2024-12-28 19:07:56.518332	t
2	4	1	0	A1	2024-12-28 18:44:12.652513	t
5	6	1	33.33333333333333	A1	2025-01-10 15:55:56.379078	t
8	3	1	33.33333333333333	A1	2025-03-08 15:49:20.850234	t
7	3	1	33.33333333333333	A1	2025-03-08 15:42:54.148984	t
4	6	1	33.33333333333333	A1	2025-01-07 17:23:08.272932	t
9	3	1	33.33333333333333	A1	2025-03-08 15:55:27.808075	t
10	3	1	66.66666666666666	A1	2025-03-08 16:02:33.695625	f
\.


--
-- Data for Name: test_sessions; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.test_sessions (id, user_id, test_id, started_at, completed_at, status) FROM stdin;
2	4	1	2024-12-28 18:31:56.845373	\N	in_progress
3	4	1	2024-12-28 18:37:16.112058	\N	in_progress
4	4	1	2024-12-28 18:37:21.810094	\N	in_progress
5	4	1	2024-12-28 18:37:42.610148	\N	in_progress
6	4	1	2024-12-28 18:39:28.225848	\N	in_progress
7	4	1	2024-12-28 18:41:32.754922	\N	in_progress
8	4	1	2024-12-28 18:43:07.864529	\N	in_progress
9	4	1	2024-12-28 18:43:34.947552	\N	in_progress
1	4	1	2024-12-28 18:30:41.64508	2024-12-28 18:44:12.721018	completed
11	5	1	2024-12-28 18:59:54.507847	\N	in_progress
12	5	1	2024-12-28 19:00:03.656648	\N	in_progress
13	5	1	2024-12-28 19:01:22.734367	\N	in_progress
14	5	1	2024-12-28 19:01:50.295118	\N	in_progress
15	5	1	2024-12-28 19:07:32.923782	\N	in_progress
10	5	1	2024-12-28 18:59:33.925627	2024-12-28 19:07:56.527002	completed
16	6	1	2025-01-07 17:22:26.174528	2025-01-07 17:23:08.285311	completed
17	6	1	2025-01-10 15:55:29.214048	2025-01-10 15:55:56.389353	completed
18	6	1	2025-01-10 15:56:01.873198	\N	in_progress
19	3	1	2025-03-08 15:40:43.877533	\N	in_progress
20	3	1	2025-03-08 15:49:00.277446	\N	in_progress
21	3	1	2025-03-08 15:55:14.777826	\N	in_progress
22	3	1	2025-03-08 16:02:15.402467	\N	in_progress
\.


--
-- Data for Name: tests; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.tests (id, title, level, description, duration, created_at, is_active, user_role) FROM stdin;
2	Test de niveau A2 Anglais	A2	test1	60	2025-03-08 17:35:54.26961	t	client
1	Test de niveau A1 Anglais	A1	test description	60	2024-12-20 15:14:20.310074	t	client
\.


--
-- Data for Name: user_answers; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.user_answers (id, test_result_id, question_id, answer_id, text_answer, is_correct) FROM stdin;
1	7	1	2	\N	f
2	7	2	8	\N	f
3	7	3	9	\N	t
4	8	1	2	\N	f
5	8	2	8	\N	f
6	8	3	9	\N	t
7	9	1	2	\N	f
8	9	2	8	\N	f
9	9	3	9	\N	t
10	10	1	3	\N	t
11	10	2	6	\N	f
12	10	3	9	\N	t
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: sjrbpfay_abouhanemehd
--

COPY public.users (id, email, password_hash, role, created_at, username, last_login, active) FROM stdin;
5	student2@test.com	scrypt:32768:8:1$c40qKZJQpTE8QIis$33ea869d74b39c53648dccbee302f52346f09f2bdfb247ef649a64b66567c16189666a1f1ef8b3df2389d3432888e34e0c44d91fad69d2e109fe389cd8bf22b4	prospect	2024-12-28 18:59:07.650801	student2	2025-03-08 17:13:38.474482	t
3	safaetalaa@gmail.com	scrypt:32768:8:1$3Xycbu0Mv0JpyNZK$56ed28249382b320e3cc73705435f13394a089c92342f767ea81d9832f8b63ac6b97a0b272c62e317613a8d48cc959062d9e8d9eb39c982fe8b7b42e26028316	client	2024-12-20 16:00:13.605996	Safae Talaa	2025-03-08 17:44:02.206448	t
1	admin@example.com	scrypt:32768:8:1$gLbNLpWR2CkbZeeW$4cb255d79dfdb14e4f970df6c014afcb5d930bd00a8e1b0323901a9e488fbd3e4560508116a663d5b37241106cf27d9a101a7cc7200ce40a80f2cda5993200f5	admin	2024-12-20 15:11:59.387904	admin	2025-03-08 18:08:07.995239	t
4	student1@test.com	scrypt:32768:8:1$KPl0TZa6iGFTUjNy$98bfe522b25e2dd08ed7dd08e6cd6215c6f0c674e4c0c50cb24fd770ffba4d3cd4d4f741439b5aee598ba29cc011b64ccf49da91b5a68f534ada164fe5def3c9	client	2024-12-28 18:02:43.201226	student1	2024-12-28 18:03:02.055717	t
6	Kawtar@gmail.com	scrypt:32768:8:1$vXHJtT1QcoF1Upy3$a008467109a5b68c645707e0f18838a9370fa3ca6fda4dae16e0bd071bd3ea38b9acb20b526ad4e26eaf39254bd781d3cd916b00d3f91a78431ea7e6fd45ed13	prospect	2025-01-07 17:22:01.282533	Kawtar	2025-01-10 15:55:06.960042	t
2	Abouhanemehdi@gmail.com	scrypt:32768:8:1$oQOleUFDtNjwhYhM$1b25a388dd3a5d0daa65406ef88494af9d1ffa1b7711f71833a44ef46c02862b740244d3c760c1b52b3ca096749e6a85851c9873996fa1e80510be3c9c47ae16	admin	2024-12-20 15:59:36.107619	ABOUHANE MEDHI	2025-01-10 15:54:50.74981	t
\.


--
-- Name: answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.answers_id_seq', 24, true);


--
-- Name: questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.questions_id_seq', 6, true);


--
-- Name: scheduled_tests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.scheduled_tests_id_seq', 1, false);


--
-- Name: test_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.test_results_id_seq', 10, true);


--
-- Name: test_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.test_sessions_id_seq', 22, true);


--
-- Name: tests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.tests_id_seq', 2, true);


--
-- Name: user_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.user_answers_id_seq', 12, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sjrbpfay_abouhanemehd
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: answers answers_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.answers
    ADD CONSTRAINT answers_pkey PRIMARY KEY (id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- Name: scheduled_tests scheduled_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.scheduled_tests
    ADD CONSTRAINT scheduled_tests_pkey PRIMARY KEY (id);


--
-- Name: test_results test_results_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_results
    ADD CONSTRAINT test_results_pkey PRIMARY KEY (id);


--
-- Name: test_sessions test_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_sessions
    ADD CONSTRAINT test_sessions_pkey PRIMARY KEY (id);


--
-- Name: tests tests_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.tests
    ADD CONSTRAINT tests_pkey PRIMARY KEY (id);


--
-- Name: user_answers user_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.user_answers
    ADD CONSTRAINT user_answers_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: answers answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.answers
    ADD CONSTRAINT answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id);


--
-- Name: questions questions_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.tests(id);


--
-- Name: scheduled_tests scheduled_tests_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.scheduled_tests
    ADD CONSTRAINT scheduled_tests_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.tests(id);


--
-- Name: scheduled_tests scheduled_tests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.scheduled_tests
    ADD CONSTRAINT scheduled_tests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: test_results test_results_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_results
    ADD CONSTRAINT test_results_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.tests(id);


--
-- Name: test_results test_results_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_results
    ADD CONSTRAINT test_results_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: test_sessions test_sessions_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_sessions
    ADD CONSTRAINT test_sessions_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.tests(id);


--
-- Name: test_sessions test_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.test_sessions
    ADD CONSTRAINT test_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_answers user_answers_answer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.user_answers
    ADD CONSTRAINT user_answers_answer_id_fkey FOREIGN KEY (answer_id) REFERENCES public.answers(id);


--
-- Name: user_answers user_answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.user_answers
    ADD CONSTRAINT user_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id);


--
-- Name: user_answers user_answers_test_result_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sjrbpfay_abouhanemehd
--

ALTER TABLE ONLY public.user_answers
    ADD CONSTRAINT user_answers_test_result_id_fkey FOREIGN KEY (test_result_id) REFERENCES public.test_results(id);


--
-- PostgreSQL database dump complete
--

