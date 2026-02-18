"""
Database configuration and connection for EcopackAI
"""
import psycopg2
from psycopg2 import sql
import os

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'ecopack'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Success'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        return None

def query_materials():
    """Get all materials from database grouped by material_type"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cur = conn.cursor()
        # Get materials grouped by material_type
        cur.execute("""
            SELECT material_type, material_name 
            FROM material 
            ORDER BY material_type, material_name
        """)
        
        materials = {}
        for material_type, material_name in cur.fetchall():
            if material_type not in materials:
                materials[material_type] = []
            materials[material_type].append(material_name)
        
        cur.close()
        conn.close()
        return materials
    except Exception as e:
        print(f"Error querying materials: {e}")
        return {}

def query_products():
    """Get all products from database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        # Use SELECT * to avoid column name issues, then map by position
        # Columns: product_id, product_name, sector, strength_score, weight_capacity_score,
        #          barrier_score, biodegradability_score, co2_emission_score, 
        #          recyclability_percent, cost_score, reuse_potential_score
        cur.execute("""
            SELECT * FROM product
            ORDER BY sector, product_name
        """)
        
        products = []
        for row in cur.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'sector': row[2],
                'strength': row[3],
                'weight_capacity': row[4],
                'barrier': row[5],
                'biodegradability': row[6],
                'co2_emission': row[7],
                'recyclability': row[8],
                'cost': row[9],
                'reuse_potential': row[10]
            })
        
        cur.close()
        conn.close()
        return products
    except Exception as e:
        print(f"Error querying products: {e}")
        return []

def test_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        print("✓ Database connection successful")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM material;")
        material_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM product;")
        product_count = cur.fetchone()[0]
        print(f"  Materials: {material_count}")
        print(f"  Products: {product_count}")
        cur.close()
        conn.close()
        return True
    else:
        print("✗ Database connection failed")
        return False

if __name__ == '__main__':
    test_connection()
