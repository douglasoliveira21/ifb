-- =============================================================================
-- Script de inicialização do banco de dados IFB
-- Executar apenas uma vez na primeira configuração
-- =============================================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Verificação
SELECT 'Extensões criadas com sucesso' AS status;
