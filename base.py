"""
Base Model for SQLAlchemy ORM

This module provides the declarative base class for all database models.
All models should inherit from this Base class.
"""

from sqlalchemy.orm import declarative_base

# Create declarative base for all models
# All model classes (User, Product, Category, etc.) will inherit from this
Base = declarative_base()

# Metadata is automatically created on Base
# Tables will be created based on model definitions