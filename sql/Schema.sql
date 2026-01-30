CREATE TABLE materials (
    material_id            VARCHAR(10) PRIMARY KEY,
    material_type          VARCHAR(100) UNIQUE NOT NULL,
    material_category      VARCHAR(50) NOT NULL,
    strength_level         VARCHAR(10) NOT NULL
        CHECK (strength_level IN ('Low', 'Medium', 'High')),
    weight_capacity        NUMERIC(10,3) NOT NULL
        CHECK (weight_capacity > 0),
    biodegradability_score SMALLINT NOT NULL
        CHECK (biodegradability_score BETWEEN 0 AND 10),
    recyclability_pct      NUMERIC(5,2) NOT NULL
        CHECK (recyclability_pct BETWEEN 0 AND 100),
    co2_emission_kg_per_kg NUMERIC(10,3) NOT NULL
        CHECK (co2_emission_kg_per_kg >= 0),
    cost_inr_per_kg        NUMERIC(10,2) NOT NULL
        CHECK (cost_inr_per_kg > 0),
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendation_logs (
    log_id                SERIAL PRIMARY KEY,
    product_weight_g      NUMERIC(10,2) NOT NULL,
    strength_level        VARCHAR(10) NOT NULL,
    biodegradability_req  SMALLINT NOT NULL,
    recyclability_req     NUMERIC(5,2) NOT NULL,
    recommended_material  VARCHAR(100) NOT NULL,
    predicted_cost_inr    NUMERIC(10,2) NOT NULL,
    predicted_co2_impact  NUMERIC(10,3) NOT NULL,
    model_version         VARCHAR(50) NOT NULL,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


