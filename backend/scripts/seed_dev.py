import asyncio
import os
from app.core.database import AsyncSessionLocal
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.utils.security import hash_password

async def seed_roles_and_admin() -> None:
    async with AsyncSessionLocal() as db:
        role_repo = RoleRepository(db)
        
        # Standard application roles
        roles_to_seed = [
            {"code": "SUPER_ADMIN", "name": "Super Administrator", "is_active": True},
            {"code": "ADMIN", "name": "Administrator", "is_active": True},
            {"code": "MANAGER", "name": "Manager", "is_active": True},
            {"code": "EMPLOYEE", "name": "Employee", "is_active": True},
            {"code": "VIEWER", "name": "Viewer", "is_active": True},
        ]
        
        for role_data in roles_to_seed:
            existing_role = await role_repo.get_by_code(role_data["code"])
            if not existing_role:
                print(f"Creating role: {role_data['code']}")
                await role_repo.create(obj_in=role_data)
            else:
                print(f"Role already exists: {role_data['code']}")

        # Seed SUPER_ADMIN user
        super_admin_email = os.getenv("DEV_SUPER_ADMIN_EMAIL")
        super_admin_password = os.getenv("DEV_SUPER_ADMIN_PASSWORD")

        if super_admin_email and super_admin_password:
            user_repo = UserRepository(db)
            
            existing_super_admin = await user_repo.get_by_email(super_admin_email.lower())
            if not existing_super_admin:
                super_admin_role = await role_repo.get_by_code("SUPER_ADMIN")
                if super_admin_role:
                    print(f"Creating development SUPER_ADMIN user: {super_admin_email}")
                    user_data = {
                        "employee_code": "SA-001",
                        "full_name": "Development Super Admin",
                        "email": super_admin_email.lower(),
                        "password_hash": hash_password(super_admin_password),
                        "role_id": super_admin_role.id,
                        "is_verified": True,
                        "is_active": True,
                        "created_by": None
                    }
                    await user_repo.create(obj_in=user_data)
            else:
                print(f"Development SUPER_ADMIN user already exists: {super_admin_email}")
        else:
            print("Skipping development SUPER_ADMIN user creation. Set DEV_SUPER_ADMIN_EMAIL and DEV_SUPER_ADMIN_PASSWORD.")

async def main() -> None:
    print("Starting development seed process...")
    await seed_roles_and_admin()
    print("Seed process completed.")

if __name__ == "__main__":
    asyncio.run(main())
