"""multi dataset support

Revision ID: 7a1c9e2f3b4d
Revises: 0f96d778cbde
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a1c9e2f3b4d'
down_revision: Union[str, None] = '0f96d778cbde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'datasets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('fuente_archivo', sa.String(), nullable=False),
        sa.Column('n_registros', sa.Integer(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.execute(
        "INSERT INTO datasets (nombre, fuente_archivo, n_registros) "
        "VALUES ('UAGRM 2017 (original)', 'dataset_2017.csv', 0)"
    )

    op.add_column(
        'registros_academicos',
        sa.Column('dataset_id', sa.Integer(), nullable=False, server_default='1'),
    )
    op.create_index(
        op.f('ix_registros_academicos_dataset_id'), 'registros_academicos', ['dataset_id'], unique=False
    )
    op.create_foreign_key(
        'fk_registros_academicos_dataset_id', 'registros_academicos', 'datasets', ['dataset_id'], ['id']
    )

    op.add_column(
        'modelos_entrenados',
        sa.Column('dataset_id', sa.Integer(), nullable=False, server_default='1'),
    )
    op.create_index(
        op.f('ix_modelos_entrenados_dataset_id'), 'modelos_entrenados', ['dataset_id'], unique=False
    )
    op.create_foreign_key(
        'fk_modelos_entrenados_dataset_id', 'modelos_entrenados', 'datasets', ['dataset_id'], ['id']
    )
    op.drop_constraint('modelos_entrenados_nombre_interno_key', 'modelos_entrenados', type_='unique')
    op.create_unique_constraint(
        'uq_modelo_dataset_nombre', 'modelos_entrenados', ['dataset_id', 'nombre_interno']
    )

    op.execute(
        "UPDATE datasets SET n_registros = "
        "(SELECT COUNT(*) FROM registros_academicos WHERE dataset_id = 1) WHERE id = 1"
    )


def downgrade() -> None:
    op.drop_constraint('uq_modelo_dataset_nombre', 'modelos_entrenados', type_='unique')
    op.create_unique_constraint('modelos_entrenados_nombre_interno_key', 'modelos_entrenados', ['nombre_interno'])
    op.drop_constraint('fk_modelos_entrenados_dataset_id', 'modelos_entrenados', type_='foreignkey')
    op.drop_index(op.f('ix_modelos_entrenados_dataset_id'), table_name='modelos_entrenados')
    op.drop_column('modelos_entrenados', 'dataset_id')

    op.drop_constraint('fk_registros_academicos_dataset_id', 'registros_academicos', type_='foreignkey')
    op.drop_index(op.f('ix_registros_academicos_dataset_id'), table_name='registros_academicos')
    op.drop_column('registros_academicos', 'dataset_id')

    op.drop_table('datasets')
