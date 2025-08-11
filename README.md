# Sistema E-Commerce Flask

Sistema de e-commerce desenvolvido em Flask para compra e venda de produtos online.

## Funcionalidades

- ✅ **Usuários**: Cadastro, login, perfil
- ✅ **Anúncios**: Criar, editar, visualizar, categorizar
- ✅ **Perguntas e Respostas**: Sistema de Q&A nos anúncios
- ✅ **Compras**: Sistema de compra direta (sem carrinho)
- ✅ **Favoritos**: Lista de anúncios favoritos
- ✅ **Relatórios**: Relatórios de compras e vendas
- ✅ **Categorias**: Organização por categorias

## Tecnologias

- **Backend**: Python 3.8+ com Flask
- **Banco de Dados**: SQLite (desenvolvimento)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **ORM**: SQLAlchemy

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd ecommerce-flask
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute a aplicação:
```bash
python app.py
```

6. Acesse no navegador:
```
http://localhost:5000
```

## Dados de Teste

O sistema cria automaticamente:
- **Usuário admin**: admin@ecommerce.com / admin123
- **6 categorias**: Eletrônicos, Roupas, Casa e Jardim, Esportes, Livros, Veículos
- **3 anúncios de exemplo**

## Estrutura do Projeto

```
ecommerce-flask/
│
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── README.md              # Documentação
├── ecommerce.db           # Banco de dados SQLite (criado automaticamente)
└── templates/             # Templates HTML
    ├── base.html          # Template base
    ├── index.html         # Página inicial
    ├── usuario/           # Templates de usuário
        ├── cadastro.html  # Template cadastro
        ├── login.html     # Template login
    ├── anuncio/           # Templates de anúncios
        ├── detalhes.html  # Template detalhes
        ├── listar.html    # Template listar
        ├── novo.html      # Template novo
    ├── compra/            # Templates de compras
    ├── favorito/          # Templates de favoritos
    ├── relatorio/         # Templates de relatórios
    └── categoria/         # Templates de categorias
        ├── categoria.html # Template categoria
```

## Funcionalidades Implementadas

### 1. Sistema de Usuários
- Cadastro com validação de email único
- Login seguro com hash de senhas
- Perfil do usuário
- Controle de sessão

### 2. Gestão de Anúncios
- Criar novos anúncios
- Editar anúncios próprios
- Listar anúncios por categoria
- Busca por texto
- Sistema de disponibilidade

### 3. Perguntas e Respostas
- Usuários podem fazer perguntas
- Proprietários podem responder
- Histórico de perguntas por anúncio

### 4. Sistema de Compras
- Compra direta (sem carrinho)
- Controle de estoque
- Histórico de compras
- Histórico de vendas

### 5. Sistema de Favoritos
- Adicionar/remover favoritos
- Lista personalizada de favoritos
- Interface intuitiva

### 6. Relatórios
- Relatório detalhado de compras
- Relatório detalhado de vendas
- Estatísticas pessoais

## Rotas Principais

### Públicas
- `GET /` - Página inicial
- `GET /anuncios` - Lista de anúncios
- `GET /anuncio/<id>` - Detalhes do anúncio
- `GET /categoria/<id>` - Anúncios por categoria

### Autenticação
- `GET/POST /login` - Login
- `GET/POST /cadastro` - Cadastro
- `GET /logout` - Logout

### Área do Usuário (Requer Login)
- `GET /perfil` - Visualizar perfil
- `GET /meus-anuncios` - Meus anúncios
- `GET/POST /anuncio/novo` - Criar anúncio
- `POST /anuncio/<id>/pergunta` - Fazer pergunta
- `POST /pergunta/<id>/responder` - Responder pergunta
- `POST /anuncio/<id>/comprar` - Comprar produto
- `POST /anuncio/<id>/favoritar` - Adicionar aos favoritos
- `GET /favoritos` - Lista de favoritos
- `GET /compras` - Histórico de compras
- `GET /vendas` - Histórico de vendas
- `GET /relatorio-compras` - Relatório de compras
- `GET /relatorio-vendas` - Relatório de vendas

## Modelo de Dados

### Principais Entidades

- **Usuario**: Dados dos usuários (nome, email, senha, etc.)
- **Categoria**: Categorias dos produtos
- **Anuncio**: Anúncios de produtos
- **Pergunta**: Perguntas feitas nos anúncios
- **Resposta**: Respostas às perguntas
- **Compra**: Registro de compras realizadas
- **Favorito**: Lista de favoritos dos usuários

### Relacionamentos

- Um usuário pode ter vários anúncios
- Um anúncio pertence a uma categoria
- Um anúncio pode ter várias perguntas
- Uma pergunta pode ter uma resposta
- Um usuário pode fazer várias compras
- Um usuário pode ter vários favoritos

## Segurança

- Senhas criptografadas com hash
- Validação de autenticação em rotas protegidas
- Validação de propriedade de anúncios
- Prevenção de compras próprias
- Sessões seguras

## Possíveis Melhorias Futuras

- Sistema de avaliação de usuários
- Upload de imagens para anúncios
- Sistema de mensagens privadas
- Integração com gateways de pagamento
- Sistema de frete
- App mobile
- API REST

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é para fins acadêmicos e de aprendizado.

## Contato


Desenvolvido como projeto acadêmico para disciplina de Frameworks para Desenvolvimento de Software.

