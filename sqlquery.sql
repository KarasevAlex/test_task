CREATE TABLE item(
	id BIGINT PRIMARY KEY,
	status varchar NOT NULL,
	updated_at timestamptz DEFAULT NULL,
	logged_at timestamptz DEFAULT NULL);

CREATE OR REPLACE FUNCTION notify_trigger() 
RETURNS trigger AS $trigger$
BEGIN
	NEW.updated_at:=now();
	PERFORM pg_notify('item_change', row_to_json(NEW)::text);
	RETURN NEW;
 
END;
$trigger$ LANGUAGE plpgsql;



CREATE TRIGGER item_notify_update
	BEFORE UPDATE ON item
	FOR EACH ROW
	WHEN (OLD.status IS DISTINCT FROM NEW.status)
	EXECUTE PROCEDURE notify_trigger(); 