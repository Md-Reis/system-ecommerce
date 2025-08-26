from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_, and_, func

import os

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'seu-secret-key-aqui'

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://MarceloReis:pythonany@MarceloReis.mysql.pythonanywhere-services.com/MarceloReis$ecommerce'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
db = SQLAlchemy(app)

@app.context_processor
def inject_user_functions():
    def is_logged_in():
        return 'usuario_id' in session
    
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
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    resposta = db.relationship('Resposta', backref='pergunta', uselist=False)

class Resposta(db.Model):
    id_resposta = db.Column(db.Integer, primary_key=True)
    id_pergunta = db.Column(db.Integer, db.ForeignKey('pergunta.id_pergunta'), nullable=False)
    id_usuario_resposta = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    texto_resposta = db.Column(db.Text, nullable=False)
    data_resposta = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

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
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)

class Favorito(db.Model):
    id_favorito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_anuncio = db.Column(db.Integer, db.ForeignKey('anuncio.id_anuncio'), nullable=False)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)

# ============== ROTAS DA APLICAÇÃO ==============


@app.route('/')
def home():
    """Página inicial com lista de anúncios e categorias"""
    anuncios = Anuncio.query.filter_by(ativo=True).order_by(Anuncio.data_publicacao.desc()).limit(20).all()
    categorias = Categoria.query.filter_by(ativo=True).order_by(Categoria.nome).all()
    return render_template('index.html', anuncios=anuncios, categorias=categorias)


# ============== ROTAS DE PERGUNTAS ==============

@app.route('/anuncio/<int:id>/pergunta', methods=['POST'])
def fazer_pergunta(id):
    """Fazer uma pergunta em um anúncio"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para fazer perguntas!')
        return redirect(url_for('login'))
    
    anuncio = Anuncio.query.get_or_404(id)
    
    # Verificar se não está perguntando no próprio anúncio
    if anuncio.id_usuario == session['usuario_id']:
        flash('Você não pode fazer perguntas no seu próprio anúncio!')
        return redirect(url_for('detalhes_anuncio', id=id))
    
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

@app.route('/minhas-perguntas')
def minhas_perguntas():
    """Listar perguntas feitas pelo usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    perguntas = db.session.query(Pergunta, Anuncio).join(
        Anuncio, Pergunta.id_anuncio == Anuncio.id_anuncio
    ).filter(
        Pergunta.id_usuario_pergunta == session['usuario_id'],
        Pergunta.ativo == True
    ).order_by(Pergunta.data_pergunta.desc()).all()
    
    return render_template('pergunta/minhas_perguntas.html', perguntas=perguntas)

@app.route('/perguntas-recebidas')
def perguntas_recebidas():
    """Listar perguntas recebidas nos anúncios do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    perguntas = db.session.query(Pergunta, Anuncio).join(
        Anuncio, Pergunta.id_anuncio == Anuncio.id_anuncio
    ).filter(
        Anuncio.id_usuario == session['usuario_id'],
        Pergunta.ativo == True
    ).order_by(Pergunta.data_pergunta.desc()).all()
    
    return render_template('pergunta/perguntas_recebidas.html', perguntas=perguntas)

@app.route('/pergunta/<int:id>/editar', methods=['GET', 'POST'])
def editar_pergunta(id):
    """Editar uma pergunta"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    pergunta = Pergunta.query.get_or_404(id)
    
    # Verificar se é o autor da pergunta
    if pergunta.id_usuario_pergunta != session['usuario_id']:
        flash('Você só pode editar suas próprias perguntas!')
        return redirect(url_for('minhas_perguntas'))
    
    # Verificar se já foi respondida
    if pergunta.resposta:
        flash('Não é possível editar perguntas que já foram respondidas!')
        return redirect(url_for('minhas_perguntas'))
    
    if request.method == 'POST':
        pergunta.texto_pergunta = request.form['pergunta']
        pergunta.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        flash('Pergunta atualizada com sucesso!')
        return redirect(url_for('minhas_perguntas'))
    
    return render_template('pergunta/editar.html', pergunta=pergunta)

