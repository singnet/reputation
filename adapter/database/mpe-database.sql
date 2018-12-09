--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 10.5

-- Started on 2018-12-09 02:03:53 CET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2417 (class 0 OID 0)
-- Dependencies: 2416
-- Name: DATABASE postgres; Type: COMMENT; Schema: -; Owner: tiero
--

COMMENT ON DATABASE postgres IS 'default administrative connection database';


--
-- TOC entry 1 (class 3079 OID 12544)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2419 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 196 (class 1259 OID 16540)
-- Name: channel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.channel (
    channel_id integer NOT NULL,
    nonce integer NOT NULL,
    sender character varying(50) NOT NULL,
    recipient character varying(50) NOT NULL,
    amount bigint NOT NULL,
    open_time integer,
    close_time integer
);


ALTER TABLE public.channel OWNER TO postgres;

--
-- TOC entry 2410 (class 0 OID 16540)
-- Dependencies: 196
-- Data for Name: channel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.channel (channel_id, nonce, sender, recipient, amount, open_time, close_time) FROM stdin;
0	0	0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE	0xA6E06cF37110930D2906e6Ae70bA6224eDED917B	11	9424242	9454432
1	0	0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE	0xA6E06cF37110930D2906e6Ae70bA6224eDED917B	11	9424242	9454432
2	0	0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE	0xA6E06cF37110930D2906e6Ae70bA6224eDED917B	135	9424242	9498084
\.


--
-- TOC entry 2288 (class 2606 OID 16544)
-- Name: channel channel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.channel
    ADD CONSTRAINT channel_pkey PRIMARY KEY (channel_id, nonce);


-- Completed on 2018-12-09 02:03:53 CET

--
-- PostgreSQL database dump complete
--

