"""CLI para operações administrativas do IFB."""

import asyncio
import getpass
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.security import hash_password, validate_password_strength


settings = get_settings()


async def create_superadmin() -> None:
    """Cria superadministrador via CLI segura."""
    print("\n=== Instituto Fiscaliza Brasil ===")
    print("Criação de Superadministrador\n")

    full_name = input("Nome completo: ").strip()
    if not full_name:
        print("Erro: Nome é obrigatório.")
        sys.exit(1)

    email = input("E-mail: ").strip().lower()
    if not email or "@" not in email:
        print("Erro: E-mail inválido.")
        sys.exit(1)

    password = getpass.getpass("Senha (mín. 10 caracteres): ")
    errors = validate_password_strength(password)
    if errors:
        print(f"Erro: {errors[0]}")
        sys.exit(1)

    confirm = getpass.getpass("Confirme a senha: ")
    if password != confirm:
        print("Erro: As senhas não conferem.")
        sys.exit(1)

    # Connect to database
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    async with session_factory() as db:
        from app.models.user import Role, User, UserRole

        # Check if email already exists
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            print(f"Erro: E-mail '{email}' já está cadastrado.")
            sys.exit(1)

        # Get or create superadmin role
        role_result = await db.execute(
            select(Role).where(Role.name == "superadmin")
        )
        role = role_result.scalar_one_or_none()
        if not role:
            role = Role(
                name="superadmin",
                display_name="Superadministrador",
                description="Controle total do sistema",
            )
            db.add(role)
            await db.flush()

        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_active=True,
            is_verified=True,
            must_change_password=False,
        )
        db.add(user)
        await db.flush()

        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            assigned_by="CLI bootstrap",
        )
        db.add(user_role)

        # Capture ID before commit closes session
        user_id = user.id
        user_email = email

        await db.commit()

        print(f"\n✓ Superadministrador criado com sucesso!")
        print(f"  E-mail: {user_email}")
        print(f"  ID: {user_id}")
        print(f"\n⚠ Ative o MFA no primeiro login.")

    await engine.dispose()


async def seed_roles() -> None:
    """Cria roles e permissões padrão."""
    print("\n=== Seed: Roles e Permissões ===\n")

    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    async with session_factory() as db:
        from app.models.user import Permission, Role, RolePermission

        # Define roles
        roles_data = [
            ("visitor", "Visitante", "Acesso público básico"),
            ("user", "Usuário Cadastrado", "Pode seguir políticos e receber alertas"),
            ("analyst", "Analista", "Pode revisar e validar informações"),
            ("journalist", "Jornalista Parceiro", "Acesso a relatórios avançados"),
            ("admin", "Administrador", "Gerenciamento completo da plataforma"),
            ("superadmin", "Superadministrador", "Controle total do sistema"),
        ]

        # Define permissions
        permissions_data = [
            ("politicians.read", "Visualizar políticos", "politicians", "read"),
            ("politicians.create", "Criar políticos", "politicians", "create"),
            ("politicians.update", "Editar políticos", "politicians", "update"),
            ("politicians.delete", "Remover políticos", "politicians", "delete"),
            ("news.read", "Visualizar notícias", "news", "read"),
            ("news.review", "Revisar notícias", "news", "review"),
            ("news.publish", "Publicar notícias", "news", "publish"),
            ("promises.read", "Visualizar promessas", "promises", "read"),
            ("promises.review", "Revisar promessas", "promises", "review"),
            ("users.read", "Visualizar usuários", "users", "read"),
            ("users.manage", "Gerenciar usuários", "users", "manage"),
            ("roles.read", "Visualizar roles", "roles", "read"),
            ("roles.manage", "Gerenciar roles", "roles", "manage"),
            ("audit.read", "Visualizar auditoria", "audit", "read"),
            ("system.manage", "Gerenciar sistema", "system", "manage"),
            ("donations.read", "Visualizar doações", "donations", "read"),
            ("donations.manage", "Gerenciar doações", "donations", "manage"),
            ("transparency.manage", "Gerenciar transparência", "transparency", "manage"),
        ]

        # Create roles
        created_roles = {}
        for name, display, desc in roles_data:
            existing = await db.execute(select(Role).where(Role.name == name))
            role = existing.scalar_one_or_none()
            if not role:
                role = Role(name=name, display_name=display, description=desc)
                db.add(role)
                await db.flush()
                print(f"  ✓ Role criada: {name}")
            else:
                print(f"  - Role já existe: {name}")
            created_roles[name] = role

        # Create permissions
        created_perms = {}
        for name, desc, resource, action in permissions_data:
            existing = await db.execute(select(Permission).where(Permission.name == name))
            perm = existing.scalar_one_or_none()
            if not perm:
                perm = Permission(name=name, description=desc, resource=resource, action=action)
                db.add(perm)
                await db.flush()
                print(f"  ✓ Permissão criada: {name}")
            created_perms[name] = perm

        # Assign permissions to roles
        role_perms = {
            "user": ["politicians.read", "news.read", "promises.read"],
            "analyst": [
                "politicians.read", "politicians.update", "news.read",
                "news.review", "promises.read", "promises.review",
            ],
            "journalist": [
                "politicians.read", "news.read", "promises.read", "audit.read",
            ],
            "admin": [
                "politicians.read", "politicians.create", "politicians.update",
                "politicians.delete", "news.read", "news.review", "news.publish",
                "promises.read", "promises.review", "users.read", "users.manage",
                "roles.read", "audit.read", "donations.read", "donations.manage",
                "transparency.manage",
            ],
            "superadmin": [p[0] for p in permissions_data],  # All permissions
        }

        for role_name, perm_names in role_perms.items():
            role = created_roles.get(role_name)
            if not role:
                continue
            for perm_name in perm_names:
                perm = created_perms.get(perm_name)
                if not perm:
                    continue
                existing = await db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id,
                    )
                )
                if not existing.scalar_one_or_none():
                    db.add(RolePermission(role_id=role.id, permission_id=perm.id))

        await db.commit()
        print("\n✓ Seed concluído!")

    await engine.dispose()


