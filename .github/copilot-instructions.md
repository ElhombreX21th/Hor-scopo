<!-- Copilot Instructions for SeuFuturo Project -->

# SeuFuturo - Instruções do Projeto

## Visão Geral
Este é um projeto SaaS de horóscopo com backend em FastAPI e frontend responsivo. Inclui sistema de planos (Basic, Premium, VIP) com diferentes níveis de acesso a conteúdo.

## Estrutura do Projeto
- **backend/**: API FastAPI com lógica de planos e consumo de API de astrologia
- **frontend/**: Interface HTML/CSS responsiva com Tailwind CSS
- **requirements.txt**: Dependências Python

## Stack Tecnológico
- Backend: Python, FastAPI, Uvicorn
- Frontend: HTML5, CSS3, Tailwind CSS, JavaScript
- Database: Pronto para integração (atualmente simulado)

## Configuração Inicial

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
API ativa em: http://127.0.0.1:8000

### Frontend
Abra `frontend/index.html` no navegador ou:
```bash
python -m http.server 8001 --directory frontend
```

## Rotas Principais

### API Endpoints
- `GET /api/horoscopo` - Retorna horóscopo filtrado por signo e plano
- `GET /docs` - Interface Swagger UI para testes

## Funcionalidades

### Planos
- **Basic**: Previsão diária (grátis)
- **Premium**: Amor + Carreira (R$ 49,90/mês)
- **VIP**: Tudo + Conselho Místico (R$ 150,00/mês)

### Signos
Todos os 12 signos do zodíaco com previsões personalizadas

## Integração com API Real
Para conectar com API real de astrologia:
1. Edita `backend/main.py`
2. Substitui `ASTRO_API_URL` e `API_KEY`
3. Implementa lógica em `buscar_dados_astrologicos()`

## Próximas Etapas
- [ ] Integrar com API real de astrologia
- [ ] Adicionar autenticação de usuários
- [ ] Implementar base de dados
- [ ] Sistema de pagamento (Stripe)
- [ ] Deploy em produção

## Convenções de Código
- Python: PEP 8
- Frontend: Tailwind CSS para estilos
- Nomeação clara e descritiva

## Contato & Suporte
Projeto desenvolvido em maio de 2026.
