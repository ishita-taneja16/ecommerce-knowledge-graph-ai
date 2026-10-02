import networkx as nx
from src.data_loader import load_ecommerce_data

def build_ecommerce_graph(data_dir=None):
    """
    Builds a NetworkX MultiDiGraph representing the e-commerce knowledge graph.
    
    Entities (Nodes):
    - Brand (prefix: 'brand:')
    - Category (prefix: 'category:')
    - Vendor (prefix: 'vendor:')
    - Customer (prefix: 'customer:')
    - Product (prefix: 'product:')
    - Order (prefix: 'order:')
    
    Relationships (Edges):
    - Customer -> PLACED -> Order
    - Order -> CONTAINS -> Product
    - Product -> BELONGS_TO_BRAND -> Brand
    - Product -> IN_CATEGORY -> Category
    - Vendor -> SUPPLIES -> Product
    """
    data = load_ecommerce_data(data_dir)
    G = nx.MultiDiGraph()
    
    # 1. Add Brands
    for _, row in data["brands"].iterrows():
        node_id = f"brand:{row['brand_id']}"
        G.add_node(
            node_id,
            id=row['brand_id'],
            entity_type="Brand",
            name=row['brand_name'],
            value=row['brand_name'],
            country=row.get('country', '')
        )
        
    # 2. Add Categories
    for _, row in data["categories"].iterrows():
        node_id = f"category:{row['category_id']}"
        G.add_node(
            node_id,
            id=row['category_id'],
            entity_type="Category",
            name=row['category_name'],
            value=row['category_name'],
            description=row.get('description', '')
        )
        
    # 3. Add Vendors
    for _, row in data["vendors"].iterrows():
        node_id = f"vendor:{row['vendor_id']}"
        G.add_node(
            node_id,
            id=row['vendor_id'],
            entity_type="Vendor",
            name=row['vendor_name'],
            value=row['vendor_name'],
            location=row.get('location', '')
        )
        
    # 4. Add Customers
    for _, row in data["customers"].iterrows():
        node_id = f"customer:{row['customer_id']}"
        G.add_node(
            node_id,
            id=row['customer_id'],
            entity_type="Customer",
            name=row['customer_name'],
            value=row['customer_name'],
            email=row.get('email', ''),
            city=row.get('city', '')
        )
        
    # 5. Add Products and their relationships with Brand, Category, Vendor
    for _, row in data["products"].iterrows():
        prod_node_id = f"product:{row['product_id']}"
        G.add_node(
            prod_node_id,
            id=row['product_id'],
            entity_type="Product",
            name=row['product_name'],
            value=row['product_name'],
            price=float(row['price']) if 'price' in row else 0.0
        )
        
        # Product -> BELONGS_TO_BRAND -> Brand
        brand_node_id = f"brand:{row['brand_id']}"
        if G.has_node(brand_node_id):
            G.add_edge(prod_node_id, brand_node_id, relation="BELONGS_TO_BRAND")
            
        # Product -> IN_CATEGORY -> Category
        cat_node_id = f"category:{row['category_id']}"
        if G.has_node(cat_node_id):
            G.add_edge(prod_node_id, cat_node_id, relation="IN_CATEGORY")
            
        # Vendor -> SUPPLIES -> Product
        vendor_node_id = f"vendor:{row['vendor_id']}"
        if G.has_node(vendor_node_id):
            G.add_edge(vendor_node_id, prod_node_id, relation="SUPPLIES")
            
    # 6. Add Orders and relationships with Customer & Product
    for _, row in data["orders"].iterrows():
        order_node_id = f"order:{row['order_id']}"
        if not G.has_node(order_node_id):
            G.add_node(
                order_node_id,
                id=row['order_id'],
                entity_type="Order",
                name=row['order_id'],
                value=row['order_id'],
                order_date=row.get('order_date', '')
            )
            
        # Customer -> PLACED -> Order
        cust_node_id = f"customer:{row['customer_id']}"
        if G.has_node(cust_node_id):
            # Add edge only if not already connected
            already_placed = False
            for _, v, data in G.out_edges(cust_node_id, data=True):
                if v == order_node_id and data.get("relation") == "PLACED":
                    already_placed = True
                    break
            if not already_placed:
                G.add_edge(cust_node_id, order_node_id, relation="PLACED")
            
        # Order -> CONTAINS -> Product
        prod_node_id = f"product:{row['product_id']}"
        if G.has_node(prod_node_id):
            G.add_edge(
                order_node_id,
                prod_node_id,
                relation="CONTAINS",
                quantity=int(row.get('quantity', 1))
            )
            
    return G