@app.route('/pergunta/<int:id>/excluir', methods=['GET', 'POST'])
def excluir_pergunta(id):
    """Excluir uma pergunta"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    pergunta = Pergunta.query.get_or_404(id)
    
    # Verificar se é o autor da pergunta
    if pergunta.id_usuario_pergunta != session['usuario_id']:
        flash('Você só pode excluir suas próprias perguntas!')
        return redirect(url_for('minhas_perguntas'))
    
    if request.method == 'POST':
        # Se tem resposta, desativar também
        if pergunta.resposta:
            pergunta.resposta.ativo = False
        
        pergunta.ativo = False
        db.session.commit()
        
        flash('Pergunta excluída com sucesso!')
        return redirect(url_for('minhas_perguntas'))
    
    return render_template('pergunta/confirmar_exclusao.html', pergunta=pergunta)

# ============== ROTAS DE RESPOSTAS ==============

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
    
    # Verificar se já foi respondida
    if pergunta.resposta:
        flash('Esta pergunta já foi respondida!')
        return redirect(url_for('detalhes_anuncio', id=pergunta.id_anuncio))
    
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

@app.route('/minhas-respostas')
def minhas_respostas():
    """Listar respostas dadas pelo usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    respostas = db.session.query(Resposta, Pergunta, Anuncio).join(
        Pergunta, Resposta.id_pergunta == Pergunta.id_pergunta
    ).join(
        Anuncio, Pergunta.id_anuncio == Anuncio.id_anuncio
    ).filter(
        Resposta.id_usuario_resposta == session['usuario_id'],
        Resposta.ativo == True
    ).order_by(Resposta.data_resposta.desc()).all()
    
    return render_template('resposta/minhas_respostas.html', respostas=respostas)

@app.route('/resposta/<int:id>/editar', methods=['GET', 'POST'])
def editar_resposta(id):
    """Editar uma resposta"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    resposta = Resposta.query.get_or_404(id)
    
    # Verificar se é o autor da resposta
    if resposta.id_usuario_resposta != session['usuario_id']:
        flash('Você só pode editar suas próprias respostas!')
        return redirect(url_for('minhas_respostas'))
    
    if request.method == 'POST':
        resposta.texto_resposta = request.form['resposta']
        resposta.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        flash('Resposta atualizada com sucesso!')
        return redirect(url_for('minhas_respostas'))
    
    return render_template('resposta/editar.html', resposta=resposta)

@app.route('/resposta/<int:id>/excluir', methods=['GET', 'POST'])
def excluir_resposta(id):
    """Excluir uma resposta"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    resposta = Resposta.query.get_or_404(id)
    
    # Verificar se é o autor da resposta
    if resposta.id_usuario_resposta != session['usuario_id']:
        flash('Você só pode excluir suas próprias respostas!')
        return redirect(url_for('minhas_respostas'))
    
    if request.method == 'POST':
        resposta.ativo = False
        db.session.commit()
        
        flash('Resposta excluída com sucesso!')
        return redirect(url_for('minhas_respostas'))
    
    return render_template('resposta/confirmar_exclusao.html', resposta=resposta)

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
    
    compras = db.session.query(Compra, Anuncio, Usuario).join(
        Anuncio, Compra.id_anuncio == Anuncio.id_anuncio
    ).join(
        Usuario, Compra.id_usuario_vendedor == Usuario.id_usuario
    ).filter(
        Compra.id_usuario_comprador == session['usuario_id'],
        Compra.ativo == True
    ).order_by(Compra.data_compra.desc()).all()
    
    return render_template('compra/minhas_compras.html', compras=compras)

