from app.database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Numeric, String
from enum import Enum as PyEnum 
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Enum
   

class Empresa(db.Model):
    id          = Column(Integer, primary_key=True)
    cod_interno = Column(Integer, nullable=True)
    cgc         = Column(String(14), unique=True, nullable=False )
    empresa     = Column(String(6), nullable=False)
    nome        = Column(String(100), nullable=False)
    valsaldo    = Column(Boolean, default=False, nullable=False)
    telegran    = Column(String(255), nullable=True)
    ativo       = Column(Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'cod_interno': self.cod_interno,
            'cgc': self.cgc,
            'empresa': self.empresa,
            'nome': self.nome,
            'valsaldo': self.valsaldo,
            'telegran': self.telegran,
            'ativo': self.ativo
        }
    
class Grupo(db.Model):
    id          = Column(Integer, primary_key=True)
    empresa_id  = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    nome        = Column(String(40), unique=True, nullable=False)
    ativo       = Column(Boolean, default=True, nullable=False)
    empresa     = relationship("Empresa")

    def to_dict(self):
        return {
            'id' : self.id,   
            'empresa_id': self.empresa_id,
            'nome' : self.nome,
            'ativo' : self.ativo,
            'empresa':self.empresa
        }
    

class SaldoGrupo(db.Model):
    id          = Column(Integer, primary_key=True)
    grupo_id    = Column(Integer, ForeignKey('grupo.id'), nullable=True)
    quantide    = Column(Numeric(10), nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    grupo       = relationship("Grupo")

    def to_dict(self):
        return {
            'id'    : self.id,      
            'grupo_id'  : self.grupo_id,
            'quantide'  : self.quantide,
            'created_at' : format_datetime_br(self.created_at),
            'updated_at' : format_datetime_br(self.updated_at),
        }

class Parceiro(db.Model):
    id          = Column(Integer, primary_key=True)
    cod_interno = Column(Integer, nullable=True)
    empresa_id  = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    grupo_id    = Column(Integer, ForeignKey('grupo.id'), nullable=True)
    cgc         = Column(String(14), unique=True, nullable=False) 
    nome        = Column(String(100), nullable=False)
    lmt_trava   = Column(Numeric(10, 2), nullable=False)
    lmt_mes     = Column(Numeric(10, 2), nullable=False)
    plano       = Column(Numeric(10, 2), nullable=False)
    ativo       = Column(Boolean, default=True, nullable=False)
    empresa     = relationship("Empresa")

    def to_dict(self):
        return {
            'id': self.id,
            'cod_interno': self.cod_interno ,
            'empresa_id': self.empresa_id,
            'cgc': self.cgc,
            'nome': self.nome,
            'lmt_trava': self.lmt_trava,
            'lmt_mes': self.lmt_mes,
            'plano': self.plano,
            'ativo': self.ativo,
            'empresa': self.empresa     
        }

class Trava(db.Model):
    id              = Column(Integer, primary_key=True)
    empresa_id      = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    produto_id      = Column(String(30), default="OURO")
    parceiro_id     = Column(Integer, ForeignKey('parceiro.id'), nullable=False)
    usuario_id      = Column(Integer, ForeignKey('user.id'), nullable=False)
    quantidade      = Column(Integer, nullable=False)
    preco_unitario  = Column(Numeric(10, 2), nullable=False)
    preco_total     = Column(Numeric(10, 2), nullable=False)
    ativo           = Column(Boolean, default=True, nullable=False)
    status          = Column(String(3), default="A", nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario         = relationship("User")
    empresa         = relationship("Empresa")
    parceiro        = relationship("Parceiro")

    def to_dict(self):
        return {
            'id'            : self.id,
            'empresa_id'    : self.empresa_id,
            'produto_id'    : self.produto_id,
            'parceiro_id'   : self.parceiro_id,
            'usuario_id'    : self.usuario_id,
            'quantidade'    : self.quantidade,
            'preco_unitario': self.preco_unitario,
            'preco_total'   : self.preco_total,
            'ativo'         : self.ativo,
            'status'        : self.status,
            'created_at'    : format_datetime_br(self.created_at),
            'updated_at'    : format_datetime_br(self.updated_at),
            'usuario'       : self.usuario,
            'empresa'       : self.empresa,
            'parceiro'      : self.parceiro      
        }
    
def format_datetime_br(date):
    return date.strftime('%d/%m/%Y %H:%m') if date else ''


class User(db.Model):
    id          = Column(Integer, primary_key=True)
    empresa_id  = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    cod_interno = Column(String(11), nullable=False)
    password    = Column(String(250), nullable=False)
    nome        = Column(String(80), nullable=False)
    email       = Column(String(80), nullable=False)
    telefone    = Column(String(80), nullable=False)
    ativo       = Column(Boolean, default=True, nullable=False)
    interno     = Column(Boolean, default=True, nullable=False)
    empresa     = relationship("Empresa")
    
    def to_dict(self):
        return {
            'id'         : self.id,     
            'empresa_id' : self.empresa_id,
            'cod_interno': self.cod_interno,
            'password'   : self.password,
            'nome'       : self.nome,
            'email'      : self.email,
            'telefone'   : self.telefone,
            'ativo'      : self.ativo,
            'interno'    : self.interno
        }

class Acessos(db.Model):
    id          = Column(Integer, primary_key=True)
    usuario_id  = Column(Integer, ForeignKey('user.id'), nullable=False)
    empresa_id  = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    parceiro_id = Column(Integer, ForeignKey('parceiro.id'), nullable=False)
    ativo       = Column(Boolean, default=True, nullable=False)
    usuario     = relationship("User")
    empresa     = relationship("Empresa")
    parceiro    = relationship("Parceiro")

    def to_dict(self):
        return {
            'id'          : self.id         ,
            'usuario_id'  : self.usuario_id ,
            'empresa_id'  : self.empresa_id ,
            'parceiro_id' : self.parceiro_id,
            'ativo'       : self.ativo      ,
            'usuario'     : self.usuario    ,
            'empresa'     : self.empresa    ,
            'parceiro'    : self.parceiro   
        }
    
class Roles(db.Model):
    id              = Column(Integer, primary_key=True)
    usuario_id      = Column(Integer, ForeignKey('user.id'), nullable=False)
    cad_empresa     = Column(Boolean, default=True, nullable=False)
    cad_parceiro    = Column(Boolean, default=True, nullable=False)
    cad_usuario     = Column(Boolean, default=True, nullable=False)
    cad_contacao    = Column(Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id'           : self.id,
            'usuario_id'   : self.usuario_id,
            'cad_empresa'  : self.cad_empresa,
            'cad_usuario'  : self.cad_usuario,
            'cad_contacao' : self.cad_contacao    
        }
    

class Firebase(db.Model):
    id          = Column(Integer, primary_key=True)
    empresa_id  = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    usuario_id  = Column(Integer, ForeignKey('user.id'), nullable=False)
    token       = Column(String(255), nullable=True)
    interno     = Column(Boolean, default=False, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa     = relationship("Empresa")
    usuario     = relationship("User")

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_id': self.empresa_id,
            'usuario_id': self.usuario_id,
            'token': self.token,
            'interno': self.interno,
            'created_at': format_datetime_br(self.created_at),
            'updated_at': format_datetime_br(self.updated_at),
        }