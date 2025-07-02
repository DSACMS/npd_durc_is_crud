-- Generated PostgreSQL Foreign Key Statements
-- Source: DURC relational model
-- Generated on: 2025-07-02 00:11:55
-- Command: durc-mine-fkeys --input_json_file ../not_pointless/durc_config/DURC_relational_model.json --output_sql_file test_console_foreign_keys.sql

-- Database: postgres
ALTER TABLE postgres.NPIToEndpoint ADD CONSTRAINT fk_NPIToEndpoint_NPI_id FOREIGN KEY (NPI_id) REFERENCES public.NPI(id);
ALTER TABLE postgres.NPIToEndpoint ADD CONSTRAINT fk_NPIToEndpoint_Endpoint_id FOREIGN KEY (Endpoint_id) REFERENCES postgres.Endpoint(id);
ALTER TABLE postgres.OrgToEndpoint ADD CONSTRAINT fk_OrgToEndpoint_Endpoint_id FOREIGN KEY (Endpoint_id) REFERENCES postgres.Endpoint(id);
ALTER TABLE postgres.NPIAddress ADD CONSTRAINT fk_NPIAddress_NPI_id FOREIGN KEY (NPI_id) REFERENCES public.NPI(id);
ALTER TABLE postgres.address ADD CONSTRAINT fk_address_address_us_id FOREIGN KEY (address_us_id) REFERENCES postgres.address_us(id);
ALTER TABLE postgres.address ADD CONSTRAINT fk_address_address_international_id FOREIGN KEY (address_international_id) REFERENCES postgres.address_international(id);
ALTER TABLE postgres.address ADD CONSTRAINT fk_address_address_nonstandard_id FOREIGN KEY (address_nonstandard_id) REFERENCES postgres.address_nonstandard(id);
ALTER TABLE postgres.address_us ADD CONSTRAINT fk_address_us_address_id FOREIGN KEY (address_id) REFERENCES postgres.address(id);
ALTER TABLE postgres.address_international ADD CONSTRAINT fk_address_international_address_id FOREIGN KEY (address_id) REFERENCES postgres.address(id);
ALTER TABLE postgres.address_nonstandard ADD CONSTRAINT fk_address_nonstandard_address_id FOREIGN KEY (address_id) REFERENCES postgres.address(id);

