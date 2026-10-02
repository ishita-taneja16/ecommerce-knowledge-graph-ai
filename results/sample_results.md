# Sample Questions and Retrieval Results

This document contains the actual execution output of sample natural-language queries against the E-Commerce Knowledge Graph system.

## Question 1: Which products are supplied by Amazon?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "products_by_vendor",
  "parameters": {
    "vendor": "Amazon"
  }
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "success",
  "vendor": "Amazon",
  "results": [
    {
      "product_id": "P001",
      "product_name": "iPhone 15 Pro",
      "price": 999.0,
      "vendor": "Amazon"
    },
    {
      "product_id": "P002",
      "product_name": "MacBook Air M3",
      "price": 1099.0,
      "vendor": "Amazon"
    },
    {
      "product_id": "P005",
      "product_name": "WH-1000XM5 Headphones",
      "price": 399.0,
      "vendor": "Amazon"
    }
  ],
  "count": 3
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** Based on retrieved graph data (3 item(s)): iPhone 15 Pro, MacBook Air M3, WH-1000XM5 Headphones.

---

## Question 2: Which products belong to Apple?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "products_by_brand",
  "parameters": {
    "brand": "Apple"
  }
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "success",
  "brand": "Apple",
  "results": [
    {
      "product_id": "P001",
      "product_name": "iPhone 15 Pro",
      "price": 999.0,
      "brand": "Apple"
    },
    {
      "product_id": "P002",
      "product_name": "MacBook Air M3",
      "price": 1099.0,
      "brand": "Apple"
    },
    {
      "product_id": "P003",
      "product_name": "AirPods Max",
      "price": 549.0,
      "brand": "Apple"
    }
  ],
  "count": 3
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** Based on retrieved graph data (3 item(s)): iPhone 15 Pro, MacBook Air M3, AirPods Max.

---

## Question 3: Which products from Apple are supplied by Amazon?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "products_by_brand_and_vendor",
  "parameters": {
    "brand": "Apple",
    "vendor": "Amazon"
  }
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "success",
  "brand": "Apple",
  "vendor": "Amazon",
  "results": [
    {
      "product_id": "P001",
      "product_name": "iPhone 15 Pro",
      "price": 999.0,
      "brand": "Apple"
    },
    {
      "product_id": "P002",
      "product_name": "MacBook Air M3",
      "price": 1099.0,
      "brand": "Apple"
    }
  ],
  "count": 2
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** Based on retrieved graph data (2 item(s)): iPhone 15 Pro, MacBook Air M3.

---

## Question 4: Which orders were placed by Rahul?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "orders_by_customer",
  "parameters": {
    "customer": "Rahul"
  }
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "success",
  "customer": "Rahul",
  "results": [
    {
      "order_id": "ORD001",
      "order_date": "2026-09-15",
      "customer": "Rahul",
      "items": [
        {
          "product_id": "P001",
          "product_name": "iPhone 15 Pro",
          "quantity": 1
        },
        {
          "product_id": "P002",
          "product_name": "MacBook Air M3",
          "quantity": 1
        }
      ]
    },
    {
      "order_id": "ORD002",
      "order_date": "2026-09-18",
      "customer": "Rahul",
      "items": [
        {
          "product_id": "P005",
          "product_name": "WH-1000XM5 Headphones",
          "quantity": 2
        }
      ]
    }
  ],
  "count": 2
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** Based on retrieved graph data (2 item(s)): ORD001, ORD002.

---

## Question 5: Which products are contained in order ORD001?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "products_by_order",
  "parameters": {
    "order": "ORD001"
  }
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "success",
  "order_id": "ORD001",
  "results": [
    {
      "product_id": "P001",
      "product_name": "iPhone 15 Pro",
      "price": 999.0,
      "quantity": 1
    },
    {
      "product_id": "P002",
      "product_name": "MacBook Air M3",
      "price": 1099.0,
      "quantity": 1
    }
  ],
  "count": 2
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** Based on retrieved graph data (2 item(s)): iPhone 15 Pro, MacBook Air M3.

---

## Question 6: How many banana values are present in the Knowledge Graph?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "banana_values",
  "parameters": {}
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "success",
  "query": "banana",
  "count": 5,
  "results": [
    {
      "node_id": "brand:B005",
      "entity_id": "B005",
      "entity_type": "Brand",
      "name": "banana",
      "value": "banana"
    },
    {
      "node_id": "category:C004",
      "entity_id": "C004",
      "entity_type": "Category",
      "name": "banana",
      "value": "banana"
    },
    {
      "node_id": "vendor:V004",
      "entity_id": "V004",
      "entity_type": "Vendor",
      "name": "banana",
      "value": "banana"
    },
    {
      "node_id": "customer:CU004",
      "entity_id": "CU004",
      "entity_type": "Customer",
      "name": "banana",
      "value": "banana"
    },
    {
      "node_id": "product:P007",
      "entity_id": "P007",
      "entity_type": "Product",
      "name": "banana",
      "value": "banana"
    }
  ]
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** There are exactly 5 'banana' values present in the Knowledge Graph across Brand, Category, Vendor, Customer, and Product entities.

---

## Question 7: Which products are supplied by Walmart?

### 1. Structured Retrieval Request (LLM Intent)
```json
{
  "intent": "products_by_vendor",
  "parameters": {
    "vendor": "Walmart"
  }
}
```

### 2. Retrieved Knowledge Graph Data
```json
{
  "status": "not_found",
  "message": "Vendor 'Walmart' was not found in the Knowledge Graph.",
  "results": [],
  "count": 0
}
```

### 3. Final Grounded Natural Language Answer
> **Answer:** The information is not available in the Knowledge Graph.

---