@app.route('/vendas')
def minhas_vendas():
    """Histórico de vendas do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    vendas = db.session.query(Compra, Anuncio, Usuario).join(
        Anuncio, Compra.id_anuncio == Anuncio.id_anuncio
    ).join(
        Usuario, Compra.id_usuario_comprador == Usuario.id_usuario
    ).filter(
        Compra.id_usuario_vendedor == session['usuario_id'],
        Compra.ativo == True
    ).order_by(Compra.data_compra.desc()).all()
    
    return render_template('compra/minhas_vendas.html', vendas=vendas)

@app.route('/compra/<int:id>')
def detalhes_compra(id):
    """Detalhes de uma compra específica"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    compra = Compra.query.get_or_404(id)
    
    # Verificar se o usuário tem permissão para ver esta compra
    if compra.id_usuario_comprador != session['usuario_id'] and compra.id_usuario_vendedor != session['usuario_id']:
        flash('Você não tem permissão para ver esta compra!')
        return redirect(url_for('home'))
    
    return render_template('compra/detalhes.html', compra=compra)

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
    observacoes = request.form.get('observacoes', '')
    
    compra.status = novo_status
    compra.observacoes = observacoes
    
    db.session.commit()
    
    flash('Status da compra atualizado com sucesso!')
    return redirect(url_for('minhas_vendas'))

@app.route('/compra/<int:id>/cancelar', methods=['GET', 'POST'])
def cancelar_compra(id):
    """Cancelar uma compra"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    compra = Compra.query.get_or_404(id)
    
    # Verificar se é o comprador ou vendedor
    if compra.id_usuario_comprador != session['usuario_id'] and compra.id_usuario_vendedor != session['usuario_id']:
        flash('Você não tem permissão para cancelar esta compra!')
        return redirect(url_for('home'))
    
    # Verificar se ainda pode cancelar (apenas pendente)
    if compra.status != 'pendente':
        flash('Só é possível cancelar compras com status pendente!')
        return redirect(url_for('detalhes_compra', id=id))
    
    if request.method == 'POST':
        motivo = request.form.get('motivo', '')
        
        # Devolver quantidade ao estoque
        anuncio = Anuncio.query.get(compra.id_anuncio)
        if anuncio and anuncio.ativo:
            anuncio.quantidade_disponivel += compra.quantidade
        
        # Atualizar status da compra
        compra.status = 'cancelada'
        compra.observacoes = f"Cancelada: {motivo}"
        
        db.session.commit()
        
        flash('Compra cancelada com sucesso!')
        
        if compra.id_usuario_comprador == session['usuario_id']:
            return redirect(url_for('minhas_compras'))
        else:
            return redirect(url_for('minhas_vendas'))
    
    return render_template('compra/cancelar.html', compra=compra)

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
    
    favoritos = db.session.query(Favorito, Anuncio, Categoria, Usuario).join(
        Anuncio, Favorito.id_anuncio == Anuncio.id_anuncio
    ).join(
        Categoria, Anuncio.id_categoria == Categoria.id_categoria
    ).join(
        Usuario, Anuncio.id_usuario == Usuario.id_usuario
    ).filter(
        Favorito.id_usuario == session['usuario_id'],
        Anuncio.ativo == True
    ).order_by(Favorito.data_adicao.desc()).all()
    
    return render_template('favorito/meus_favoritos.html', favoritos=favoritos)

@app.route('/favorito/<int:id>/remover', methods=['POST'])
def remover_favorito(id):
    """Remover favorito específico"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    favorito = Favorito.query.get_or_404(id)
    
    # Verificar se é o dono do favorito
    if favorito.id_usuario != session['usuario_id']:
        flash('Você só pode remover seus próprios favoritos!')
        return redirect(url_for('meus_favoritos'))
    
    db.session.delete(favorito)
    db.session.commit()
    
    flash('Favorito removido com sucesso!')
    return redirect(url_for('meus_favoritos'))

# ============== ROTAS DE RELATÓRIOS ==============

