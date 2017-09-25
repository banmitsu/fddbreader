DROP DATABASE if exists fddb;

CREATE DATABASE fddb
    WITH OWNER docker
    TEMPLATE template0
    ENCODING 'UTF8'
    TABLESPACE  pg_default
    LC_COLLATE  'C.UTF-8'
    LC_CTYPE  'C.UTF-8';

\c fddb

CREATE TABLE Images (
    id SERIAL PRIMARY KEY NOT NULL,
    foldid INT,
    originalfilename VARCHAR UNIQUE,
    width INT,
    height INT,
    channel INT
);

CREATE TABLE Annotations (
    imageid INT REFERENCES Images(id),
    major_axis_radius FLOAT,
    minor_axis_radius FLOAT,
    angle FLOAT,
    center_x FLOAT,
    center_y FLOAT,
    label INT
);

CREATE OR REPLACE FUNCTION add_images(foldid INT, filename VARCHAR, width INT, height INT, channel INT)
    RETURNS void AS $$
    BEGIN
        INSERT INTO Images (foldid, originalfilename, width, height, channel) VALUES (foldid, filename, width, height, channel);
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_faces(filename VARCHAR, r1 FLOAT, r2 FLOAT, angle FLOAT, cx FLOAT, cy FLOAT, label INT)
    RETURNS void AS $$
    DECLARE
        i Images%rowtype;
    BEGIN
        --INSERT INTO Images (foldid, originalfilename, width, height, channel) VALUES (foldid, filename, width, height, channel);
        FOR i IN
            SELECT id FROM Images WHERE originalfilename=filename
        LOOP
            INSERT INTO Annotations (imageid, major_axis_radius, minor_axis_radius, angle, center_x, center_y, label) VALUES (i.id, r1, r2, angle, cx, cy, label);
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;

