### API Documentation

#### Base URL 
http://54.206.250.20

#### Authentication 
All protected endpoints require a valid JWT token in the Authorization header:
Authorization: Bearer {access token}
##### POST /auth/register
Register a new user account.
{
  "email": "user@example.com",
  "password": "password@123",
  "username": "Alex",
}
Response (201 Created):
{
  "id": "user_id",
  "email": "user@example.com",
  "username": "John Doe",
  "role": "customer",
  "first_name":'',
  "last_name":'',
  "created_at": "2025-03-31T12:00:00Z"
}

##### POST /auth/login
Authenticate a user and receive JWT tokens.
{
  "email": "user@example.com",
  "password": "password@123"
}
Response (200 OK):

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIs..........................",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzM......................",
    "user": {
        "id": 1,
        "first_name": "",
        "last_name": "",
        "username": "username",
        "email": "user@example.com",
        "role": "customer"
    }
}

##### POST /auth/refresh
Refresh an expired access token.
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}

#### Product Management

Categories
##### GET api/categories/

[{
"id":1,
"title":"Tablets",
"slug":"tablets",
"description":"Latest tablets",
"parent":null
},{"id":2,
"title":"Laptops",
"slug":"laptops",
"description":"Latest tablets",
"parent":null
}]

##### POST api/categories/
Create a new category(admin only:provide token)
{
  "title": "Home appliances",
  "description": "Smart home devices and accessories",
}
Response (201 Created):
{
    "id": 3,
    "title": "Home appliances",
    "slug": "home-appliances",
    "description": "Smart home devices and accessories",
    "parent": null
}

##### GET /api/categories/
Get all categories
[
    {
        "id": 1,
        "title": "Tablets",
        "slug": "tablets",
        "description": "Latest tablets",
        "parent": null
    },
    {
        "id": 2,
        "title": "Laptops",
        "slug": "laptops",
        "description": "Latest tablets",
        "parent": null
    },
    {
        "id": 3,
        "title": "Home appliances",
        "slug": "home-appliances",
        "description": "Smart home devices and accessories",
        "parent": null
    }
]

##### Get /api/categories/{category_slug}/
Get a particular category
{
    "id": 3,
    "title": "Home appliances",
    "slug": "home-appliances",
    "description": "Smart home devices and accessories",
    "parent": null
}

##### PUT /api/categories/{category_id} (Admin only)
update the category

##### DELETE /api/categories/{category_id} (Admin only)
delete category

#### Product
##### GET /api/products
Retrieve all products

##### GET /api/products/{product_slug}/
Retrieve one product
##### POST /api/products (Admin only)
request body:
{
    "title":"Prestige pressure cooker",
    "price" : 2000,
    "category_ids":[3]
}
##### PUT /api/products/{product_id}/ (Admin only)
{
    "title":"Prestige pressure cooker",
    "price" : 2500,
    "category_ids":[3]
}
##### DELETE api/products/{product_id} (Admin only)
Delete product

#### Shopping Cart
##### GET api/cart/ (authenticated user)
retrieve all items in cart

##### POST api/cart/add_item/ (authenticated user)
{
    "product_id": "e7e5f193-8a9b-4d42-abc3-6aa7d5fdf7ba",
    "quantity": 1
}

##### POST /api/cart/remove_item/ (authenticated user)
{
    "product_id": "e7e5f193-8a9b-4d42-abc3-6aa7d5fdf7ba",
    "quantity": 1
}

##### POST /api/order/ (authenticated user)
{
  "shipping_address": "123 Main St, Anytown, AN 12345"
}
##### POST /api/order/19/update-status/ (admin only)
{
    "status":"delivered"
}

##### GET /api/order/
Retrieve all orders

##### GET /api/order/{order_id}/
get specific order

#### Coupon and discount
###### POST /api/coupons/ (admin only)
Adding coupon
{
  "code": "WINTER25",
  "description": "25% off winter sale",
  "discount_percent": 25.00,
  "is_active": true,
  "valid_from": "2025-03-30T00:00:00Z",
  "valid_to": "2025-06-30T23:59:59Z",
  "min_purchase_amount": 100.00,
  "max_discount_amount": 500.00,
  "usage_limit": 1000,
  "usage_count": 0
}

##### POST api/coupons/validate/
coupon validation
{
  "code": "SUMMER25"
  
}