@app.route('/relatorio-compras')
def relatorio_compras():
    """Relatório detalhado de compras"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Estatísticas gerais
    total_compras = Compra.query.filter_by(id_usuario_comprador=session['usuario_id'], ativo=True).count()
    valor_total = db.session.query(func.sum(Compra.preco_total)).filter_by(
        id_usuario_comprador=session['usuario_id'], ativo=True
    ).scalar() or 0
    
    # Compras por status
    compras_por_status = db.session.query(
        Compra.status, func.count(Compra.id_compra), func.sum(Compra.preco_total)
    ).filter_by(
        id_usuario_comprador=session['usuario_id'], ativo=True
    ).group_by(Compra.status).all()
    
    # Compras recentes
    compras_recentes = db.session.query(Compra, Anuncio, Usuario).join(
        Anuncio, Compra.id_anuncio == Anuncio.id_anuncio
    ).join(
        Usuario, Compra.id_usuario_vendedor == Usuario.id_usuario
    ).filter(
        Compra.id_usuario_comprador == session['usuario_id'],
        Compra.ativo == True
    ).order_by(Compra.data_compra.desc()).limit(10).all()
    
    return render_template('relatorio/compras.html', 
                         total_compras=total_compras,
                         valor_total=valor_total,
                         compras_por_status=compras_por_status,
                         compras_recentes=compras_recentes)

@app.route('/relatorio-vendas')
def relatorio_vendas():
    """Relatório detalhado de vendas"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Estatísticas gerais
    total_vendas = Compra.query.filter_by(id_usuario_vendedor=session['usuario_id'], ativo=True).count()
    valor_total = db.session.query(func.sum(Compra.preco_total)).filter_by(
        id_usuario_vendedor=session['usuario_id'], ativo=True
    ).scalar() or 0
    
    # Vendas por status
    vendas_por_status = db.session.query(
        Compra.status, func.count(Compra.id_compra), func.sum(Compra.preco_total)
    ).filter_by(
        id_usuario_vendedor=session['usuario_id'], ativo=True
    ).group_by(Compra.status).all()
    
    # Produtos mais vendidos
    produtos_vendidos = db.session.query(
        Anuncio.titulo, func.sum(Compra.quantidade), func.sum(Compra.preco_total)
    ).join(
        Compra, Anuncio.id_anuncio == Compra.id_anuncio
    ).filter(
        Compra.id_usuario_vendedor == session['usuario_id'],
        Compra.ativo == True
    ).group_by(Anuncio.id_anuncio, Anuncio.titulo).order_by(
        func.sum(Compra.quantidade).desc()
    ).limit(5).all()
    
    return render_template('relatorio/vendas.html',
                         total_vendas=total_vendas,
                         valor_total=valor_total,
                         vendas_por_status=vendas_por_status,
                         produtos_vendidos=produtos_vendidos)

# ============== FUNCÕES UTILITÁRIAS ==============

def init_db():
    """Inicializar banco de dados e criar tabelas"""
    with app.app_context():
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

@app.template_filter('status_badge')
def status_badge_filter(status):
    """Filtro para criar badges de status"""
    badges = {
        'pendente': 'warning',
        'confirmada': 'success',
        'cancelada': 'danger',
        'entregue': 'info'
    }
    return badges.get(status, 'secondary')

# ============== CONTEXTO GLOBAL PARA TEMPLATES ==============

@app.context_processor
def utility_processor():
    """Adicionar funções utilitárias aos templates"""
    def get_user_name():
        if 'usuario_id' in session:
            usuario = Usuario.query.get(session['usuario_id'])
            return usuario.nome if usuario else None
        return None
    
    def count_unread_questions():
        if 'usuario_id' in session:
            # Contar perguntas não respondidas nos anúncios do usuário
            count = db.session.query(Pergunta).join(
                Anuncio, Pergunta.id_anuncio == Anuncio.id_anuncio
            ).outerjoin(
                Resposta, Pergunta.id_pergunta == Resposta.id_pergunta
            ).filter(
                Anuncio.id_usuario == session['usuario_id'],
                Pergunta.ativo == True,
                Resposta.id_resposta.is_(None)
            ).count()
            return count
        return 0
    
    return dict(
        len=len,
        enumerate=enumerate,
        datetime=datetime,
        get_user_name=get_user_name,
        count_unread_questions=count_unread_questions
    )

