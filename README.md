# EcopackAI-AI-powere-sustinable-packing-recommendation-system

## Project Theme:

Traditional packaging used in industries and e-commerce heavily relies on non-biodegradable and costly
materials, causing increasing environmental damage and financial inefficiency. Businesses lack intelligent
decision-support systems that can help them evaluate and adopt eco-friendly alternative packaging materials
without compromising durability, product safety, or cost-efficiency.
EcoPackAI is an AI-powered full-stack web platform designed to solve this challenge by recommending optimal
packaging materials based on product attributes, sustainability parameters, and industry standards. The system
uses machine learning models to assess material suitability and predict both environmental impact (carbon
footprint) and cost efficiency. The platform integrates a Business Intelligence (BI) dashboard to provide
actionable sustainability insights and report measurable reductions in environmental impact, helping
organizations make data-driven decisions towards greener supply chains.

# Process: 

## Choosing the dataset:
1. I have searched for the material and product datasets with the attributes that are essential for the project. I searched kaggle and other online resources. 
2. I prepared the datasets of material used for package with attributes Material type, strength ,weight capacity, biodegradable score, co2 released for kg, recylability percentage. 
3. I prepared a dataset for the products that are ordered online with the attributes such as Product name, product category, product weight, product volume, price, fragility level, temperature sensitivity, moisture sensitivity, self life in days, packaging format and the current packing material
4. I made sure that all the values in a column are in the same units
   
## Adding the datasets to the database: 
1. Firstly we are adding the datasets for the database instead of using the datasets directly because we can update the dataset whenever it is required
2. I am using Pgadmin4 for the database and added the datasets into the database server.

## Feature Engineering:
1. Now to get an accurate and precise results from the model we need to have a very good training data without any missing values 
2. So I used python for the pre processing and the datacleaning. when I checked the dataset has the duplicates so I removed the duplictes and cleaned the dataset without any missing and duplicate values
