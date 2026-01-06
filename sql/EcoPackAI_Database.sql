CREATE TABLE materials (
    material_id              VARCHAR(10) PRIMARY KEY,
    material_type            VARCHAR(100) UNIQUE NOT NULL,
    strength_mpa             NUMERIC(10,2) NOT NULL CHECK (strength_mpa > 0),
    weight_capacity          NUMERIC(10,3) NOT NULL CHECK (weight_capacity > 0),
    co2_emission_kg_per_kg   NUMERIC(10,3) NOT NULL CHECK (co2_emission_kg_per_kg >= 0),
    biodegradability_score   SMALLINT NOT NULL CHECK (biodegradability_score IN (0,1)),
    recyclability_pct        NUMERIC(5,2) NOT NULL CHECK (recyclability_pct >= 0 AND recyclability_pct <= 100),
    cost_inr_per_kg          NUMERIC(10,2) NOT NULL CHECK (cost_inr_per_kg > 0),
    material_category        VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(200) UNIQUE NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    product_weight_g NUMERIC(10,2) NOT NULL CHECK (product_weight_g > 0),
    product_volume_cm3 NUMERIC(12,2) NOT NULL CHECK (product_volume_cm3 > 0),
    price_inr NUMERIC(12,2) NOT NULL CHECK (price_inr > 0),
    fragility_level VARCHAR(10) NOT NULL CHECK (fragility_level IN ('Low','Medium','High')),
    temperature_sensitivity VARCHAR(10) NOT NULL CHECK (temperature_sensitivity IN ('Low','Medium','High')),
    moisture_sensitivity VARCHAR(10) NOT NULL CHECK (moisture_sensitivity IN ('Low','Medium','High')),
    shelf_life_days INTEGER NOT NULL CHECK (shelf_life_days > 0),
    packaging_format VARCHAR(20) NOT NULL,
    current_packaging_material VARCHAR(100) NOT NULL
);

ALTER TABLE products
ADD CONSTRAINT fk_material_type
FOREIGN KEY (current_packaging_material)
REFERENCES materials(material_type);



