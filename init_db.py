#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do sistema E-Commerce
Cria as tabelas e dados iniciais necessários
"""

from app import app, db, Usuario, Categoria, Anuncio
from werkzeug.security import generate_password_hash

def criar_tabelas():
    """Criar todas as tabelas do banco de dados"""
    print("Criando tabelas do banco de dados...")
    db.create_all()
    print("✓ Tabelas criadas com sucesso!")

def criar_categorias():
    """Criar categorias padrão do sistema"""
    print("Criando categorias padrão...")
    
    categorias = [
        {
            'nome': 'Eletrônicos',
            'descricao': 'Smartphones, notebooks, tablets, acessórios eletrônicos e gadgets'
        },
        {
            'nome': 'Roupas e Acessórios',
            'descricao': 'Roupas masculinas, femininas, infantis, calçados e acessórios de moda'
        },
        {
            'nome': 'Casa e Jardim',
            'descricao': 'Móveis, decoração, eletrodomésticos, ferramentas e itens para jardim'
        },
        {
            'nome': 'Esportes e Lazer',
            'descricao': 'Equipamentos esportivos, bicicletas, jogos e artigos de lazer'
        },
        {
            'nome': 'Livros e Educação',
            'descricao': 'Livros físicos e digitais, materiais educativos e cursos'
        },
        {
            'nome': 'Veículos',
            'descricao': 'Carros, motos, bicicletas e acessórios automotivos'
        },
        {
            'nome': 'Beleza e Saúde',
            'descricao': 'Cosméticos, produtos de beleza, suplementos e equipamentos de saúde'
        },
        {
            'nome': 'Música e Instrumentos',
            'descricao': 'Instrumentos musicais, equipamentos de som e acessórios musicais'
        }
    ]
    
    for cat_data in categorias:
        # Verificar se categoria já existe
        categoria_existente = Categoria.query.filter_by(nome=cat_data['nome']).first()
        if not categoria_existente:
            categoria = Categoria(
                nome=cat_data['nome'],
                descricao=cat_data['descricao']
            )
            db.session.add(categoria)
    
    db.session.commit()
    print(f"✓ {len(categorias)} categorias criadas com sucesso!")

def criar_usuario_admin():
    """Criar usuário administrador padrão"""
    print("Criando usuário administrador...")
    
    # Verificar se admin já existe
    admin_existente = Usuario.query.filter_by(email='admin@ecommerce.com').first()
    if admin_existente:
        print("✓ Usuário admin já existe!")
        return admin_existente
    
    admin = Usuario(
        nome='Administrador do Sistema',
        email='admin@ecommerce.com',
        senha=generate_password_hash('admin123'),
        telefone='(11) 99999-9999',
        endereco='Rua da Administração, 123 - Centro, São Paulo, SP - 01000-000'
    )
    
    db.session.add(admin)
    db.session.commit()
    print("✓ Usuário admin criado com sucesso!")
    print("   Email: admin@ecommerce.com")
    print("   Senha: admin123")
    
    return admin

def criar_usuarios_exemplo():
    """Criar alguns usuários de exemplo"""
    print("Criando usuários de exemplo...")
    
    usuarios_exemplo = [
        {
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'joao123',
            'telefone': '(11) 98888-1111',
            'endereco': 'Rua das Flores, 456 - Jardim Paulista, São Paulo, SP'
        },
        {
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'senha': 'maria123',
            'telefone': '(11) 97777-2222',
            'endereco': 'Av. Paulista, 789 - Bela Vista, São Paulo, SP'
        },
        {
            'nome': 'Pedro Costa',
            'email': 'pedro@email.com',
            'senha': 'pedro123',
            'telefone': '(11) 96666-3333',
            'endereco': 'Rua Augusta, 321 - Vila Madalena, São Paulo, SP'
        }
    ]
    
    usuarios_criados = []
    for user_data in usuarios_exemplo:
        # Verificar se usuário já existe
        usuario_existente = Usuario.query.filter_by(email=user_data['email']).first()
        if not usuario_existente:
            usuario = Usuario(
                nome=user_data['nome'],
                email=user_data['email'],
                senha=generate_password_hash(user_data['senha']),
                telefone=user_data['telefone'],
                endereco=user_data['endereco']
            )
            db.session.add(usuario)
            usuarios_criados.append(usuario)
    
    db.session.commit()
    print(f"✓ {len(usuarios_criados)} usuários de exemplo criados!")
    return usuarios_criados

def criar_anuncios_exemplo(admin, usuarios):
    """Criar anúncios de exemplo"""
    print("Criando anúncios de exemplo...")
    
    # Buscar categorias
    cat_eletronicos = Categoria.query.filter_by(nome='Eletrônicos').first()
    cat_roupas = Categoria.query.filter_by(nome='Roupas e Acessórios').first()
    cat_casa = Categoria.query.filter_by(nome='Casa e Jardim').first()
    cat_esportes = Categoria.query.filter_by(nome='Esportes e Lazer').first()
    cat_livros = Categoria.query.filter_by(nome='Livros e Educação').first()
    cat_veiculos = Categoria.query.filter_by(nome='Veículos').first()
    
    anuncios_exemplo = [
        # Anúncios do Admin
        {
            'usuario': admin,
            'categoria': cat_eletronicos,
            'titulo': 'iPhone 13 Pro 256GB Azul Sierra',
            'descricao': 'iPhone 13 Pro em excelente estado de conservação. Sempre usado com película e capinha. Bateria com 92% de saúde. Acompanha carregador original, cabo lightning e caixinha. Motivo da venda: upgrade para iPhone 14.',
            'preco': 3500.00,
            'quantidade': 1
        },
        {
            'usuario': admin,
            'categoria': cat_casa,
            'titulo': 'Mesa de Jantar 6 Lugares com Cadeiras',
            'descricao': 'Mesa de jantar em madeira maciça cor mogno com 6 cadeiras estofadas em tecido bege. Dimensões: 1,80m x 1,00m. Muito bem conservada, apenas alguns riscos mínimos de uso. Ideal para sala de jantar ou varanda gourmet.',
            'preco': 1200.00,
            'quantidade': 1
        },
        {
            'usuario': admin,
            'categoria': cat_eletronicos,
            'titulo': 'Notebook Gamer Acer Nitro 5',
            'descricao': 'Notebook Gamer Acer Nitro 5 com Intel Core i5, 16GB RAM, SSD 512GB, GeForce GTX 1650. Ideal para jogos e trabalho pesado. Acompanha carregador e mouse gamer de brinde. Estado impecável.',
            'preco': 2800.00,
            'quantidade': 1
        }
    ]
    
    # Adicionar anúncios dos outros usuários se existirem
    if usuarios:
        for i, usuario in enumerate(usuarios[:3]):  # Apenas os 3 primeiros
            anuncios_exemplo.extend([
                {
                    'usuario': usuario,
                    'categoria': cat_roupas,
                    'titulo': f'Jaqueta de Couro Masculina Tamanho {"M" if i == 0 else "G" if i == 1 else "P"}',
                    'descricao': f'Jaqueta de couro legítimo em excelente estado. Cor preta, muito elegante e confortável. Tamanho {"M" if i == 0 else "G" if i == 1 else "P"}. Pouco usada, sem defeitos.',
                    'preco': 299.90 + (i * 50),
                    'quantidade': 1
                },
                {
                    'usuario': usuario,
                    'categoria': cat_esportes,
                    'titulo': f'Bicicleta {"Mountain Bike" if i == 0 else "Speed" if i == 1 else "Urbana"} Aro 26',
                    'descricao': f'Bicicleta {"para trilhas" if i == 0 else "para velocidade" if i == 1 else "para cidade"} em ótimo estado. Revisada recentemente, pneus novos, freios ajustados. Ideal para {"aventuras" if i == 0 else "exercícios" if i == 1 else "transporte"}.',
                    'preco': 600.00 + (i * 200),
                    'quantidade': 1
                }
            ])
    
    anuncios_criados = []
    for anuncio_data in anuncios_exemplo:
        # Verificar se anúncio similar já existe
        anuncio_existente = Anuncio.query.filter_by(
            titulo=anuncio_data['titulo'],
            id_usuario=anuncio_data['usuario'].id_usuario
        ).first()
        
        if not anuncio_existente:
            anuncio = Anuncio(
                id_usuario=anuncio_data['usuario'].id_usuario,
                id_categoria=anuncio_data['categoria'].id_categoria,
                titulo=anuncio_data['titulo'],
                descricao=anuncio_data['descricao'],
                preco=anuncio_data['preco'],
                quantidade_disponivel=anuncio_data['quantidade']
            )
            db.session.add(anuncio)
            anuncios_criados.append(anuncio)
    
    db.session.commit()
    print(f"✓ {len(anuncios_criados)} anúncios de exemplo criados!")

def main():
    """Função principal de inicialização"""
    print("=" * 50)
    print("INICIALIZAÇÃO DO SISTEMA E-COMMERCE")
    print("=" * 50)
    
    with app.app_context():
        try:
            # 1. Criar tabelas
            criar_tabelas()
            
            # 2. Criar categorias
            criar_categorias()
            
            # 3. Criar usuário admin
            admin = criar_usuario_admin()
            
            # 4. Criar usuários de exemplo
            usuarios_exemplo = criar_usuarios_exemplo()
            
            # 5. Criar anúncios de exemplo
            criar_anuncios_exemplo(admin, usuarios_exemplo)
            
            print("\n" + "=" * 50)
            print("INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 50)
            print("\n🎉 Sistema pronto para uso!")
            print("\n📊 Dados criados:")
            print(f"   • {Categoria.query.count()} categorias")
            print(f"   • {Usuario.query.count()} usuários")
            print(f"   • {Anuncio.query.count()} anúncios")
            
            print("\n🔑 Credenciais de acesso:")
            print("   Admin: admin@ecommerce.com / admin123")
            print("   Usuário teste 1: joao@email.com / joao123")
            print("   Usuário teste 2: maria@email.com / maria123")
            print("   Usuário teste 3: pedro@email.com / pedro123")
            
            print("\n🚀 Para iniciar o sistema:")
            print("   python app.py")
            print("   Acesse: http://localhost:5000")
            
        except Exception as e:
            print(f"\n❌ Erro durante a inicialização: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        exit(1)