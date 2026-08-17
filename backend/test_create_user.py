import asyncio
from app.core.database import async_session_maker
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.services.user import UserService
from app.utils.security import hash_password

async def main():
    async with async_session_maker() as db:
        role_repo = RoleRepository(db)
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)
        
        # Get employee role
        employee_role = await role_repo.get_by_code("EMPLOYEE")
        if not employee_role:
            print("Employee role not found")
            return
            
        # Create user
        user = await user_repo.get_by_email("minetest@gmail.com")
        if not user:
            print("Creating minetest user")
            await user_service.create({
                "employee_code": "MINE-001",
                "full_name": "Mine Test",
                "email": "minetest@gmail.com",
                "password": "minetest@123",
                "role_id": employee_role.id,
                "is_verified": True,
                "is_active": True
            }, current_user=None)
            print("User created")
        else:
            print("User already exists")
            # Update password
            user.password_hash = hash_password("minetest@123")
            await db.commit()
            print("Password updated")

if __name__ == "__main__":
    asyncio.run(main())
