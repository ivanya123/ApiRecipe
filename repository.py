from shemas import ProdPy
from sql_model.models import as_session, Products


class Repo:

    @classmethod
    async def add_product(cls, prod_py: ProdPy):
        async with as_session() as session:
            prod_dict = prod_py.model_dump()
            product = Products(**prod_dict)
            session.add(product)
            await session.flush()
            await session.commit()
            return product

