import networkx as nx

class GraphRetriever:
    """
    Retrieval layer that queries and traverses the NetworkX Knowledge Graph.
    Returns structured data for the LLM grounding layer.
    """
    
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    def _find_nodes_by_type_and_name(self, entity_type: str, name: str):
        """Helper to find nodes matching entity_type and name (case-insensitive)."""
        matches = []
        name_lower = name.strip().lower()
        for node, data in self.graph.nodes(data=True):
            if data.get("entity_type", "").lower() == entity_type.lower():
                node_name = str(data.get("name", "")).strip().lower()
                node_id = str(data.get("id", "")).strip().lower()
                if node_name == name_lower or node_id == name_lower:
                    matches.append((node, data))
        return matches

    def get_products_by_brand(self, brand_name: str) -> dict:
        """Finds all products associated with a specific brand."""
        brand_nodes = self._find_nodes_by_type_and_name("Brand", brand_name)
        if not brand_nodes:
            return {
                "status": "not_found",
                "message": f"Brand '{brand_name}' was not found in the Knowledge Graph.",
                "results": [],
                "count": 0
            }
            
        products = []
        for brand_node, brand_data in brand_nodes:
            # Find incoming edges with relation="BELONGS_TO_BRAND" (Product -> Brand)
            for u, v, k, edge_data in self.graph.in_edges(brand_node, keys=True, data=True):
                if edge_data.get("relation") == "BELONGS_TO_BRAND":
                    prod_data = self.graph.nodes[u]
                    products.append({
                        "product_id": prod_data.get("id"),
                        "product_name": prod_data.get("name"),
                        "price": prod_data.get("price"),
                        "brand": brand_data.get("name")
                    })
                    
        if not products:
            return {
                "status": "empty",
                "message": f"No products found for brand '{brand_name}'.",
                "results": [],
                "count": 0
            }
            
        return {
            "status": "success",
            "brand": brand_nodes[0][1].get("name"),
            "results": products,
            "count": len(products)
        }

    def get_products_by_vendor(self, vendor_name: str) -> dict:
        """Finds all products supplied by a specific vendor."""
        vendor_nodes = self._find_nodes_by_type_and_name("Vendor", vendor_name)
        if not vendor_nodes:
            return {
                "status": "not_found",
                "message": f"Vendor '{vendor_name}' was not found in the Knowledge Graph.",
                "results": [],
                "count": 0
            }
            
        products = []
        for vendor_node, vendor_data in vendor_nodes:
            # Find outgoing edges with relation="SUPPLIES" (Vendor -> Product)
            for u, v, k, edge_data in self.graph.out_edges(vendor_node, keys=True, data=True):
                if edge_data.get("relation") == "SUPPLIES":
                    prod_data = self.graph.nodes[v]
                    products.append({
                        "product_id": prod_data.get("id"),
                        "product_name": prod_data.get("name"),
                        "price": prod_data.get("price"),
                        "vendor": vendor_data.get("name")
                    })
                    
        if not products:
            return {
                "status": "empty",
                "message": f"No products found supplied by vendor '{vendor_name}'.",
                "results": [],
                "count": 0
            }
            
        return {
            "status": "success",
            "vendor": vendor_nodes[0][1].get("name"),
            "results": products,
            "count": len(products)
        }

    def get_products_by_brand_and_vendor(self, brand_name: str, vendor_name: str) -> dict:
        """Finds products from a specific brand supplied by a specific vendor."""
        brand_res = self.get_products_by_brand(brand_name)
        vendor_res = self.get_products_by_vendor(vendor_name)
        
        if brand_res["status"] != "success":
            return brand_res
        if vendor_res["status"] != "success":
            return vendor_res
            
        brand_prod_ids = {p["product_id"]: p for p in brand_res["results"]}
        vendor_prod_ids = {p["product_id"]: p for p in vendor_res["results"]}
        
        common_ids = set(brand_prod_ids.keys()).intersection(set(vendor_prod_ids.keys()))
        
        results = [brand_prod_ids[pid] for pid in common_ids]
        
        if not results:
            return {
                "status": "empty",
                "message": f"No products from brand '{brand_name}' are supplied by vendor '{vendor_name}'.",
                "results": [],
                "count": 0
            }
            
        return {
            "status": "success",
            "brand": brand_res.get("brand"),
            "vendor": vendor_res.get("vendor"),
            "results": results,
            "count": len(results)
        }

    def get_orders_by_customer(self, customer_name: str) -> dict:
        """Finds all orders placed by a specific customer."""
        cust_nodes = self._find_nodes_by_type_and_name("Customer", customer_name)
        if not cust_nodes:
            return {
                "status": "not_found",
                "message": f"Customer '{customer_name}' was not found in the Knowledge Graph.",
                "results": [],
                "count": 0
            }
            
        orders = []
        seen_order_ids = set()
        for cust_node, cust_data in cust_nodes:
            # Outgoing edges from Customer -> PLACED -> Order
            for u, v, k, edge_data in self.graph.out_edges(cust_node, keys=True, data=True):
                if edge_data.get("relation") == "PLACED":
                    order_data = self.graph.nodes[v]
                    oid = order_data.get("id")
                    if oid in seen_order_ids:
                        continue
                    seen_order_ids.add(oid)
                    
                    # Also fetch items in this order
                    items = []
                    for o_u, o_v, o_k, o_edge in self.graph.out_edges(v, keys=True, data=True):
                        if o_edge.get("relation") == "CONTAINS":
                            item_data = self.graph.nodes[o_v]
                            items.append({
                                "product_id": item_data.get("id"),
                                "product_name": item_data.get("name"),
                                "quantity": o_edge.get("quantity", 1)
                            })
                            
                    orders.append({
                        "order_id": order_data.get("id"),
                        "order_date": order_data.get("order_date"),
                        "customer": cust_data.get("name"),
                        "items": items
                    })
                    
        if not orders:
            return {
                "status": "empty",
                "message": f"No orders found for customer '{customer_name}'.",
                "results": [],
                "count": 0
            }
            
        return {
            "status": "success",
            "customer": cust_nodes[0][1].get("name"),
            "results": orders,
            "count": len(orders)
        }

    def get_products_by_order(self, order_id: str) -> dict:
        """Finds all products contained in a specific order."""
        order_nodes = self._find_nodes_by_type_and_name("Order", order_id)
        if not order_nodes:
            return {
                "status": "not_found",
                "message": f"Order '{order_id}' was not found in the Knowledge Graph.",
                "results": [],
                "count": 0
            }
            
        products = []
        for order_node, order_data in order_nodes:
            # Order -> CONTAINS -> Product
            for u, v, k, edge_data in self.graph.out_edges(order_node, keys=True, data=True):
                if edge_data.get("relation") == "CONTAINS":
                    prod_data = self.graph.nodes[v]
                    products.append({
                        "product_id": prod_data.get("id"),
                        "product_name": prod_data.get("name"),
                        "price": prod_data.get("price"),
                        "quantity": edge_data.get("quantity", 1)
                    })
                    
        if not products:
            return {
                "status": "empty",
                "message": f"Order '{order_id}' contains no products.",
                "results": [],
                "count": 0
            }
            
        return {
            "status": "success",
            "order_id": order_nodes[0][1].get("id"),
            "results": products,
            "count": len(products)
        }

    def get_banana_values(self) -> dict:
        """
        Retrieves all graph nodes/values containing 'banana'.
        Fulfills strict Requirement 8 (finding all 5 banana entities/values).
        """
        banana_entries = []
        for node, data in self.graph.nodes(data=True):
            name_val = str(data.get("name", "")).lower()
            value_val = str(data.get("value", "")).lower()
            if name_val == "banana" or value_val == "banana":
                banana_entries.append({
                    "node_id": node,
                    "entity_id": data.get("id"),
                    "entity_type": data.get("entity_type"),
                    "name": data.get("name"),
                    "value": data.get("value")
                })
                
        return {
            "status": "success",
            "query": "banana",
            "count": len(banana_entries),
            "results": banana_entries
        }

    def get_products_by_category(self, category_name: str) -> dict:
        """Finds all products in a specific category."""
        cat_nodes = self._find_nodes_by_type_and_name("Category", category_name)
        if not cat_nodes:
            return {
                "status": "not_found",
                "message": f"Category '{category_name}' was not found in the Knowledge Graph.",
                "results": [],
                "count": 0
            }
            
        products = []
        for cat_node, cat_data in cat_nodes:
            for u, v, k, edge_data in self.graph.in_edges(cat_node, keys=True, data=True):
                if edge_data.get("relation") == "IN_CATEGORY":
                    prod_data = self.graph.nodes[u]
                    products.append({
                        "product_id": prod_data.get("id"),
                        "product_name": prod_data.get("name"),
                        "price": prod_data.get("price"),
                        "category": cat_data.get("name")
                    })
                    
        return {
            "status": "success",
            "category": cat_nodes[0][1].get("name"),
            "results": products,
            "count": len(products)
        }

    def search_graph_by_keyword(self, keyword: str) -> dict:
        """Fuzzy fallback search for keyword matching across any node in the graph."""
        kw_lower = keyword.strip().lower()
        matches = []
        for node, data in self.graph.nodes(data=True):
            for k, v in data.items():
                if kw_lower in str(v).lower():
                    matches.append({
                        "node_id": node,
                        "entity_id": data.get("id"),
                        "entity_type": data.get("entity_type"),
                        "matched_field": k,
                        "matched_value": str(v),
                        "data": data
                    })
                    break
        
        if not matches:
            return {
                "status": "not_found",
                "message": f"No entries found in the Knowledge Graph matching keyword '{keyword}'.",
                "results": [],
                "count": 0
            }
            
        return {
            "status": "success",
            "keyword": keyword,
            "results": matches,
            "count": len(matches)
        }
