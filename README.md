

### Arquitetura:

 - FastAPI
 - PostgreSQL
 - SQLAlchemy
 - PyJWT
 - Requests para chamar a API externa

### 1. Tabelas (entity):

**Customer**
- id (uuid)
- name
- email (unique)
- password_hash 

**WishlistItem**
- id (int)
- customer_id (FK)
- product_id (string)
- unique(customer_id, product_id)

**Token**
- id (int)
- session (string)
- date (timestamp)
- falta definir mais campos

### 2. Endpoints

**Auth**

- POST /auth/login -> retorna JWT

**Customers**

- POST /customers
- GET /customers/{id}
- PATCH /customers/{id}
- DELETE /customers/{id}

**Wishlist**

GET /customers/{id}/wishlist
POST /customers/{id}/wishlist (body: { product_id })
DELETE /customers/{id}/wishlist/{product_id}





 