# ============== HANDLERS DE ERRO ==============

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500



# ============== ROTAS DE USUÁRIO ==============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login do usuário"""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        
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

@app.route('/usuario/desativar', methods=['GET', 'POST'])
def desativar_conta():
    """Desativar conta do usuário"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    
    if request.method == 'POST':
        senha_confirmacao = request.form.get('senha_confirmacao')
        
        if check_password_hash(usuario.senha, senha_confirmacao):
            # Desativar usuário (soft delete)
            usuario.ativo = False
            
            # Desativar todos os anúncios do usuário
            Anuncio.query.filter_by(id_usuario=usuario.id_usuario).update({'ativo': False})
            
            db.session.commit()
            
            # Fazer logout
            session.clear()
            flash('Conta desativada com sucesso!')
            return redirect(url_for('home'))
        else:
            flash('Senha incorreta!')
    
    return render_template('usuario/desativar_conta.html', usuario=usuario)

@app.route('/usuarios')
def listar_usuarios():
    """Listar todos os usuários (admin)"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Verificar se é admin (implementação simples)
    usuario_atual = Usuario.query.get(session['usuario_id'])
    if usuario_atual.email != 'admin@ecommerce.com':
        flash('Acesso negado!')
        return redirect(url_for('home'))
    
    usuarios = Usuario.query.order_by(Usuario.data_cadastro.desc()).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

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
        query = query.filter(or_(
            Anuncio.titulo.contains(busca),
            Anuncio.descricao.contains(busca)
        ))
    
    anuncios = query.order_by(Anuncio.data_publicacao.desc()).all()
    categorias = Categoria.query.filter_by(ativo=True).all()
    
    return render_template('anuncio/listar.html', anuncios=anuncios, categorias=categorias, busca=busca)

@app.route('/anuncio/<int:id>')
def detalhes_anuncio(id):
    """Detalhes de um anúncio específico"""
    anuncio = Anuncio.query.get_or_404(id)
    perguntas = Pergunta.query.filter_by(id_anuncio=id, ativo=True).order_by(Pergunta.data_pergunta.desc()).all()
    
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
        anuncio.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        flash('Anúncio atualizado com sucesso!')
        return redirect(url_for('meus_anuncios'))
    
    categorias = Categoria.query.filter_by(ativo=True).all()
    return render_template('anuncio/editar.html', anuncio=anuncio, categorias=categorias)

@app.route('/anuncio/<int:id>/excluir', methods=['GET', 'POST'])
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
    
    if request.method == 'POST':
        anuncio.ativo = False
        db.session.commit()
        
        flash('Anúncio excluído com sucesso!')
        return redirect(url_for('meus_anuncios'))
    
    return render_template('anuncio/confirmar_exclusao.html', anuncio=anuncio)

# ============== ROTAS DE CATEGORIAS ==============

@app.route('/categorias')
def listar_categorias_publico():
    """Listar todas as categorias (público)"""
    categorias = Categoria.query.filter_by(ativo=True).order_by(Categoria.nome).all()
    return render_template('categoria/listar_publico.html', categorias=categorias)

@app.route('/categoria/<int:id>')
def anuncios_categoria(id):
    """Anúncios por categoria"""
    categoria = Categoria.query.get_or_404(id)
    anuncios = Anuncio.query.filter_by(id_categoria=id, ativo=True).order_by(Anuncio.data_publicacao.desc()).all()
    
    return render_template('categoria/categoria.html', categoria=categoria, anuncios=anuncios)

