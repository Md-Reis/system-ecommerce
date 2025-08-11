from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import os

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'seu-secret-key-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
db = SQLAlchemy(app)

@app.context_processor
def inject_user_functions():
    def is_logged_in():
        return 'user_id' in session
    return dict(is_logged_in=is_logged_in)

# ============== MODELOS DO BANCO DE DADOS ==============

class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    anuncios = db.relationship('Anuncio', backref='proprietario', lazy=True)
    perguntas = db.relationship('Pergunta', backref='usuario_pergunta', lazy=True)
    respostas = db.relationship('Resposta', backref='usuario_resposta', lazy=True)
    compras = db.relationship('Compra', foreign_keys='Compra.id_usuario_comprador', backref='comprador', lazy=True)
    vendas = db.relationship('Compra', foreign_keys='Compra.id_usuario_vendedor', backref='vendedor', lazy=True)
    favoritos = db.relationship('Favorito', backref='usuario_favorito', lazy=True)

class Categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    anuncios = db.relationship('Anuncio', backref='categoria', lazy=True)

class Anuncio(db.Model):
    id_anuncio = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    quantidade_disponivel = db.Column(db.Integer, default=1)
    data_publicacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    perguntas = db.relationship('Pergunta', backref='anuncio', lazy=True)
    compras = db.relationship('Compra', backref='anuncio', lazy=True)
    favoritos = db.relationship('Favorito', backref='anuncio_favorito', lazy=True)

class Pergunta(db.Model):
    id_pergunta = db.Column(db.Integer, primary_key=True)
    id_anuncio = db.Column(db.Integer, db.ForeignKey('anuncio.id_anuncio'), nullable=False)
    id_usuario_pergunta = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    texto_pergunta = db.Column(db.Text, nullable=False)
    data_pergunta = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    resposta = db.relationship('Resposta', backref='pergunta', uselist=False)

class Resposta(db.Model):
    id_resposta = db.Column(db.Integer, primary_key=True)
    id_pergunta = db.Column(db.Integer, db.ForeignKey('pergunta.id_pergunta'), nullable=False)
    id_usuario_resposta = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    texto_resposta = db.Column(db.Text, nullable=False)
    data_resposta = db.Column(db.DateTime, default=datetime.utcnow)

class Compra(db.Model):
    id_compra = db.Column(db.Integer, primary_key=True)
    id_anuncio = db.Column(db.Integer, db.ForeignKey('anuncio.id_anuncio'), nullable=False)
    id_usuario_comprador = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_usuario_vendedor = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    preco_total = db.Column(db.Numeric(10, 2), nullable=False)
    data_compra = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pendente')

class Favorito(db.Model):
    id_favorito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_anuncio = db.Column(db.Integer, db.ForeignKey('anuncio.id_anuncio'), nullable=False)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)

# ============== ROTAS DA APLICAÇÃO ==============

@app.route('/')
def home():
    """Página inicial com lista de anúncios"""
    anuncios = Anuncio.query.filter_by(ativo=True).order_by(Anuncio.data_publicacao.desc()).limit(20).all()
    categorias = Categoria.query.filter_by(ativo=True).all()
    return render_template('index.html', anuncios=anuncios, categorias=categorias)

