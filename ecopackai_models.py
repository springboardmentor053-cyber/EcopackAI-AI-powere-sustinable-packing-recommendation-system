class Material:
    material_id: str
    material_type: str
    strength_mpa: float
    weight_capacity: float
    co2_emission_per_kg: float
    biodegradability_score: int
    recyclability_pct: float
    cost_inr_per_kg: float
    material_category: str


class Product:
    product_id: str
    product_name: str
    product_category: str
    product_weight_g: float
    product_volume_cm3: float
    price_inr: float
    fragility_level: int
    temperature_sensitivity: bool
    moisture_sensitivity: bool
    shelf_life_days: int
    packaging_format: str

    # Foreign Key reference
    current_packaging_material: Material
