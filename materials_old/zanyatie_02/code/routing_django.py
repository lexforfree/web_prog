"""
Django Routing Example
URL patterns and view handlers with different HTTP methods
"""

from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
import json


# Mock database
users_db = {
    1: {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
    2: {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
}
next_id = 3


@require_http_methods(["GET"])
def users_list(request):
    """GET /users/ - Get all users with optional filtering"""
    age_gt = request.GET.get('age_gt')
    search = request.GET.get('search')
    
    users = list(users_db.values())
    
    if age_gt:
        users = [u for u in users if u['age'] > int(age_gt)]
    
    if search:
        users = [u for u in users if search.lower() in u['name'].lower()]
    
    return JsonResponse({"users": users, "count": len(users)})


@require_http_methods(["GET"])
def user_detail(request, user_id):
    """GET /users/{id}/ - Get specific user"""
    user = users_db.get(user_id)
    if not user:
        return HttpResponseNotFound("User not found", status=404)
    return JsonResponse(user)


@require_http_methods(["POST"])
def user_create(request):
    """POST /users/ - Create new user"""
    try:
        data = json.loads(request.body)
        
        # Validation
        name = data.get('name', '')
        email = data.get('email', '')
        age = data.get('age')
        
        if len(name) < 2 or len(name) > 50:
            return JsonResponse(
                {"error": "Name must be 2-50 characters"}, 
                status=400
            )
        
        if '@' not in email:
            return JsonResponse(
                {"error": "Invalid email"}, 
                status=400
            )
        
        if age is None or age < 18 or age > 120:
            return JsonResponse(
                {"error": "Age must be between 18 and 120"}, 
                status=400
            )
        
        # Create user
        global next_id
        new_user = {
            "id": next_id,
            "name": name,
            "email": email,
            "age": age
        }
        users_db[next_id] = new_user
        next_id += 1
        
        return JsonResponse(new_user, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@require_http_methods(["PUT"])
def user_update(request, user_id):
    """PUT /users/{id}/ - Update user"""
    user = users_db.get(user_id)
    if not user:
        return HttpResponseNotFound("User not found", status=404)
    
    try:
        data = json.loads(request.body)
        
        # Update fields
        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            user['email'] = data['email']
        if 'age' in data:
            user['age'] = data['age']
        
        return JsonResponse(user)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@require_http_methods(["DELETE"])
def user_delete(request, user_id):
    """DELETE /users/{id}/ - Delete user"""
    user = users_db.pop(user_id, None)
    if not user:
        return HttpResponseNotFound("User not found", status=404)
    
    return JsonResponse({"message": "User deleted", "id": user_id})


# URL patterns
from django.urls import path

urlpatterns = [
    path('users/', users_list, name='users_list'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('users/create/', user_create, name='user_create'),
    path('users/<int:user_id>/update/', user_update, name='user_update'),
    path('users/<int:user_id>/delete/', user_delete, name='user_delete'),
]
