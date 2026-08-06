-- =============================================================================
-- Seed: Roles e permissões base do IFB
-- =============================================================================

-- Roles
INSERT INTO roles (id, name, display_name, description, is_active, created_at, updated_at)
VALUES
    (uuid_generate_v4(), 'visitor', 'Visitante', 'Acesso público básico', true, NOW(), NOW()),
    (uuid_generate_v4(), 'user', 'Usuário Cadastrado', 'Pode seguir políticos e receber alertas', true, NOW(), NOW()),
    (uuid_generate_v4(), 'analyst', 'Analista', 'Pode revisar e validar informações', true, NOW(), NOW()),
    (uuid_generate_v4(), 'journalist', 'Jornalista Parceiro', 'Acesso a relatórios avançados', true, NOW(), NOW()),
    (uuid_generate_v4(), 'admin', 'Administrador', 'Gerenciamento completo da plataforma', true, NOW(), NOW()),
    (uuid_generate_v4(), 'superadmin', 'Superadministrador', 'Controle total do sistema', true, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

SELECT 'Roles criadas com sucesso' AS status;
