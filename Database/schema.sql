CREATE TABLE materials (
    material_id SERIAL PRIMARY KEY,
    material_name VARCHAR(100) NOT NULL,
    material_type VARCHAR(100),
    strength_score FLOAT CHECK (strength_score >= 0),
    weight_capacity_kg FLOAT,
    biodegradability_score FLOAT CHECK (biodegradability_score BETWEEN 0 AND 1),
    recyclability_percent INT CHECK (recyclability_percent BETWEEN 0 AND 100),
    co2_emission_kg FLOAT,
    cost_per_kg FLOAT,
    water_resistance VARCHAR(50),
    food_safe BOOLEAN,
    industry_usage VARCHAR(100),
    sustainability_rating VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_categories (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_weight_kg FLOAT,
    dimensions_cm VARCHAR(50),
    fragile BOOLEAN,
    food_grade_required BOOLEAN,
    moisture_sensitive BOOLEAN,
    temperature_sensitive BOOLEAN,
    preferred_material_type VARCHAR(100),
    max_packaging_cost FLOAT,
    sustainability_priority VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE material_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES product_categories(product_id) ON DELETE CASCADE,
    material_id INT REFERENCES materials(material_id) ON DELETE CASCADE,
    predicted_cost FLOAT,
    predicted_co2 FLOAT,
    suitability_score FLOAT,
    rank INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
