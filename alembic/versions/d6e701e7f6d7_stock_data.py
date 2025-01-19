"""Stock Data

Revision ID: d6e701e7f6d7
Revises: 
Create Date: 2025-01-19 10:57:35.886572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6e701e7f6d7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    stock_data_table = op.create_table('stock_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('ticker', sa.String(length=10), nullable=True),
    sa.Column('daily_pct_change', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ticker', 'date', name='uq_ticker_date')
    )
    op.create_index(op.f('ix_stock_data_date'), 'stock_data', ['date'], unique=False)
    op.create_index(op.f('ix_stock_data_id'), 'stock_data', ['id'], unique=False)
    op.create_index(op.f('ix_stock_data_ticker'), 'stock_data', ['ticker'], unique=False)
    # ### end Alembic commands ###
    from sqlalchemy.orm import Session
    from db import stock_data_hook
    connection = op.get_bind()
    session = Session(bind=connection)
    stock_data_hook(session, stock_data_table)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stock_data_ticker'), table_name='stock_data')
    op.drop_index(op.f('ix_stock_data_id'), table_name='stock_data')
    op.drop_index(op.f('ix_stock_data_date'), table_name='stock_data')
    op.drop_table('stock_data')
    # ### end Alembic commands ###