async def seed_political_reference_data() -> None:
    """Cria partidos e cargos políticos brasileiros."""
    print("\n=== Seed: Partidos e Cargos Políticos ===\n")

    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    async with session_factory() as db:
        from app.models.politician import PoliticalParty, PoliticalPosition

        # Brazilian political parties (active as of 2026)
        parties = [
            ("MDB", "Movimento Democrático Brasileiro", 15),
            ("PT", "Partido dos Trabalhadores", 13),
            ("PSDB", "Partido da Social Democracia Brasileira", 45),
            ("PP", "Progressistas", 11),
            ("PDT", "Partido Democrático Trabalhista", 12),
            ("UNIÃO", "União Brasil", 44),
            ("PL", "Partido Liberal", 22),
            ("PSB", "Partido Socialista Brasileiro", 40),
            ("REPUBLICANOS", "Republicanos", 10),
            ("PSD", "Partido Social Democrático", 55),
            ("PODE", "Podemos", 20),
            ("PSOL", "Partido Socialismo e Liberdade", 50),
            ("CIDADANIA", "Cidadania", 23),
            ("PV", "Partido Verde", 43),
            ("AVANTE", "Avante", 70),
            ("SOLIDARIEDADE", "Solidariedade", 77),
            ("NOVO", "Partido Novo", 30),
            ("REDE", "Rede Sustentabilidade", 18),
            ("PCdoB", "Partido Comunista do Brasil", 65),
            ("PSC", "Partido Social Cristão", 20),
            ("DC", "Democracia Cristã", 27),
            ("PMB", "Partido da Mulher Brasileira", 35),
            ("PRTB", "Partido Renovador Trabalhista Brasileiro", 28),
            ("PCB", "Partido Comunista Brasileiro", 21),
            ("PCO", "Partido da Causa Operária", 29),
            ("PSTU", "Partido Socialista dos Trabalhadores Unificado", 16),
            ("UP", "Unidade Popular", 80),
            ("AGIR", "Agir", 36),
            ("PMN", "Partido da Mobilização Nacional", 33),
            ("PROS", "Partido Republicano da Ordem Social", 90),
        ]

        created_parties = 0
        for acronym, name, number in parties:
            existing = await db.execute(
                select(PoliticalParty).where(PoliticalParty.acronym == acronym)
            )
            if not existing.scalar_one_or_none():
                db.add(PoliticalParty(
                    name=name, acronym=acronym, electoral_number=number, status="active",
                ))
                created_parties += 1

        # Political positions
        positions = [
            # Federal
            ("Presidente da República", "federal", "executivo", "nacional"),
            ("Vice-Presidente", "federal", "executivo", "nacional"),
            ("Deputado Federal", "federal", "legislativo", "estadual"),
            ("Senador", "federal", "legislativo", "estadual"),
            ("Ministro de Estado", "federal", "executivo", "nacional"),
            # State
            ("Governador", "estadual", "executivo", "estadual"),
            ("Vice-Governador", "estadual", "executivo", "estadual"),
            ("Deputado Estadual", "estadual", "legislativo", "estadual"),
            ("Deputado Distrital", "distrital", "legislativo", "distrital"),
            # Municipal
            ("Prefeito", "municipal", "executivo", "municipal"),
            ("Vice-Prefeito", "municipal", "executivo", "municipal"),
            ("Vereador", "municipal", "legislativo", "municipal"),
        ]

        created_positions = 0
        for name, level, branch, scope in positions:
            existing = await db.execute(
                select(PoliticalPosition).where(
                    PoliticalPosition.name == name,
                    PoliticalPosition.government_level == level,
                )
            )
            if not existing.scalar_one_or_none():
                db.add(PoliticalPosition(
                    name=name, government_level=level, branch=branch, scope=scope,
                ))
                created_positions += 1

        await db.commit()
        print(f"  ✓ {created_parties} partidos criados")
        print(f"  ✓ {created_positions} cargos criados")
        print("\n✓ Seed de dados de referência concluído!")

    await engine.dispose()


def main() -> None:
    """Ponto de entrada do CLI."""
    if len(sys.argv) < 2:
        print("Uso: python -m app.cli <comando>")
        print("Comandos:")
        print("  create-superadmin              - Cria superadministrador")
        print("  seed-roles                     - Cria roles e permissões padrão")
        print("  seed-political-reference-data  - Cria partidos e cargos")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create-superadmin":
        asyncio.run(create_superadmin())
    elif command == "seed-roles":
        asyncio.run(seed_roles())
    elif command == "seed-political-reference-data":
        asyncio.run(seed_political_reference_data())
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
