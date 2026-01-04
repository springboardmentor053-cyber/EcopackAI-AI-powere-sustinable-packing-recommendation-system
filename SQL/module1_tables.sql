/*SQL Code for Creation of Material Table*/

create table material(
	material_id int primary key,
	material_name varchar(50),
	material_type varchar(50),
	strength_score int,
	weight_capacity_score int,
	biodegradability_score int,
	co2_emission_score int,
	recyclability_percent int
)

/*SQL Code for verifying the Material Table*/

select * from material;

/*SQL Code Creation of Product Table*/

create table product (
	product_id int primary key,
	product_name varchar(70),
	sector varchar(40),
	main_packaging_material varchar(70),
	strength_score int,
	weight_capacity_score int,
	barrier_score int,
	biodegradability_score int,
	co2_emission_score int,
	recyclability_score int,
	cost_per_unit int,
	reuse_potential_score int
)

/*SQL Code for Verifying the Product Table*/

select * from product;