# coding=utf-8

from __future__ import absolute_import

from talos.db.dictbase import DictBase
from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class MatchParam(Base, DictBase):
    __tablename__ = 'match_param'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    type = Column(String(36), nullable=False)
    params = Column(String(512), nullable=False)


class Policy(Base, DictBase):
    __tablename__ = 'policy'
    attributes = ['id', 'name', 'description', 'enabled', 'rules']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    enabled = Column(TINYINT(4), nullable=False)
    
    rules = relationship("Rule", secondary="policy_rule", lazy='subquery')


class Rule(Base, DictBase):
    __tablename__ = 'rule'
    attributes = ['id', 'name', 'description', 'level', 'type', 'effect_on', 'match_type', 'match_param_id', 'match_value', 'match_param']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    level = Column(INTEGER(11), nullable=False)
    type = Column(String(36), nullable=False)
    effect_on = Column(String(36), nullable=False)
    match_type = Column(String(36), nullable=False)
    match_param_id = Column(ForeignKey('match_param.id'), nullable=True)
    match_value = Column(String(512), nullable=False)
    
    match_param = relationship('MatchParam', lazy=False)
    # policies = relationship("Policy", back_populates="policy_rule")


class Subject(Base, DictBase):
    __tablename__ = 'subject'
    attributes = ['id', 'name', 'description', 'enabled', 'targets']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    enabled = Column(TINYINT(4), nullable=False)
    
    targets = relationship('Target', secondary='subject_target', lazy='subquery')


class Target(Base, DictBase):
    __tablename__ = 'target'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    args_scope = Column(String(512))
    entity_scope = Column(String(512))
    enabled = Column(TINYINT(4), nullable=False)
    
    # subjects = relationship('SubjectTarget', back_populates='target')


class Box(Base, DictBase):
    __tablename__ = 'box'
    attributes = ['id', 'name', 'description', 'policy_id', 'subject_id', 'policy', 'subject']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    policy_id = Column(ForeignKey('policy.id'), nullable=False, index=True)
    subject_id = Column(ForeignKey('subject.id'), nullable=False, index=True)

    policy = relationship('Policy', lazy=False)
    subject = relationship('Subject', lazy=False)


class PolicyRule(Base, DictBase):
    __tablename__ = 'policy_rule'

    id = Column(INTEGER(11), primary_key=True)
    policy_id = Column(ForeignKey('policy.id'), nullable=False, index=True)
    rule_id = Column(ForeignKey('rule.id'), nullable=False, index=True)

    # policy = relationship('Policy', back_populates='rules')
    # rule = relationship('Rule', back_populates='policies')


class SubjectTarget(Base, DictBase):
    __tablename__ = 'subject_target'

    id = Column(INTEGER(11), primary_key=True)
    subject_id = Column(ForeignKey('subject.id'), nullable=False, index=True)
    target_id = Column(ForeignKey('target.id'), nullable=False, index=True)

    # subject = relationship('Subject', back_populates='targets')
    # target = relationship('Target', back_populates='subjects')