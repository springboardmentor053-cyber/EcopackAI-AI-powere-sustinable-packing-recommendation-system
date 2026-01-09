CREATE TABLE IF NOT EXISTS public.materials
(
    material_id integer NOT NULL DEFAULT nextval('materials_material_id_seq'::regclass),
    material_name character varying(120) COLLATE pg_catalog."default",
    strength_score integer,
    weight_capacity_kg double precision,
    biodegradability_score integer,
    co2_emission_kg double precision,
    recyclability_percent integer,
    cost_per_unit_usd double precision,
    moisture_resistance character varying(20) COLLATE pg_catalog."default",
    heat_resistance character varying(20) COLLATE pg_catalog."default",
    industry_standard character varying(50) COLLATE pg_catalog."default",
    reuse_cycles integer,
    compostable character varying(10) COLLATE pg_catalog."default",
    eco_score double precision,
    co2_per_strength double precision,
    cost_efficiency double precision,
    reuse_efficiency double precision,
    CONSTRAINT materials_pkey PRIMARY KEY (material_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.materials
    OWNER to postgres;


CREATE TABLE IF NOT EXISTS public.products
(
    product_id integer NOT NULL DEFAULT nextval('products_product_id_seq'::regclass),
    product_category character varying(100) COLLATE pg_catalog."default",
    required_strength integer,
    product_weight_kg double precision,
    handling_type character varying(50) COLLATE pg_catalog."default",
    value_category character varying(50) COLLATE pg_catalog."default",
    shipping_type character varying(50) COLLATE pg_catalog."default",
    breakage_risk character varying(20) COLLATE pg_catalog."default",
    temperature_sensitive character varying(10) COLLATE pg_catalog."default",
    shelf_life_months integer,
    CONSTRAINT products_pkey PRIMARY KEY (product_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.products
    OWNER to postgres;

ALTER TABLE materials
ADD COLUMN eco_score FLOAT,
ADD COLUMN co2_per_strength FLOAT,
ADD COLUMN cost_efficiency FLOAT,
ADD COLUMN reuse_efficiency FLOAT;

UPDATE materials
SET
    eco_score = (biodegradability_score + recyclability_percent) / 2.0,
    co2_per_strength = co2_emission_kg / NULLIF(strength_score, 0),
    cost_efficiency = strength_score / NULLIF(cost_per_unit_usd, 0),
    reuse_efficiency = reuse_cycles / NULLIF(cost_per_unit_usd, 0);

UPDATE materials
SET
    eco_score = ROUND(((biodegradability_score + recyclability_percent) / 2.0)::NUMERIC, 3),
    co2_per_strength = ROUND((co2_emission_kg / NULLIF(strength_score, 0))::NUMERIC, 3),
    cost_efficiency = ROUND((strength_score / NULLIF(cost_per_unit_usd, 0))::NUMERIC, 3),
    reuse_efficiency = ROUND((reuse_cycles / NULLIF(cost_per_unit_usd, 0))::NUMERIC, 3);


SELECT
  material_name,
  eco_score,
  co2_per_strength,
  cost_efficiency,
  reuse_efficiency
FROM materials;