# ============== ROTAS DE USUÁRIO ==============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login do usuário"""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id_usuario
            session['usuario_nome'] = usuario.nome
            flash('Login realizado com sucesso!')
            return redirect(url_for('home'))
        else:
            flash('Email ou senha incorretos!')
    
    return render_template('usuario/login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        telefone = request.form.get('telefone', '')
        endereco = request.form.get('endereco', '')
        
        # Verificar se email já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Este email já está em uso!')
            return render_template('usuario/cadastro.html')
        
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            telefone=telefone,
            endereco=endereco
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('usuario/cadastro.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('home'))

@app.route('/perfil')
def perfil():
    """Visualizar perfil do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página!')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('usuario/perfil.html', usuario=usuario)

@app.route('/perfil/editar', methods=['GET', 'POST'])
def editar_perfil():
    """Editar perfil do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.telefone = request.form.get('telefone', '')
        usuario.endereco = request.form.get('endereco', '')
        
        # Se uma nova senha foi fornecida
        nova_senha = request.form.get('nova_senha')
        if nova_senha:
            usuario.senha = generate_password_hash(nova_senha)
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!')
        return redirect(url_for('perfil'))
    
    return render_template('usuario/editar_perfil.html', usuario=usuario)

# ============== ROTAS DE ANÚNCIOS ==============

@app.route('/anuncios')
def listar_anuncios():
    """Listar todos os anúncios"""
    categoria_id = request.args.get('categoria')
    busca = request.args.get('busca', '')
    
    query = Anuncio.query.filter_by(ativo=True)
    
    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)
    
    if busca:
        query = query.filter(Anuncio.titulo.contains(busca))
    
    anuncios = query.order_by(Anuncio.data_publicacao.desc()).all()
    categorias = Categoria.query.filter_by(ativo=True).all()
    
    return render_template('anuncio/listar.html', anuncios=anuncios, categorias=categorias)

@app.route('/anuncio/<int:id>')
def detalhes_anuncio(id):
    """Detalhes de um anúncio específico"""
    anuncio = Anuncio.query.get_or_404(id)
    perguntas = Pergunta.query.filter_by(id_anuncio=id).order_by(Pergunta.data_pergunta.desc()).all()
    
    # Verificar se está nos favoritos (se usuário logado)
    favorito = False
    if 'usuario_id' in session:
        favorito = Favorito.query.filter_by(
            id_usuario=session['usuario_id'], 
            id_anuncio=id
        ).first() is not None
    
    return render_template('anuncio/detalhes.html', anuncio=anuncio, perguntas=perguntas, favorito=favorito)

@app.route('/meus-anuncios')
def meus_anuncios():
    """Listar anúncios do usuário logado"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página!')
        return redirect(url_for('login'))
    
    anuncios = Anuncio.query.filter_by(id_usuario=session['usuario_id']).order_by(Anuncio.data_publicacao.desc()).all()
    return render_template('anuncio/meus_anuncios.html', anuncios=anuncios)

@app.route('/anuncio/novo', methods=['GET', 'POST'])
def novo_anuncio():
    """Criar novo anúncio"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para criar anúncios!')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])
        quantidade = int(request.form['quantidade'])
        categoria_id = int(request.form['categoria'])
        
        novo_anuncio = Anuncio(
            id_usuario=session['usuario_id'],
            id_categoria=categoria_id,
            titulo=titulo,
            descricao=descricao,
            preco=preco,
            quantidade_disponivel=quantidade
        )
        
        db.session.add(novo_anuncio)
        db.session.commit()
        
        flash('Anúncio criado com sucesso!')
        return redirect(url_for('meus_anuncios'))
    
    categorias = Categoria.query.filter_by(ativo=True).all()
    return render_template('anuncio/novo.html', categorias=categorias)

@app.route('/anuncio/<int:id>/editar', methods=['GET', 'POST'])
def editar_anuncio(id):
    """Editar um anúncio existente"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    anuncio = Anuncio.query.get_or_404(id)
    
    # Verificar se é o proprietário do anúncio
    if anuncio.id_usuario != session['usuario_id']:
        flash('Você só pode editar seus próprios anúncios!')
        return redirect(url_for('meus_anuncios'))
    
    if request.method == 'POST':
        anuncio.titulo = request.form['titulo']
        anuncio.descricao = request.form['descricao']
        anuncio.preco = float(request.form['preco'])
        anuncio.quantidade_disponivel = int(request.form['quantidade'])
        anuncio.id_categoria = int(request.form['categoria'])
        
        db.session.commit()
        
        flash('Anúncio atualizado com sucesso!')
        return redirect(url_for('meus_anuncios'))
    
    categorias = Categoria.query.filter_by(ativo=True).all()
    return render_template('anuncio/editar.html', anuncio=anuncio, categorias=categorias)

@app.route('/anuncio/<int:id>/excluir', methods=['POST'])
def excluir_anuncio(id):
    """Excluir (desativar) um anúncio"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    anuncio = Anuncio.query.get_or_404(id)
    
    # Verificar se é o proprietário do anúncio
    if anuncio.id_usuario != session['usuario_id']:
        flash('Você só pode excluir seus próprios anúncios!')
        return redirect(url_for('meus_anuncios'))
    
    anuncio.ativo = False
    db.session.commit()
    
    flash('Anúncio excluído com sucesso!')
    return redirect(url_for('meus_anuncios'))

# ============== ROTAS DE PERGUNTAS ==============

@app.route('/anuncio/<int:id>/pergunta', methods=['POST'])
def fazer_pergunta(id):
    """Fazer uma pergunta em um anúncio"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para fazer perguntas!')
        return redirect(url_for('login'))
    
    texto_pergunta = request.form['pergunta']
    
    nova_pergunta = Pergunta(
        id_anuncio=id,
        id_usuario_pergunta=session['usuario_id'],
        texto_pergunta=texto_pergunta
    )
    
    db.session.add(nova_pergunta)
    db.session.commit()
    
    flash('Pergunta enviada com sucesso!')
    return redirect(url_for('detalhes_anuncio', id=id))

@app.route('/pergunta/<int:id>/responder', methods=['POST'])
def responder_pergunta(id):
    """Responder uma pergunta"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    pergunta = Pergunta.query.get_or_404(id)
    
    # Verificar se é o proprietário do anúncio
    if pergunta.anuncio.id_usuario != session['usuario_id']:
        flash('Você só pode responder perguntas dos seus anúncios!')
        return redirect(url_for('home'))
    
    texto_resposta = request.form['resposta']
    
    nova_resposta = Resposta(
        id_pergunta=id,
        id_usuario_resposta=session['usuario_id'],
        texto_resposta=texto_resposta
    )
    
    db.session.add(nova_resposta)
    db.session.commit()
    
    flash('Resposta enviada com sucesso!')
    return redirect(url_for('detalhes_anuncio', id=pergunta.id_anuncio))

# ============== ROTAS DE COMPRAS ==============

@app.route('/anuncio/<int:id>/comprar', methods=['POST'])
def comprar_anuncio(id):
    """Realizar compra de um anúncio"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para comprar!')
        return redirect(url_for('login'))
    
    anuncio = Anuncio.query.get_or_404(id)
    quantidade = int(request.form.get('quantidade', 1))
    
    # Verificar disponibilidade
    if anuncio.quantidade_disponivel < quantidade:
        flash('Quantidade não disponível!')
        return redirect(url_for('detalhes_anuncio', id=id))
    
    # Verificar se não está comprando do próprio anúncio
    if anuncio.id_usuario == session['usuario_id']:
        flash('Você não pode comprar do seu próprio anúncio!')
        return redirect(url_for('detalhes_anuncio', id=id))
    
    preco_total = float(anuncio.preco) * quantidade
    
    nova_compra = Compra(
        id_anuncio=id,
        id_usuario_comprador=session['usuario_id'],
        id_usuario_vendedor=anuncio.id_usuario,
        quantidade=quantidade,
        preco_unitario=anuncio.preco,
        preco_total=preco_total
    )
    
    # Atualizar quantidade disponível
    anuncio.quantidade_disponivel -= quantidade
    
    db.session.add(nova_compra)
    db.session.commit()
    
    flash('Compra realizada com sucesso!')
    return redirect(url_for('minhas_compras'))

@app.route('/compras')
def minhas_compras():
    """Histórico de compras do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    compras = Compra.query.filter_by(id_usuario_comprador=session['usuario_id']).order_by(Compra.data_compra.desc()).all()
    return render_template('compra/minhas_compras.html', compras=compras)

@app.route('/vendas')
def minhas_vendas():
    """Histórico de vendas do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    vendas = Compra.query.filter_by(id_usuario_vendedor=session['usuario_id']).order_by(Compra.data_compra.desc()).all()
    return render_template('compra/minhas_vendas.html', vendas=vendas)

@app.route('/compra/<int:id>/status', methods=['POST'])
def atualizar_status_compra(id):
    """Atualizar status de uma compra (pelo vendedor)"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    compra = Compra.query.get_or_404(id)
    
    # Verificar se é o vendedor
    if compra.id_usuario_vendedor != session['usuario_id']:
        flash('Você só pode atualizar o status das suas vendas!')
        return redirect(url_for('minhas_vendas'))
    
    novo_status = request.form['status']
    compra.status = novo_status
    
    db.session.commit()
    
    flash('Status da compra atualizado com sucesso!')
    return redirect(url_for('minhas_vendas'))



# ============== ROTAS DE FAVORITOS ==============

@app.route('/anuncio/<int:id>/favoritar', methods=['POST'])
def favoritar_anuncio(id):
    """Adicionar/remover anúncio dos favoritos"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para favoritar!')
        return redirect(url_for('login'))
    
    # Verificar se já está nos favoritos
    favorito_existente = Favorito.query.filter_by(
        id_usuario=session['usuario_id'],
        id_anuncio=id
    ).first()
    
    if favorito_existente:
        # Remover dos favoritos
        db.session.delete(favorito_existente)
        flash('Anúncio removido dos favoritos!')
    else:
        # Adicionar aos favoritos
        novo_favorito = Favorito(
            id_usuario=session['usuario_id'],
            id_anuncio=id
        )
        db.session.add(novo_favorito)
        flash('Anúncio adicionado aos favoritos!')
    
    db.session.commit()
    return redirect(url_for('detalhes_anuncio', id=id))

@app.route('/favoritos')
def meus_favoritos():
    """Listar anúncios favoritos do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    favoritos = db.session.query(Favorito, Anuncio).join(
        Anuncio, Favorito.id_anuncio == Anuncio.id_anuncio
    ).filter(
        Favorito.id_usuario == session['usuario_id'],
        Anuncio.ativo == True
    ).order_by(Favorito.data_adicao.desc()).all()
    
    return render_template('favorito/meus_favoritos.html', favoritos=favoritos)

# ============== ROTAS DE CATEGORIA =================

@app.route('/categoria/<int:id>')
def anuncios_categoria(id):
    # Buscar categoria pelo ID
    categoria = Categoria.query.get(id)

    # Buscar anúncios dessa categoria
    anuncios = Anuncio.query.filter_by(id_categoria=id).all()

    return render_template(
        'categoria.html',
        categoria_nome=categoria.nome,
        anuncios=anuncios
    )

# ============== ROTAS ADMINISTRATIVAS ==============

@app.route('/admin/categorias')
def admin_categorias():
    """Gerenciar categorias (funcionalidade administrativa básica)"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    categorias = Categoria.query.all()
    return render_template('admin/categorias.html', categorias=categorias)

@app.route('/admin/categoria/nova', methods=['GET', 'POST'])
def nova_categoria():
    """Criar nova categoria"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        
        nova_categoria = Categoria(
            nome=nome,
            descricao=descricao
        )
        
        db.session.add(nova_categoria)
        db.session.commit()
        
        flash('Categoria criada com sucesso!')
        return redirect(url_for('admin_categorias'))
    
    return render_template('admin/nova_categoria.html')

# ============== FUNCÕES UTILITÁRIAS ==============

def init_db():
    """Inicializar banco de dados e criar tabelas"""
    db.create_all()
    
    # Criar categorias padrão se não existirem
    if not Categoria.query.first():
        categorias_padrao = [
            {'nome': 'Eletrônicos', 'descricao': 'Dispositivos eletrônicos e acessórios'},
            {'nome': 'Roupas e Acessórios', 'descricao': 'Vestuário e acessórios de moda'},
            {'nome': 'Casa e Jardim', 'descricao': 'Itens para casa e jardim'},
            {'nome': 'Esportes e Lazer', 'descricao': 'Equipamentos esportivos e de lazer'},
            {'nome': 'Livros e Educação', 'descricao': 'Livros e materiais educacionais'},
            {'nome': 'Veículos', 'descricao': 'Carros, motos e acessórios automotivos'},
            {'nome': 'Móveis', 'descricao': 'Móveis e decoração'},
            {'nome': 'Outros', 'descricao': 'Diversos itens'}
        ]
        
        for categoria_data in categorias_padrao:
            categoria = Categoria(
                nome=categoria_data['nome'],
                descricao=categoria_data['descricao']
            )
            db.session.add(categoria)
        
        db.session.commit()

# ============== FILTROS PARA TEMPLATES ==============

@app.template_filter('currency')
def currency_filter(value):
    """Filtro para formatar valores monetários"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

@app.template_filter('datetime')
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    """Filtro para formatar datas"""
    if isinstance(value, str):
        return value
    return value.strftime(format)

# ============== CONTEXTO GLOBAL PARA TEMPLATES ==============

@app.context_processor
def utility_processor():
    """Adicionar funções utilitárias aos templates"""
    return dict(
        len=len,
        enumerate=enumerate,
        datetime=datetime
    )

# ============== EXECUÇÃO DA APLICAÇÃO ==============

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    # Configurações para desenvolvimento
    app.run(debug=True, host='0.0.0.0', port=5000)