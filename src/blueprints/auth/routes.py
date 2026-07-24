"""Rotas de autenticação"""

from flask import jsonify, request, render_template
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt,
    set_access_cookies, unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import traceback
from src.blueprints.auth import auth_bp
from src.database import DBConnectionHendler
from src.models import Loja, Usuario

db_handler = DBConnectionHendler()


@auth_bp.route('/login', methods=['POST'])
def login():
    """Faz login e retorna JWT token"""
    session = db_handler.get_session()

    try:
        dados = request.get_json() or {}
        print(dados)
        if not dados.get('email') or not dados.get('senha'):
            return jsonify({'erro': 'Email e senha obrigatórios'}), 400

        usuario = session.query(Usuario).filter_by(
            email=dados['email'].lower()
        ).first()

        if not usuario or not check_password_hash(usuario.senha_hash, dados['senha']):
            return jsonify({'erro': 'Email ou senha inválidos'}), 401

        if not usuario.ativo:
            return jsonify({'erro': 'Usuário inativo'}), 403

        # Atualizar último acesso
        usuario.ultimo_acesso = datetime.utcnow()
        session.commit()

        # Criar token
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                'loja_id': usuario.loja_id,
                'email': usuario.email,
                'nome': usuario.nome,
                'eh_admin': usuario.eh_admin
            }
        )

        resposta = jsonify({
            'mensagem': 'Login realizado com sucesso',
            'token': access_token,
            'usuario': usuario.to_dict()
        })

        set_access_cookies(resposta, access_token)
        return resposta, 200

    except Exception:
        traceback.print_exc()
        raise
    finally:
        db_handler.remove_session()


@auth_bp.route('/registrar', methods=['POST'])
def registrar():
    """Registra nova loja e usuário admin"""
    session = db_handler.get_session()

    try:
        dados = request.get_json() or {}

        # Validações
        if not dados.get('nome_loja'):
            return jsonify({'erro': 'Nome da loja obrigatório'}), 400
        if not dados.get('email'):
            return jsonify({'erro': 'Email obrigatório'}), 400
        if not dados.get('senha') or len(dados['senha']) < 6:
            return jsonify({'erro': 'Senha deve ter pelo menos 6 caracteres'}), 400

        # Verificar se loja já existe
        loja_existe = session.query(Loja).filter_by(
            email=dados['email'].lower()
        ).first()
        if loja_existe:
            return jsonify({'erro': 'Este email já está cadastrado'}), 409

        # Criar loja
        loja = Loja(
            nome=dados['nome_loja'].strip(),
            email=dados['email'].lower().strip(),
            telefone=dados.get('telefone', ''),
            endereco=dados.get('endereco'),
            cnpj=dados.get('cnpj'),
            cor_primaria=dados.get('cor_primaria', '#FF1493'),
            cor_secundaria=dados.get('cor_secundaria', '#0099FF'),
        )

        # Criar usuário admin
        usuario = Usuario(
            loja_id=None,  # Será preenchido após salvar loja
            email=dados['email'].lower().strip(),
            nome=dados.get('nome', 'Admin'),
            senha_hash=generate_password_hash(dados['senha']),
            eh_admin=True,
            ativo=True,
            verificado=False
        )

        session.add(loja)
        session.flush()  # Para pegar o ID gerado

        usuario.loja_id = loja.id
        session.add(usuario)
        session.commit()

        # Criar token de login
        access_token = create_access_token(
            identity=usuario.id,
            additional_claims={
                'loja_id': loja.id,
                'email': usuario.email,
                'nome': usuario.nome,
                'eh_admin': True
            }
        )

        resposta = jsonify({
            'mensagem': 'Loja criada com sucesso',
            'token': access_token,
            'loja': loja.to_dict(),
            'usuario': usuario.to_dict()
        })
        set_access_cookies(resposta, access_token)
        return resposta, 201

    except Exception as e:
        session.rollback()
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Faz logout (invalida o cookie/token no cliente)"""
    resposta = jsonify({'mensagem': 'Logout realizado com sucesso'})
    unset_jwt_cookies(resposta)
    return resposta, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def obter_usuario_atual():
    """Retorna dados do usuário atual"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        usuario = session.query(Usuario).filter_by(id=claims['sub']).first()

        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        return jsonify(usuario.to_dict()), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()


# Páginas HTML
@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Página de login"""
    return render_template('login.html')


@auth_bp.route('/registrar', methods=['GET'])
def registrar_page():
    """Página de registro"""
    return render_template('cadastro.html')