@app.route('/admin/categorias')
def admin_categorias():
    """Gerenciar categorias (admin)"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Verificar se é admin
    usuario_atual = Usuario.query.get(session['usuario_id'])
    if usuario_atual.email != 'admin@ecommerce.com':
        flash('Acesso negado!')
        return redirect(url_for('home'))
    
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template('admin/categorias.html', categorias=categorias)

@app.route('/admin/categoria/nova', methods=['GET', 'POST'])
def nova_categoria():
    """Criar nova categoria"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Verificar se é admin
    usuario_atual = Usuario.query.get(session['usuario_id'])
    if usuario_atual.email != 'admin@ecommerce.com':
        flash('Acesso negado!')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        
        # Verificar se categoria já existe
        categoria_existente = Categoria.query.filter_by(nome=nome).first()
        if categoria_existente:
            flash('Categoria com este nome já existe!')
            return render_template('admin/nova_categoria.html')
        
        nova_categoria = Categoria(
            nome=nome,
            descricao=descricao
        )
        
        db.session.add(nova_categoria)
        db.session.commit()
        
        flash('Categoria criada com sucesso!')
        return redirect(url_for('admin_categorias'))
    
    return render_template('admin/nova_categoria.html')

@app.route('/admin/categoria/<int:id>/editar', methods=['GET', 'POST'])
def editar_categoria(id):
    """Editar categoria existente"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Verificar se é admin
    usuario_atual = Usuario.query.get(session['usuario_id'])
    if usuario_atual.email != 'admin@ecommerce.com':
        flash('Acesso negado!')
        return redirect(url_for('home'))
    
    categoria = Categoria.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        
        # Verificar se outro categoria já usa este nome
        categoria_existente = Categoria.query.filter(
            Categoria.nome == nome,
            Categoria.id_categoria != id
        ).first()
        
        if categoria_existente:
            flash('Categoria com este nome já existe!')
            return render_template('admin/editar_categoria.html', categoria=categoria)
        
        categoria.nome = nome
        categoria.descricao = descricao
        
        db.session.commit()
        
        flash('Categoria atualizada com sucesso!')
        return redirect(url_for('admin_categorias'))
    
    return render_template('admin/editar_categoria.html', categoria=categoria)

@app.route('/admin/categoria/<int:id>/excluir', methods=['GET', 'POST'])
def excluir_categoria(id):
    """Excluir (desativar) categoria"""
    if 'usuario_id' not in session:
        flash('Você precisa estar logado!')
        return redirect(url_for('login'))
    
    # Verificar se é admin
    usuario_atual = Usuario.query.get(session['usuario_id'])
    if usuario_atual.email != 'admin@ecommerce.com':
        flash('Acesso negado!')
        return redirect(url_for('home'))
    
    categoria = Categoria.query.get_or_404(id)
    
    if request.method == 'POST':
        # Verificar se há anúncios ativos nesta categoria
        anuncios_ativos = Anuncio.query.filter_by(id_categoria=id, ativo=True).count()
        
        if anuncios_ativos > 0:
            flash(f'Não é possível excluir a categoria. Existem {anuncios_ativos} anúncios ativos nesta categoria!')
            return redirect(url_for('admin_categorias'))
        
        categoria.ativo = False
        db.session.commit()
        
        flash('Categoria desativada com sucesso!')
        return redirect(url_for('admin_categorias'))
    
    # Contar anúncios na categoria
    total_anuncios = Anuncio.query.filter_by(id_categoria=id).count()
    anuncios_ativos = Anuncio.query.filter_by(id_categoria=id, ativo=True).count()
    
    return render_template('admin/confirmar_exclusao_categoria.html', categoria=categoria, total_anuncios=total_anuncios, anuncios_ativos=anuncios_ativos)


# ============== UTIL ==============
@app.route('/health')
def health():
    return jsonify(status="ok")

# ============== EXECUÇÃO DA APLICAÇÃO ==============
print(f"DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)