from api.services.recommendation_service import recommend_material

input_data = {
    "category": "electronics",
    "weight_capacity_upto": 5
}

result = recommend_material(input_data)
print(result)
